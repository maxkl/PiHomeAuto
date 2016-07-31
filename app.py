import sys
import subprocess
import threading
import re
from flask import Flask, jsonify, render_template, abort
from rcswitch import rcswitch

pin = 4

ret = subprocess.call('gpio export ' + str(pin) + ' out', shell=True, stderr=subprocess.STDOUT)
if ret != 0:
    print('GPIO export failed', file=sys.stderr)
    exit(-1)

switch_lock = threading.Lock()

rcswitch.setup()
switch = rcswitch.RCSwitch()
switch.enable_transmit(pin)


def switch_on(group, device):
    with switch_lock:
        for _ in range(4):
            switch.switch_on(group, device)


def switch_off(group, device):
    with switch_lock:
        for _ in range(4):
            switch.switch_off(group, device)

app = Flask(__name__)


@app.route('/')
def route_index():
    return render_template('home.html')

rident = re.compile(r'^[01]{5}$')
r_device_code = re.compile(r'^([01]{5})([01]{5})$')


@app.route('/api/<group>/<device>/<cmd>')
def route_switch_on(group, device, cmd):
    if not rident.match(group) or not rident.match(device):
        return jsonify(success=False, error='Invalid group or device')
    if cmd == 'on':
        switch_on(group, device)
        return jsonify(success=True)
    elif cmd == 'off':
        switch_off(group, device)
        return jsonify(success=True)
    return jsonify(success=False, error='Unknown command \'' + cmd + '\'')


@app.route('/api/device/<code>/state', methods=['GET', 'PUT'])
def route_device_state(code):
    m = r_device_code.match(code)
    if m is None:
        abort(400)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
