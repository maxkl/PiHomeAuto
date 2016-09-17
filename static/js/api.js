
(function (window, document) {
    'use strict';

    function callApi(verb, endpoint, data, cb) {
        if (typeof cb === 'undefined') {
            cb = data;
            data = undefined;
        }

        var req = new XMLHttpRequest();

        req.addEventListener('load', function () {
            if (req.status == 200) {
                try {
                    var data = JSON.parse(req.responseText);

                    if (typeof data === 'object') {
                        cb(null, data);
                    } else {
                        cb(new TypeError('Server did not respond with a JSON object'));
                    }
                } catch (e) {
                    cb(new SyntaxError('Server did not respond with valid JSON (' + e.message + ')'));
                }
            } else {
                cb(new Error('Server error: ' + req.status + ' (' + req.statusText + ')'));
            }
        });

        req.addEventListener('error', function () {
            cb(new Error('Network/client error'));
        });

        req.open(verb, '/api/' + endpoint);

        req.setRequestHeader('Content-Type', 'application/json; charset=utf-8');

        if (typeof data !== 'undefined') {
            req.send(JSON.stringify(data));
        } else {
            req.send();
        }
    }

    function getDevices(cb) {
        callApi('get', 'devices/', cb);
    }

    function createDevice(name, groupCode, deviceCode, cb) {
        callApi('put', 'devices/', {
            name: name,
            group_code: groupCode,
            device_code: deviceCode
        }, cb);
    }

    function getDevice(id, cb) {
        callApi('get', 'devices/' + id, cb);
    }

    function updateDevice(id, name, groupCode, deviceCode, cb) {
        callApi('put', 'devices/' + id, {
            name: name,
            group_code: groupCode,
            device_code: deviceCode
        }, cb);
    }

    function deleteDevice(id, cb) {
        callApi('delete', 'devices/' + id, cb);
    }

    function getDeviceState(id, cb) {
        callApi('get', 'devices/' + id + '/state', cb);
    }

    function setDeviceState(id, state, cb) {
        callApi('put', 'devices/' + id + '/state', state, cb);
    }

    function getDeviceSchedule(id, cb) {
        callApi('get', 'devices/' + id + '/schedule', cb);
    }

    function setDeviceSchedule(id, schedule, cb) {
        callApi('put', 'devices/' + id + '/schedule', schedule, cb);
    }

    window.API = {
        call: callApi,
        getDevices: getDevices,
        createDevice: createDevice,
        getDevice: getDevice,
        updateDevice: updateDevice,
        deleteDevice: deleteDevice,
        getDeviceState: getDeviceState,
        setDeviceState: setDeviceState,
        getDeviceSchedule: getDeviceSchedule,
        setDeviceSchedule: setDeviceSchedule
    };

})(window, document);
