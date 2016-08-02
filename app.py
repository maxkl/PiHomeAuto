import subprocess
import sys
import threading
from os import path

from bottle import run, get, put, json_dumps, response, request, install, abort, default_app, static_file, delete
from bottle_sqlite import SQLitePlugin

from db_util import create_tables
from rcswitch import RCSwitch

pin = 4
dbfile = 'test.db'
static_dir = path.join(path.dirname(path.abspath(__file__)), 'static')

ret = subprocess.call('gpio export ' + str(pin) + ' out', shell=True, stderr=subprocess.STDOUT)
if ret != 0:
    print('GPIO export failed', file=sys.stderr)
    exit(-1)

switch_lock = threading.Lock()

RCSwitch.setup()
switch = RCSwitch()
switch.enable_transmit(pin)


def switch_on(group, device):
    with switch_lock:
        for _ in range(4):
            switch.switch_on(group, device)


def switch_off(group, device):
    with switch_lock:
        for _ in range(4):
            switch.switch_off(group, device)


def switch_set(group, device, on):
    switch_on(group, device) if on else switch_off(group, device)

create_tables(dbfile)

install(SQLitePlugin(dbfile=dbfile))


class CatchAllErrorHandler:
    def __init__(self, handler):
        self.handler = handler

    def get(self, status, default_handler=None):
        return self.handler


default_app().error_handler = CatchAllErrorHandler(lambda err: print(err, file=sys.stderr))


def ret_json(data, *args, **kwargs):
    response.content_type = 'application/json; charset=utf-8'
    return json_dumps(data, *args, **kwargs)


@get('/static/<file:path>')
def get_static(file):
    return static_file(file, root=static_dir)


@get('/devices/')
def get_devices(db):
    devices = []
    for device in db.execute('SELECT id, name, group_code, device_code FROM devices'):
        devices.append(dict(device))
    return ret_json({'devices': devices})


@put('/devices/')
def put_devices(db):
    if request.json is None:
        abort(400, 'Not JSON')
    data = request.json
    if 'name' not in data or 'group_code' not in data or 'device_code' not in data:
        abort(400, 'Need, name, group_code and device_code')
    result = db.execute('INSERT INTO devices (name, group_code, device_code) VALUES (?, ?, ?)', (data['name'], data['group_code'], data['device_code']))
    return ret_json({
        'id': result.lastrowid
    })


@get('/devices/<device_id:int>')
def get_device(db, device_id):
    row = db.execute('SELECT id, name, group_code, device_code FROM devices WHERE id = ?', (device_id,)).fetchone()
    if not row:
        abort(404, 'Device not found')
    device = dict(row)
    return ret_json({'device': device})


@put('/devices/<device_id:int>')
def put_device(db, device_id):
    if request.json is None:
        abort(400, 'Not JSON')
    data = request.json
    if 'name' not in data or 'group_code' not in data or 'device_code' not in data:
        abort(400, 'Need, name, group_code and device_code')
    result = db.execute('UPDATE devices SET name = ?, group_code = ?, device_code = ? WHERE id = ?', (data['name'], data['group_code'], data['device_code'], device_id))
    if result.rowcount == 0:
        abort(404, 'Device not found')
    return ret_json({})


@delete('/devices/<device_id:int>')
def put_device(db, device_id):
    result = db.execute('DELETE FROM devices WHERE id = ?', (device_id,))
    if result.rowcount == 0:
        abort(404, 'Device not found')
    return ret_json({})


@get('/devices/<device_id:int>/state')
def get_device_state(db, device_id):
    # TODO
    return ret_json({'state': False})


@put('/devices/<device_id:int>/state')
def put_device_state(db, device_id):
    # TODO
    if request.json is None:
        abort(400, 'Not JSON')
    new_state = request.json
    row = db.execute('SELECT group_code, device_code FROM devices WHERE id = ?', (device_id,)).fetchone()
    if not row:
        abort(404, 'Device not found')
    switch_set(row['group_code'], row['device_code'], new_state)
    return ret_json({})


@get('/devices/<device_id:int>/schedule')
def get_device_schedule(db, device_id):
    # TODO
    return ret_json({'schedule': []})


@put('/devices/<device_id:int>/schedule')
def put_device_schedule(db, device_id):
    # TODO
    return ret_json({})

if __name__ == '__main__':
    run(host='0.0.0.0', port=8080, debug=True, reloader=True)
