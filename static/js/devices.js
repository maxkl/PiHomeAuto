
// FIXME: $modal.modal('handleUpdate') after updating modal content

var $deviceList = $('#device-list');
var $deviceListBody = $deviceList.find('tbody');
var $loadingOverlay = $('#loading');

var rCode = /^[01]{5}$/;

var devices = {};

function Device(id, name, groupCode, deviceCode) {
    this.id = id;
    this.name = name;
    this.groupCode = groupCode;
    this.deviceCode = deviceCode;

    this.hasDom = false;
    this.$el = null;
    this.$name = null;
    this.$groupCode = null;
    this.$deviceCode = null;
    this.$onOffButtons = null;
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
    var $onOffButtons = $('<button>', { type: 'button', class: 'btn btn-success'}).text('An').add($('<button>', { type: 'button', class: 'btn btn-primary'}).text('Auto')).add($('<button>', { type: 'button', class: 'btn btn-danger'}).text('Aus'));

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
            $('<button>', { class: 'btn btn-default' }).text('Zeitplan bearbeiten').click(editSchedule)
        )
    );

    this.$el = $el;
    this.$name = $name;
    this.$groupCode = $group;
    this.$deviceCode = $device;
    this.$onOffButtons = $onOffButtons;

    this.hasDom = true;

    $el.appendTo($deviceListBody);
};

Device.prototype.removeDom = function () {
    if(this.hasDom) {
        $deviceListBody.removeChild(this.$el);
        this.$el = null;
        this.$name = null;
        this.$groupCode = null;
        this.$deviceCode = null;
        this.$onOffButtons = null;
        this.hasDom = false;
    }
};

function addDevice(id, name, group, device) {
    var dev = new Device(id, name, group, device);

    devices[id] = dev;

    dev.buildDom();
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
            doApiRequest(API.createDevice, name, group, device, function (err, data) {
                if(err) {
                    console.error(err);
                    return;
                }

                addDevice(data.id, name, group, device);
            });
        } else {
            doApiRequest(API.updateDevice, editTarget, name, group, device, function (err, data) {
                if(err) {
                    console.error(err);
                    return;
                }

                editDevice(editTarget, name, group, device);
            });
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

var apiRequestQueue = [];
var apiRequestRunning = false;

function _nextApiRequest() {
    var req = apiRequestQueue.shift();
    apiRequestRunning = true;
    req.method.apply(null, req.args.concat(function (err, data) {
        if(apiRequestQueue.length > 0) {
            _nextApiRequest();
        } else {
            apiRequestRunning = false;
            $loadingOverlay.removeClass('visible');
        }

        req.cb(err, data);
    }));
}

function nextApiRequest() {
    if(apiRequestRunning) return;
    if(apiRequestQueue.length == 0) return;

    $loadingOverlay.addClass('visible');

    _nextApiRequest();
}

function doApiRequest(method) {
    var args = Array.prototype.slice.call(arguments, 1, arguments.length - 1);
    var cb = arguments[arguments.length - 1];
    apiRequestQueue.push({
        method: method,
        args: args,
        cb: cb
    });
    nextApiRequest();
}

doApiRequest(API.getDevices, function (err, res) {
    if(err) {
        console.error(err);
        return;
    }

    var devices = res['devices'];
    devices.forEach(function (device) {
       addDevice(device['id'], device['name'], device['group_code'], device['device_code']);
    });
});
