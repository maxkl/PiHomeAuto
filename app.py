import functools
import json
import subprocess
import sys
import threading

import sqlite3
from bottle import json_dumps, response, request, abort, Bottle
from bottle_sqlite import SQLitePlugin

from db_util import create_tables
from rcswitch import RCSwitch
from scheduler.scheduler import Scheduler

pin = 4
dbfile = 'pihomeauto.db'

exitcode = subprocess.call('gpio export ' + str(pin) + ' out', shell=True, stderr=subprocess.STDOUT)
if exitcode != 0:
    print('GPIO export failed', file=sys.stderr)
    exit(-1)

switch_lock = threading.Lock()

RCSwitch.setup()
switch = RCSwitch()
switch.set_pulse_length(300)
switch.set_repeat_transmit(40)
switch.enable_transmit(pin)


def switch_on(group, device):
    with switch_lock:
        switch.switch_on(group, device)


def switch_off(group, device):
    with switch_lock:
        switch.switch_off(group, device)


def switch_set(group, device, on):
    switch_on(group, device) if on else switch_off(group, device)


create_tables(dbfile)

app = Bottle()

app.install(SQLitePlugin(dbfile=dbfile))


class CatchAllErrorHandler:
    def __init__(self, handler):
        self.handler = handler

    def get(self, status, default_handler=None):
        return self.handler


app.error_handler = CatchAllErrorHandler(lambda err: print(err, file=sys.stderr))


def ret_json(data, *args, **kwargs):
    response.content_type = 'application/json; charset=utf-8'
    return json_dumps(data, *args, **kwargs)


@app.get('/devices/')
def get_devices(db):
    devices = []
    for device in db.execute('SELECT id, name, group_code, device_code FROM devices'):
        devices.append(dict(device))
    return ret_json({'devices': devices})


@app.put('/devices/')
def put_devices(db):
    if request.json is None:
        abort(400, 'Not JSON')
    data = request.json
    if 'name' not in data or 'group_code' not in data or 'device_code' not in data:
        abort(400, 'Need, name, group_code and device_code')
    result = db.execute('INSERT INTO devices (name, group_code, device_code) VALUES (?, ?, ?)',
                        (data['name'], data['group_code'], data['device_code']))
    return ret_json({
        'id': result.lastrowid
    })


@app.get('/devices/<device_id:int>')
def get_device(db, device_id):
    row = db.execute('SELECT id, name, group_code, device_code FROM devices WHERE id = ?', (device_id,)).fetchone()
    if not row:
        abort(404, 'Device not found')
    device = dict(row)
    return ret_json({'device': device})


@app.put('/devices/<device_id:int>')
def put_device(db, device_id):
    if request.json is None:
        abort(400, 'Not JSON')
    data = request.json
    if 'name' not in data or 'group_code' not in data or 'device_code' not in data:
        abort(400, 'Need, name, group_code and device_code')
    result = db.execute('UPDATE devices SET name = ?, group_code = ?, device_code = ? WHERE id = ?',
                        (data['name'], data['group_code'], data['device_code'], device_id))
    if result.rowcount == 0:
        abort(404, 'Device not found')
    return ret_json({})


@app.delete('/devices/<device_id:int>')
def delete_device(db, device_id):
    result = db.execute('DELETE FROM devices WHERE id = ?', (device_id,))
    if result.rowcount == 0:
        abort(404, 'Device not found')
    return ret_json({})


@app.get('/devices/<device_id:int>/state')
def get_device_state(db, device_id):
    # TODO
    return ret_json({'state': False})


@app.put('/devices/<device_id:int>/state')
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


@app.get('/devices/<device_id:int>/schedule')
def get_device_schedule(db, device_id):
    row = db.execute('SELECT schedule FROM devices WHERE id = ?', (device_id,)).fetchone()
    if not row:
        abort(404, 'Device not found')
    schedule_str = row['schedule']
    if schedule_str is None:
        schedule = []
    else:
        schedule = json.loads(schedule_str)
    return ret_json({
        'schedule': schedule
    })


def normalize_schedule(sched):
    if not isinstance(sched, list):
        raise TypeError('Schedule is not a list')
    new_sched = []
    for task in sched:
        if not isinstance(task, dict):
            raise TypeError('Task is not a dict')
        if 'state' not in task or 'time' not in task:
            raise AttributeError('Task is missing state and/or time')
        state = task['state']
        if not isinstance(state, bool):
            raise TypeError('State is not a bool')
        time = task['time']
        if not isinstance(time, int):
            raise TypeError('Time is not an int')
        new_sched.append({
            'state': state,
            'time': time
        })
    return new_sched


@app.put('/devices/<device_id:int>/schedule')
def put_device_schedule(db, device_id):
    if request.json is None:
        abort(400, 'Not JSON')
    schedule = None
    try:
        schedule = normalize_schedule(request.json)
    except (TypeError, AttributeError) as e:
        abort(400, str(e))
    schedule_str = json.dumps(schedule)
    result = db.execute('UPDATE devices SET schedule = ? WHERE id = ?', (schedule_str, device_id))
    if result.rowcount == 0:
        abort(404, 'Device not found')
    return ret_json({})


def use_db(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db = sqlite3.connect(dbfile)
        db.row_factory = sqlite3.Row

        kwargs['db'] = db

        try:
            ret = func(*args, **kwargs)
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            raise
        finally:
            db.close()
        return ret
    return wrapper


@use_db
def query_tasks(t, db):
    rows = db.execute('SELECT group_code, device_code, schedule FROM devices').fetchall()
    results = []
    for row in rows:
        group_code = row['group_code']
        device_code = row['device_code']
        schedule_str = row['schedule']
        if schedule_str is None:
            continue
        schedule = json.loads(schedule_str)
        for task in schedule:
            if task['time'] == t:
                results.append((
                    group_code,
                    device_code,
                    task['state']
                ))
    return results


def exec_task(task):
    switch_set(task[0], task[1], task[2])


Scheduler(query_tasks, exec_task).start()
