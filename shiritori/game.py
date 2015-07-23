#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dictionary import english
import random


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
