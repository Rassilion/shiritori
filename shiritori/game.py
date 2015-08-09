#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dictionary import english
import random
import uuid
from sockjs.tornado import SockJSConnection
import json


class Game(object):
    def __init__(self, id):
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
            self.p2_move()
            return True
        else:
            return False

    def p2_move(self):
        word = ""
        while (not self.check(word)):
            word = random.choice(english[self.letter])
        self.p2 += len(word)
        self.letter = word[-1]
        self.p2_list.append(word)


class ServerConnection(SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = {}

    def on_open(self, info):
        pass

    def on_message(self, message):
        parsed_massage = json.loads(message)
        if "user" in parsed_massage:
            self.participants[parsed_massage["user"]] = self
            self.broadcast(self.participants.itervalues(), parsed_massage["user"]+" joined.")
        else:
            # Broadcast message
            self.broadcast(self.participants.itervalues(), message)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

        self.broadcast(self.participants.itervalues(), "Someone left.")
