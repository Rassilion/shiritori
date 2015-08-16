/// <reference path="typings/tsd.d.ts" />
$(function () {

    var token = Cookies.get("remember_token");
    var sckt = GameRoom('1', token);
    var scores = null;
    var words = null;
    ;


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
    }

    $('form').submit(function () {
        var text = $('#text').val();

        sckt.emit('move', {
            move: text
        });
        $('#text').val('').focus();
        return false;
    });


    // On 'leave/join' receive, we say to all other user who connect/disco
    sckt.on('join', function (data) {
        log('User ' + data.username + ' entered room');
    });
    sckt.on('leave', function (data) {
        log('User ' + data.username + ' left room');
    })
    sckt.on('server', function (data) {
        log('Server: ' + data.message);
    })
    sckt.on('move', function (data) {
        log('Server: ' + 'User ' + data.username + ' played ' + data.move);
    })
    sckt.on('game_state', function (data) {
        scores = data.scores;
        words = data.words;
    })

});