/// <reference path="typings/jquery/jquery.d.ts" />
/// <reference path="typings/socket.io/socket.io.d.ts" />
/// <reference path="typings/sockjs/sockjs.d.ts" />
/// <reference path="typings/node/node.d.ts" />


$(document).ready(function () {

    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var sock = new SockJS('http://' + document.domain);
    sock.onopen = function () {
        console.log('open');
    };
    sock.onmessage = function (e) {
        console.log('message', e.data);
    };
    sock.onclose = function () {
        console.log('close');
    };

    sock.send('test');
    socket.on('echo_game_list', function (data) {
        var list = [];
        $.each(data.id, function (j, i) {
            list.push('<li id=' + i + '>' + i + '</li>');
        });
        $('#gamelist').html(list.join(""));
    });
    socket.on('echo_ng', function (data) {
        $('#response').html('<p>' + data.uid + '</p>');
    });
    socket.emit('game_list', {});
    $("#refresh").click(function send() {
        socket.emit('game_list', {});
    });
    $("#ng").click(function send() {
        socket.emit('new_game', {});
    });

});

