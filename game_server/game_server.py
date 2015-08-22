#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import logging
from itsdangerous import URLSafeTimedSerializer
import hashlib
import uuid
from sockjsroom import SockJSRoomHandler
from website.config import Config
from werkzeug.security import safe_str_cmp
from website.models import User
from game import Game

# temp config variables
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
        if self._game.has_key(self._gcls() + _id):
            return self._game[self._gcls() + _id]
        return None

    # override leave for perment rooms
    def leave(self, _id):
        """ Leave a room """
        if self._room.has_key(self._gcls() + _id):
            self._room[self._gcls() + _id].remove(self)

    def create(self, _id, dict):
        """ Create a room """
        if not self._room.has_key(self._gcls() + _id):
            self._room[self._gcls() + _id] = set()
            self._game[self._gcls() + _id] = Game(_id, dict)

    def join(self, _id):
        """ Join a room """
        if not self._room.has_key(self._gcls() + _id):
            # TODO: Send error meesage to client
            print "room not found"
        else:
            self._room[self._gcls() + _id].add(self)
            # add player to game
            self._game[self._gcls() + _id].add_player(self.userid, self.username)

    def on_open(self, info):
        """ open socket handler """
        # TODO better way for lobby creation
        if not self._room.has_key(self._gcls() + 'lobby'):
            self._room[self._gcls() + 'lobby'] = set()
            self._game[self._gcls() + 'lobby'] = Game('lobby', 'en')
        if not self._room.has_key(self._gcls() + 'sad'):
            self._room[self._gcls() + 'sad'] = set()
            self._game[self._gcls() + 'sad'] = Game('sad', 'en')
        if not self._room.has_key(self._gcls() + 'bs'):
            self._room[self._gcls() + 'bs'] = set()
            self._game[self._gcls() + 'bs'] = Game('bs', 'en')

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
            self.roomId = str(data['roomId'])
            # join room
            self.join(self.roomId)
            # get game of joined room
            self.game = self.getGame(self.roomId)
            # inform clients
            self.publishToMyself(self.roomId, 'server',
                                 {'letter': self.game.letter, 'message': u"Letter is " + self.game.letter})
            self.publishToMyself(self.roomId, 'game_state', self.game.get_game())
            self.publishToRoom(self.roomId, 'join', {
                'username': self.username
            })

    def on_move(self, data):
        """ player move handler """
        if self.isAuthenticated:
            move = data["move"].encode('utf-8')
            if self.game.player_move(self.userid, move):
                self.publishToRoom(self.roomId, 'move', {
                    'username': self.username,
                    'time': datetime.utcnow(),
                    'move': move
                })
                self.publishToRoom(self.roomId, 'server',
                                   {'letter': self.game.letter, 'message': u"Letter is " + self.game.letter})
            else:
                # TODO: Error handler
                self.publishToRoom(self.roomId, 'server', {
                    'time': datetime.utcnow(),
                    'message': move + u" error"
                })
                self.publishToRoom(self.roomId, 'server',
                                   {'letter': self.game.letter, 'message': u"Letter is " + self.game.letter})

    def on_create(self, data):
        """game create handler"""
        if self.isAuthenticated:
            id = str(uuid.uuid4())
            self.create(id, data['dict'])
            self.publishToMyself(self.roomId, 'create',
                                 {'roomid': id})

    def on_close(self):
        self.on_leave()

    def on_leave(self):
        ''' Quit game '''
        # Only if user has time to call self.initialize
        # (sometimes it's not the case)
        if self.roomId != '-1':
            # Debug
            logging.debug('chat: leave room (roomId: %s)' % self.roomId)

            # Say to other users the current user leave room
            self.publishToOther(self.roomId, 'leave', {
                'username': str(self.username)
            })

            # Remove sockjsroom link to this room
            self.leave(self.roomId)
        self.roomId = '-1'
        self.isAuthenticated = False
