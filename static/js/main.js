
function callApi(path, cb) {
    var req = new XMLHttpRequest();
    
    req.addEventListener('load', function () {
        if(req.status == 200) {
            try {
                cb(null, JSON.parse(req.responseText));
            } catch(err) {
                cb(err);
            }
        } else {
            cb(new Error('Server error: ' + req.status));
        }
    });
    
    req.addEventListener('error', function () {
        cb(new Error('Client/network error'));
    });
    
    req.open('GET', '/api/' + path);
    req.send();
}

function setSwitch(group, device, state) {
    $buttons.prop('disabled', true);

    $loading.show();
    $error.hide();

    callApi(group + '/' + device + '/' + (state ? 'on' : 'off'), function (err, data) {
        $loading.hide();
        $buttons.prop('disabled', false);

        if(err) {
            console.error(err);
            $error.show();
            return;
        }

        if(!data.success) {
            console.error(new Error(data.error || 'Unknown'));
            $error.show();
            return;
        }
    })
}

var $buttons = $('#buttons *');
var $group = $('#input-group');
var $device = $('#input-device');
var $loading = $('#loading');
var $error = $('#error');

$('#btn-on').click(function () {
    setSwitch($group.val(), $device.val(), true);
});

$('#btn-off').click(function () {
    setSwitch($group.val(), $device.val(), false);
});
