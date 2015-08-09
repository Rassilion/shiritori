/// <reference path="typings/tsd.d.ts" />
$(function () {
    var conn = null;
    var user = 1;

    function log(msg) {
        var control = $('#log');
        control.html(control.html() + msg + '<br/>');
        control.scrollTop(control.scrollTop() + 1000);
    }

    function connect() {
        disconnect();
        var transports = $('#protocols input:checked').map(function () {
            return $(this).attr('id');
        }).get();
        conn = new SockJS('http://' + window.location.host + '/game1', transports);
        log('Connecting...');
        conn.onopen = function () {
            conn.send(JSON.stringify({user: user}));
            log('Connected.');
            update_ui();
        };
        conn.onmessage = function (e) {
            log('Received: ' + e.data);
        };
        conn.onclose = function () {
            log('Disconnected.');
            conn = null;
            update_ui();
        };
    }

    function disconnect() {
        if (conn != null) {
            log('Disconnecting...');
            conn.close();
            conn = null;
            update_ui();
        }
    }

    function update_ui() {
        var msg = '';
        if (conn == null || conn.readyState != SockJS.OPEN) {
            $('#status').text('disconnected');
            $('#connect').text('Connect');
        } else {
            $('#status').text('connected (' + conn.protocol + ')');
            $('#connect').text('Disconnect');
        }
    }

    $('#connect').click(function () {
        if (conn == null) {
            connect();
        } else {
            disconnect();
        }
        update_ui();
        return false;
    });
    $('#connect2').click(function () {
        if (conn == null) {
            connect();
            user = 2;
        } else {
            disconnect();
        }
        update_ui();
        return false;
    });
    $('form').submit(function () {
        var text = $('#text').val();
        log('Sending: ' + text);

        conn.send(text);
        $('#text').val('').focus();
        return false;
    });
});
/*$(document).ready(function () {

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

 });*/

