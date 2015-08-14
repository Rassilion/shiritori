#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itsdangerous import URLSafeTimedSerializer
from dictionary import english
import random
import uuid
from sockjs.tornado import SockJSConnection
import json
from config import Config

s = URLSafeTimedSerializer(secret_key=Config.SECRET_KEY, salt='remember-salt')


class Game(object):
    def __init__(self):
        self.id = uuid.uuid4()
        self.p1 = 0
        self.p2 = 0
        self.p1_list = []
        self.p2_list = []
        self.letter = "a"

    def __repr__(self):
        return str(self.id)

    def check(self, word):
        if word.startswith(self.letter) and word not in self.p1_list and word not in self.p2_list and word in english[
            self.letter]:
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


class ServerConnection(SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = set()
    game = Game()

    def on_open(self, info):
        self.userid = None

    def on_message(self, message):
        parsed_massage = json.loads(message)
        if "auth" in parsed_massage:
            self.participants.add(self)
            self.userid = s.loads(parsed_massage["auth"])[0]
            self.broadcast(self.participants,
                           json.dumps({'user': 'server', 'text': self.userid + ' joined.'}))
        else:
            if self.userid == "player1" and self.game.p1_move(parsed_massage["text"]):
                msg = json.dumps({"user": self.userid, "text": parsed_massage["text"]})
                print msg
                self.broadcast(self.participants, msg)
            elif self.game.p2_move(parsed_massage["text"]):
                msg = json.dumps({"user": self.userid, "text": parsed_massage["text"]})
                print msg
                self.broadcast(self.participants, msg)
            else:
                self.broadcast(self.participants,
                               json.dumps({'user': 'server', 'text': parsed_massage["text"] + ' Error'}))
        self.broadcast(self.participants, json.dumps({'user': 'server', 'text': 'Letter is ' + self.game.letter}))

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

        self.broadcast(self.participants, json.dumps({'user': 'server', "text": self.userid + " left."}))
