#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dictionary import english, turkish
from datetime import datetime
from exceptions import *


class Game(object):
    @staticmethod
    def get_dictionary(code):
        """ Gets python dictionary of given language
        :param code: language code
        :return: language dictionary
        """
        if code == 'tr':
            return turkish
        if code == 'en':
            return english

    def __init__(self, id, code):
        """ Game constructor
        :param id: uuid4 id
        :param code: language code
        :return: game object
        """
        self.uuid = id
        self.players = {}
        self.last_turn = None
        # game dictionary
        self.dictionary_code = code
        self.dictionary = self.get_dictionary(code)

        # TODO game types
        self.mode = None
        # TODO random start letter?
        self.letter = "a"
        self.timestamp = datetime.utcnow()

    def words(self):
        """return player used word list"""
        w = []
        for p in self.players:
            w += self.players[p]['words']
        return w

    def winner(self):
        """return winner player"""
        pl = None
        s = -1
        for p in self.players:
            if self.players[p]['score'] > s:
                s = self.players[p]['score']
                pl = p
        return pl

    def __repr__(self):
        return str(self.uuid)

    def add_player(self, id, name):
        """add a player to game
        :param id: player id (db)
        :param name: username
        """
        if id not in self.players:
            self.players[id] = {'name': name, 'score': 0, 'words': []}

    def check_word(self, word):
        """
        check if word is in language dictionary and not in words list
        :param word: word
        :return: True or False
        """
        if not word.startswith(self.letter):
            raise BadLetterError
        elif word in self.words():
            raise UsedWordError
        elif word not in self.dictionary:
            raise BadWordError
        else:
            return True

    def player_move(self, id, word):
        """
        make player move
        :param id: player id (db)
        :param word: player move
        :return: True or False
        """
        # check players turn
        # TODO more than 2 player support
        if self.last_turn is id:
            raise TurnError
        elif self.check_word(word):
            self.players[id]['score'] += len(word)
            self.letter = word[-1]
            self.players[id]['words'].append(word)
            self.last_turn = id
            self.check_game()
            return True
        else:
            raise GameError

    def check_game(self):
        """check game"""
        # first mode score 100
        s = 100
        for p in self.players:
            if self.players[p]['score'] > s:
                raise GameEnd(self.endgame(p))

    # def ai_move(self):
    #     word = ""
    #     while not self.check(word):
    #         word = random.choice(english[self.letter])
    #     self.p2 += len(word)
    #     self.letter = word[-1]
    #     self.p2_words.append(word)

    # TODO hide userid
    def get_game_state(self):
        """return game state dictionary"""
        return self.players

    def game_info(self):
        """return game info(for game list) dictionary"""
        return {'dict': self.dictionary_code, 'uuid': self.uuid}

    def endgame(self, winner):
        """return game dictionary for db insert"""
        return {'dict': self.dictionary_code, 'uuid': self.uuid, 'winner': winner, 'time': str(self.timestamp),
                'players': self.players}
