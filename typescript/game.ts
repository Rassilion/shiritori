/// <reference path="typings/tsd.d.ts" />

$(function main() {
    var qs = (function (a) {
        if (a == "") return {};
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

    var token = Cookies.get("remember_token");
    var roomid = qs["id"];
    if (roomid === undefined) {
        roomid = '1';
    }
    ;
    var sckt = GameRoom(roomid, token);
    var game_status = {'p2': {'score': 0, 'words': []}, 'p1': {'score': 0, 'words': []}};
    var letter;


    /**
     * Create a new socket instance between client and server,
     * and start use it
     *
     * @method GameRoom
     *
     * @param roomId {String} A unique string to represent a single room
     * @param username {String} The username to use on this room
     */
    function GameRoom(roomId, token) {
        var sckt = new socket('game1', true);

        // On every connect, the server 'loose' us
        // so we have to join again
        sckt.on('connect', function () {
            // Everytime a connect appear, we have to logon again
            this.emit('join', {
                token: token,
                roomId: roomId
            });
        }, sckt);

        // Start socket instance
        sckt.connect();

        return sckt;
    };

    function log(msg) {
        var control = $('#log');
        control.html(control.html() + msg + '<br/>');
        control.scrollTop(control.scrollTop() + 1000);
        print_status()
    };

    function print_status() {
        var scores = $('#scores');
        scores.html('<li>roomid: ' + roomid + '</li>' +'<li>p1: ' + game_status.p1.score + '</li>' + '<li>p2: ' + game_status.p2.score + '</li>' + '<li>Letter: ' + letter + '</li>');
        var words = $('#words');
        words.html('<li>p1: ' + game_status.p1.words + '</li>' + '<li>p2: ' + game_status.p2.words + '</li>');

    };

    $('#move').submit(function () {
        var text = $('#text').val().toLowerCase();
        if (text.charAt(0) !== letter) {
            log("Client: " + text + " is don't start with " + letter);
        }
        else if ($.inArray(text, game_status.p1.words) === 1 || $.inArray(text, game_status.p2.words) === 1) {
            log("Client: " + text + " is used");
        } else {

            sckt.emit('move', {
                move: text
            });
        }


        $('#text').val('').focus();
        return false;
    });


    // On 'leave/join' receive, we say to all other user who connect/disco
    sckt.on('join', function (data) {
        log('User ' + data.username + ' entered room');
    });
    sckt.on('leave', function (data) {
        log('User ' + data.username + ' left room');
    });
    sckt.on('auth_error', function (data) {
        log('auth error');
        sckt.disconnect();
    });
    sckt.on('server', function (data) {
        if (typeof data.letter !== 'undefined') {
            letter = data.letter;
            $('#text').attr('placeholder', letter);
        }
        ;
        log('Server: ' + data.message);
    });
    sckt.on('move', function (data) {
        log('Server: ' + 'User ' + data.username + ' played ' + data.move);
        //TODO save words to right user
        game_status.p1.words.push(data.move)
    });
    sckt.on('game_state', function (data) {
            game_status.p1.score = data.p1.score;
            game_status.p1.words = data.p1.words;
            game_status.p2.score = data.p2.score;
            game_status.p2.words = data.p2.words;
            print_status()
        }
    );

});