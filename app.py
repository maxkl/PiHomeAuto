import sys
from os import path

from bottle import run, get, put, json_dumps, response, request, install, abort, default_app, static_file, delete
from bottle_sqlite import SQLitePlugin

from db_util import create_tables

dbfile = 'test.db'
static_dir = path.join(path.dirname(path.abspath(__file__)), 'static')

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
    if not request.json:
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
    if not request.json:
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
def get_device(db, device_id):
    # TODO
    return ret_json({'state': False})


@put('/devices/<device_id:int>/state')
def get_device(db, device_id):
    # TODO
    return ret_json({})


@get('/devices/<device_id:int>/schedule')
def get_device(db, device_id):
    # TODO
    return ret_json({'schedule': []})


@put('/devices/<device_id:int>/schedule')
def get_device(db, device_id):
    # TODO
    return ret_json({})

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)
