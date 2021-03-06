#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import json
import logging
from itsdangerous import URLSafeTimedSerializer
import hashlib
import uuid
from sockjsroom import SockJSRoomHandler
from website.config import Config
from werkzeug.security import safe_str_cmp
from website.models import User
from game import Game
from exceptions import *
from tornado import gen, httpclient

# temp config variables

http_client = httpclient.AsyncHTTPClient()
token_max_age = None
s = URLSafeTimedSerializer(secret_key=Config.SECRET_KEY, salt='remember-salt')


def encode_string(string):
    """Encodes a string to bytes, if it isn't already.
    :param string: The string to encode"""

    if isinstance(string, unicode):
        string = string.encode('utf-8')
    return string


def md5(data):
    return hashlib.md5(encode_string(data)).hexdigest()


class ServerConnection(SockJSRoomHandler):
    _game = {}

    def getGame(self, _id):
        """ Retrieve a game from it's id """
        if (self._gcls() + _id) in self._game:
            return self._game[self._gcls() + _id]
        return None

    # override leave for perment rooms
    def leave(self, _id):
        """ Leave a room """
        if (self._gcls() + _id) in self._room:
            self._room[self._gcls() + _id].remove(self)

    def create(self, _id, dict):
        """ Create a room """
        if not (self._gcls() + _id) in self._room:
            self._room[self._gcls() + _id] = set()
            self._game[self._gcls() + _id] = Game(_id, dict)

    def remove(self,_id):
        del self._room[self._gcls() + _id]
        del self._game[self._gcls() + _id]

    def join(self, _id):
        """ Join a room """
        if not (self._gcls() + _id) in self._room:
            raise BadRoomIdError
        else:
            self._room[self._gcls() + _id].add(self)
            # add player to game
            self._game[self._gcls() + _id].add_player(self.userid, self.username)

    def on_open(self, info):
        """ open socket handler """
        self.create('addds', 'en')
        self.create('ttttt', 'tr')
        self.create('ahhhhh', 'en')

    def __init__(self, session):
        super(ServerConnection, self).__init__(session)
        self.userid = None
        self.roomId = '-1'
        self.username = ''
        self.isAuthenticated = False

    def token_loader(self, token):
        """ decrypt remember me token and get userid and username"""
        try:
            data = s.loads(token, max_age=token_max_age)
            user = User.query.filter_by(id=data[0]).first()
            if user and safe_str_cmp(md5(user.password), data[1]):
                self.userid = data[0]
                self.username = user.username
                # give client to username
                self.publishToMyself(self.roomId, 'auth',
                                     {'username': self.username})
                return True
        except:
            # TODO error handling
            pass
        return False

    def on_auth(self, data):
        """auth handler"""
        if "token" not in data:
            self.publishToMyself(self.roomId, 'auth_error', {})
            self.isAuthenticated = False
        elif self.token_loader(data["token"]):
            self.publishToMyself(self.roomId, 'auth_succes', {})
            self.isAuthenticated = True
        else:
            self.publishToMyself(self.roomId, 'auth_error', {})
            self.isAuthenticated = False

    def on_game_list(self, data):
        """ emit game list """
        list = []
        for game in self._game.itervalues():
            list.append(game.game_info())
        self.publishToMyself(self.roomId, 'game_list', {'list': list})

    def on_join(self, data):
        """ join handler """
        if self.isAuthenticated:
            room = str(data['roomId'])
            try:
                # join room
                self.join(room)
                # get game of joined room
                self.game = self.getGame(room)
                self.roomId = room
                # inform clients
                self.publishToMyself(self.roomId, 'server',
                                     {'letter': self.game.letter, 'message': u"Letter is " + self.game.letter})
                self.publishToRoom(self.roomId, 'game_state', self.game.get_game_state())
                self.publishToRoom(self.roomId, 'join', {
                    'username': self.username
                })
            except BadRoomIdError:
                self.publishToMyself(self.roomId, 'server', {
                    'time': datetime.utcnow(),
                    'message': u" Room not found"
                })

    def on_move(self, data):
        """ player move handler """
        if self.isAuthenticated:
            move = data["move"].encode('utf-8')
            try:
                if self.game.player_move(self.userid, move):
                    self.publishToRoom(self.roomId, 'move', {
                        'username': self.username,
                        'time': datetime.utcnow(),
                        'move': move
                    })
                    self.publishToRoom(self.roomId, 'server',
                                       {'letter': self.game.letter, 'message': u"Letter is " + self.game.letter})
            except BadWordError:
                self.publishToMyself(self.roomId, 'server', {
                    'time': datetime.utcnow(),
                    'message': move + u" is not in dictionary"
                })
                self.publishToMyself(self.roomId, 'server',
                                     {'letter': self.game.letter, 'message': u"Letter is " + self.game.letter})
            except TurnError:
                self.publishToMyself(self.roomId, 'server', {
                    'time': datetime.utcnow(),
                    'message': move + u" It isn't your turn"
                })
                self.publishToMyself(self.roomId, 'server',
                                     {'letter': self.game.letter, 'message': u"Letter is " + self.game.letter})
            except GameEnd as e:
                self.publishToRoom(self.roomId, 'end',
                                     {})

                self.remove(self.roomId)
                url = 'http://localhost:5000/api/save_game'
                headers = {
                    'Content-Type': 'application/json'
                }
                # send to flask
                http_client.fetch(url, method="POST", headers=headers, body=json.dumps(e.game))

    def on_create(self, data):
        """game create handler"""
        if self.isAuthenticated:
            id = str(uuid.uuid4())
            self.create(id, data['dict'])
            self.publishToMyself(self.roomId, 'create',
                                 {'roomid': id})

    def on_close(self):
        try:
            self.on_leave()
        except TypeError:
            self.roomId = '-1'
            self.isAuthenticated = False

    def on_leave(self):
        ''' Quit game '''
        # Only if user has time to call self.initialize
        # (sometimes it's not the case)
        if self.roomId != '-1':
            # Debug
            logging.debug('chat: leave room (roomId: %s)' % self.roomId)

            # Say to other users the current user leave room
            self.publishToRoom(self.roomId, 'leave', {
                'username': str(self.username)
            })

            # Remove sockjsroom link to this room
            self.leave(self.roomId)
        self.roomId = '-1'
        self.isAuthenticated = False
