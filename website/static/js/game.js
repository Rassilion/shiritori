/// <reference path="typings/tsd.d.ts" />
$(function main() {
    // url paramater parser
    var qs = (function (a) {
        if (a == "")
            return {};
        var b = {};
        for (var i = 0; i < a.length; ++i) {
            var p = a[i].split('=', 2);
            if (p.length == 1)
                b[p[0]] = "";
            else
                b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    })(window.location.search.substr(1).split('&'));
    //get token from cookie
    var token = Cookies.get("remember_token");
    // get roomid from url
    var roomid = qs["id"];
    // if roomid not given show lobby
    if (roomid === undefined) {
        roomid = 'lobby';
        $('#game').addClass('collapse');
    }
    else {
        $('#lobby').addClass('collapse');
    }
    var user;
    //socket
    var sckt = GameRoom(roomid, token);
    var game_status = {};
    var letter;
    /**
     * Create a new socket instance between client and server,
     * and start use it
     */
    function GameRoom(roomId, token) {
        var sckt = new socket('game1', true);
        // On every connect, the server 'loose' us
        // so we have to join again
        if (roomId === 'lobby') {
            sckt.on('connect', function () {
                this.emit('auth', {
                    token: token
                });
                sckt.emit('game_list', {});
            }, sckt);
        }
        else {
            sckt.on('connect', function () {
                this.emit('auth', {
                    token: token
                });
                this.emit('join', {
                    roomId: roomId
                });
            }, sckt);
        }
        // Start socket instance
        sckt.connect();
        return sckt;
    }
    ;
    // refresh game list
    $('#refresh').click(function () {
        sckt.emit('game_list', {});
    });
    // click to join
    $('#gamelist').on('click', 'tr', function () {
        var uuid = $(this).attr("uuid");
        roomid = uuid;
        sckt.emit('join', { roomId: uuid });
        $('#lobby').addClass('collapse');
        $('#game').removeClass('collapse');
    });
    // create new game
    $('#create').on('click', function () {
        var dict = $('#dict').val();
        sckt.emit('create', { dict: dict });
    });
    // game log
    function log(msg) {
        var control = $('#log');
        control.html(control.html() + msg + '<br/>');
        control.scrollTop(control.scrollTop() + 1000);
        print_status();
    }
    ;
    // print game status
    function print_status() {
        var scores = $('#scores');
        scores.html('<li class="list-group-item">user: ' + user + '</li>' + '<li class="list-group-item">roomid: ' + roomid + '</li>' + '<li class="list-group-item">url: ' + window.location.hostname + '/game?id=' + roomid + '<li class="list-group-item">Letter: ' + letter + '</li>');
        for (var p in game_status) {
            scores.html(scores.html() + '<li class="list-group-item">' + p + ': ' + game_status[p].score + '</li>');
        }
        var words = $('#words');
        words.html(' ');
        for (var p in game_status) {
            words.html(words.html() + '<li class="list-group-item">' + p + ': ' + game_status[p].words + '</li>');
        }
    }
    ;
    // get player move
    $('#move').submit(function () {
        var text = $('#text').val().toLowerCase();
        // chekc first letter
        if (text.charAt(0) !== letter) {
            log("Client: " + text + " is don't start with " + letter);
        }
        else if ($.inArray(text, game_status[user].words) === 1 || $.inArray(text, game_status[user].words) === 1) {
            log("Client: " + text + " is used");
        }
        else {
            sckt.emit('move', {
                move: text
            });
        }
        $('#text').val('').focus();
        return false;
    });
    //socket handlers
    sckt.on('join', function (data) {
        log(data.username + ' entered room');
    });
    sckt.on('leave', function (data) {
        log(data.username + ' left room');
    });
    sckt.on('auth_error', function (data) {
        log('auth error');
        sckt.disconnect();
    });
    sckt.on('end', function (data) {
        log('game end');
        sckt.disconnect();
    });
    //get username from server
    sckt.on('auth', function (data) {
        user = data.username;
    });
    //server messages
    sckt.on('server', function (data) {
        if (typeof data.letter !== 'undefined') {
            letter = data.letter;
            $('#text').attr('placeholder', letter);
        }
        ;
        log('Server: ' + data.message);
    });
    sckt.on('move', function (data) {
        game_status[data.username].words.push(data.move);
        game_status[data.username].score += data.move.length;
        log('Server: ' + data.username + ' played ' + data.move);
    });
    sckt.on('game_state', function (data) {
        for (var p in data) {
            game_status[data[p].name] = data[p];
        }
        print_status();
    });
    sckt.on('game_list', function (data) {
        $('#gamelist').html('');
        for (var p in data.list) {
            $('#gamelist').append('<tr uuid="' + data.list[p].uuid + '"><td>' + data.list[p].dict + '</td><td>' + data.list[p].uuid + '</td></tr>');
        }
    });
    sckt.on('create', function (data) {
        roomid = data.roomid;
        sckt.emit('join', { roomId: roomid });
        $('#lobby').addClass('collapse');
        $('#game').removeClass('collapse');
    });
});
