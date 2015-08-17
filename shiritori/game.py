#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import logging
from itsdangerous import URLSafeTimedSerializer
from dictionary import english, turkish
import random
import uuid
from sockjsroom import SockJSRoomHandler
import json
from config import Config

s = URLSafeTimedSerializer(secret_key=Config.SECRET_KEY, salt='remember-salt')


class Game(object):
    def __init__(self, id):
        self.id = id
        self.p1 = 0
        self.p2 = 0
        self.p1_list = []
        self.p2_list = []
        self.letter = "a"

    def __repr__(self):
        return str(self.id)

    def check(self, word):
        if word.startswith(self.letter) and word not in self.p1_list and word not in self.p2_list and word in english:
            return True
        else:
            return False

    def p1_move(self, word):
        if self.check(word):
            self.p1 += len(word)
            self.letter = word[-1]
            self.p1_list.append(word)
            return True
        else:
            return False

    def p2_move(self, word):
        if self.check(word):
            self.p2 += len(word)
            self.letter = word[-1]
            self.p2_list.append(word)
            return True
        else:
            return False

    def ai_move(self):
        word = ""
        while (not self.check(word)):
            word = random.choice(english[self.letter])
        self.p2 += len(word)
        self.letter = word[-1]
        self.p2_list.append(word)

    # TODO make p1 given userid
    def get_game(self):
        return {'p1': {'score': self.p1, 'words': self.p1_list}, 'p2': {'score': self.p2, 'words': self.p2_list}}


class ServerConnection(SockJSRoomHandler):
    # Class level variable
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

    def create(self, _id):
        if not self._room.has_key(self._gcls() + _id):
            self._room[self._gcls() + _id] = set()
            self._game[self._gcls() + _id] = Game(_id)
        print len(self._game)

    def join(self, _id):
        """ Join a room """
        if not self._room.has_key(self._gcls() + _id):
            # TODO: Send error meesage to client
            print "room not found"
        else:
            self._room[self._gcls() + _id].add(self)

    def on_open(self, info):
        self.init()

    def init(self):
        self.userid = None
        self.roomId = '-1'

    def on_join(self, data):
        # TODO: DB check
        # basic auth check
        if "token" not in data:
            self.publishToMyself(self.roomId, 'auth_error', {})
        else:
            # set user information
            self.userid = s.loads(data["token"])[0]
            self.roomId = str(data['roomId'])
            # join room
            self.create(self.roomId)
            self.join(self.roomId)
            # get game of joined room
            self.game = self.getGame(self.roomId)
            # inform clients
            self.publishToMyself(self.roomId, 'server',
                                 {'letter': self.game.letter, 'message': "Letter is " + self.game.letter})
            self.publishToMyself(self.roomId, 'game_state', self.game.get_game())
            self.publishToRoom(self.roomId, 'join', {
                'username': self.userid
            })

    def on_move(self, data):
        if self.roomId != '-1':
            if self.userid == '1' and self.game.p1_move(data["move"]):
                self.publishToRoom(self.roomId, 'move', {
                    'username': self.userid,
                    'time': datetime.now(),
                    'move': str(data['move'])
                })
                self.publishToRoom(self.roomId, 'server',
                                   {'letter': self.game.letter, 'message': "Letter is " + self.game.letter})
            elif self.game.p2_move(data["move"]):
                self.publishToRoom(self.roomId, 'move', {
                    'username': self.userid,
                    'time': datetime.now(),
                    'move': str(data['move'])
                })
                self.publishToRoom(self.roomId, 'server',
                                   {'letter': self.game.letter, 'message': "Letter is " + self.game.letter})
            else:
                # TODO: Error handler
                self.publishToRoom(self.roomId, 'server', {
                    'time': datetime.now(),
                    'message': str(data['move'] + " error")
                })
                self.publishToRoom(self.roomId, 'server',
                                   {'letter': self.game.letter, 'message': "Letter is " + self.game.letter})

    def on_close(self):
        self.on_leave()

    def on_leave(self):
        ''' Quit chat room '''
        # Only if user has time to call self.initialize
        # (sometimes it's not the case)
        if self.roomId != '-1':
            # Debug
            logging.debug('chat: leave room (roomId: %s)' % self.roomId)

            # Say to other users the current user leave room
            self.publishToOther(self.roomId, 'leave', {
                'username': str(self.userid)
            })

            # Remove sockjsroom link to this room
            self.leave(self.roomId)
        self.init()
