
// FIXME: $modal.modal('handleUpdate') after updating modal content

var $deviceList = $('#device-list');
var $deviceListBody = $deviceList.find('tbody');

var rCode = /^[01]{5}$/;
var BASE_36_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789';
var ALPHANUMERIC_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

function randomString(len, chars) {
    chars = chars || ALPHANUMERIC_CHARS;
    var charCount = chars.length;

    var str = '';
    while(len--) {
        str += chars[Math.floor(Math.random() * charCount)];
    }

    return str;
}

function callApi(verb, endpoint, data, cb) {
    if(typeof cb === 'undefined') {
        cb = data;
        data = null;
    }

    var req = new XMLHttpRequest();

    req.addEventListener('load', function () {
       if(req.status == 200) {
           try {
               var data = JSON.parse(req.responseText);

               if(typeof data === 'object') {
                   cb(null, data);
               } else {
                   cb(new TypeError('Server did not respond with a JSON object'));
               }
           } catch (e) {
               cb(new SyntaxError('Server did not respond with valid JSON'));
           }
       } else {
           cb(new Error('Server error: ' + req.status + ' (' + req.statusText + ')'));
       }
    });

    req.addEventListener('error', function () {
        cb(new Error('Network/client error'));
    });

    req.open(verb, 'http://localhost:8000/' + endpoint);

    req.setRequestHeader('Content-Type', 'application/json; charset=utf-8');

    req.send(JSON.stringify(data));
}

var devices = {};

function Device(id, name, groupCode, deviceCode, auto) {
    this.id = id;
    this.name = name;
    this.groupCode = groupCode;
    this.deviceCode = deviceCode;
    this.auto = auto;

    this.hasDom = false;
    this.$el = null;
    this.$name = null;
    this.$groupCode = null;
    this.$deviceCode = null;
    this.$onOffButtons = null;
    this.$auto = null;
}

Device.prototype.setName = function (name) {
    this.name = name;

    if(this.hasDom) {
        this.$name.text(name);
    }
};

Device.prototype.setGroupCode = function (groupCode) {
    this.groupCode = groupCode;

    if(this.hasDom) {
        this.$groupCode.text(groupCode);
    }
};

Device.prototype.setDeviceCode = function (deviceCode) {
    this.deviceCode = deviceCode;

    if(this.hasDom) {
        this.$deviceCode.text(deviceCode);
    }
};

Device.prototype.setAuto = function (auto) {
    this.auto = auto;

    if(this.hasDom) {
        this.$auto.prop('checked', auto);
    }
};

Device.prototype.buildDom = function () {
    var self = this;

    function editSchedule() {
        openScheduleModal(self.id, self.name);
    }

    function editProps() {
        openDevicePropsModal(self.id, self.name, self.groupCode, self.deviceCode);
    }

    var $name = $('<td>').text(this.name);
    var $group = $('<span>').text(this.groupCode);
    var $device = $('<span>').text(this.deviceCode);
    var $onOffButtons = $('<button>', { type: 'button', class: 'btn btn-success'}).text('An').add($('<button>', { type: 'button', class: 'btn btn-danger'}).text('Aus'));
    var $auto = $('<input>', { type: 'checkbox' }).prop('checked', this.auto);

    var $el = $('<tr>').append(
        $('<td>').append(
            $('<button>', { class: 'btn btn-link' }).append(
                $('<span>', { class: 'glyphicon glyphicon-edit' })
            ).click(editProps)
        ),
        $name,
        $('<td>').append(
            $group,
            '<br />',
            $device
        ),
        $('<td>').append(
            $('<div>', { class: 'btn-group' }).append($onOffButtons)
        ),
        $('<td>').append(
            $('<div>', { class: 'checkbox' }).append(
                $('<label>').append(
                    $auto,
                    ' Auto'
                )
            )
        ),
        $('<td>').append(
            $('<button>', { class: 'btn btn-default' }).text('Zeitplan bearbeiten').click(editSchedule)
        ),
        $('<td>').append(
            $('<button>', { class: 'btn btn-default' }).text('Setzen')
        )
    );

    this.$el = $el;
    this.$name = $name;
    this.$groupCode = $group;
    this.$deviceCode = $device;
    this.$onOffButtons = $onOffButtons;
    this.$auto = $auto;

    this.hasDom = true;

    $el.appendTo($deviceListBody);
};

function addDevice(id, name, group, device, auto) {
    var dev = new Device(id, name, group, device, auto);

    devices[id] = dev;

    dev.buildDom();

    // function editSchedule() {
    //     openScheduleModal(id, name);
    // }
    //
    // function editProps() {
    //     openDevicePropsModal(id, name, group, device);
    // }
    //
    // var $name = $('<td>').text(name);
    // var $group = $('<span>').text(group);
    // var $device = $('<span>').text(device);
    //
    // var $tr = $('<tr>').append(
    //     $('<td>').append(
    //         $('<button>', { class: 'btn btn-link' }).append(
    //             $('<span>', { class: 'glyphicon glyphicon-edit' })
    //         ).click(editProps)
    //     ),
    //     $name,
    //     $('<td>').append(
    //         $group,
    //         '<br />',
    //         $device
    //     ),
    //     $('<td>').append(
    //         $('<div>', { class: 'btn-group' }).append(
    //             $('<button>', { type: 'button', class: 'btn btn-success'}).text('An'),
    //             $('<button>', { type: 'button', class: 'btn btn-danger'}).text('Aus')
    //         )
    //     ),
    //     $('<td>').append(
    //         $('<div>', { class: 'checkbox' }).append(
    //             $('<label>').append(
    //                 $('<input>', { type: 'checkbox' }).prop('checked', auto),
    //                 ' Auto'
    //             )
    //         )
    //     ),
    //     $('<td>').append(
    //         $('<button>', { class: 'btn btn-default' }).text('Zeitplan bearbeiten').click(editSchedule)
    //     ),
    //     $('<td>').append(
    //         $('<button>', { class: 'btn btn-default' }).text('Setzen')
    //     )
    // );
    //
    // $tr.appendTo($deviceListBody);
    //
    // devices[id] = {
    //     $el: $tr,
    //     $name: $name,
    //     $group: $group,
    //     $device: $device
    // };
}

function editDevice(id, name, group, device) {
    if(devices.hasOwnProperty(id)) {
        var dev = devices[id];

        dev.setName(name);
        dev.setGroupCode(group);
        dev.setDeviceCode(device);
    }
}

var $devicePropsModal = $('#device-props-modal');
var $deviceName = $devicePropsModal.find('#new-device-name');
var $deviceGroupCode = $devicePropsModal.find('#new-device-group-code');
var $deviceCode = $devicePropsModal.find('#new-device-code');

var propsModalNew;
var editTarget;

function openNewDeviceModal() {
    $deviceName.val('');
    $deviceGroupCode.val('');
    $deviceCode.val('');

    propsModalNew = true;

    $devicePropsModal.modal('show');
}

function openDevicePropsModal(id, name, group, device) {
    editTarget = id;

    $deviceName.val(name);
    $deviceGroupCode.val(group);
    $deviceCode.val(device);

    propsModalNew = false;

    $devicePropsModal.modal('show');
}

$('#new-device').click(openNewDeviceModal);

$devicePropsModal.on('shown.bs.modal', function () {
    $deviceName.focus();
});

$('#device-props-form').submit(function (evt) {
    evt.preventDefault();
    var name = $deviceName.val().trim();
    var group = $deviceGroupCode.val().trim();
    var device = $deviceCode.val().trim();

    if(name && rCode.test(group) && rCode.test(device)) {
        if(propsModalNew) {
            var id = randomString(32, ALPHANUMERIC_CHARS);
            addDevice(id, name, group, device, false);
        } else {
            editDevice(editTarget, name, group, device);
        }

        $devicePropsModal.modal('hide');
    }
});

var $scheduleModal = $('#schedule-modal');

var scheduleId;

function openScheduleModal(id, name) {
    scheduleId = id;
    $scheduleModal.find('.schedule-name').text(name);
    $scheduleModal.modal('show');
}

$('#save-schedule').click(function () {
    $scheduleModal.modal('hide');
});

callApi('put', 'devices/', {
    name: 'Küche',
    group_code: '10100',
    device_code: '10000'
}, function (err, res) {
    if(err) {
        console.error(err);
        return;
    }

    console.log(res);
});
