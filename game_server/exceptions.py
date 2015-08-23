#!/usr/bin/env python
# -*- coding: utf-8 -*-


class GameError(Exception):
    """base class for game errors"""
    pass


class SockError(Exception):
    """base class for sock message errors"""
    pass


class WordError(GameError):
    """base class for game word errors"""
    pass


class PlayerExistError(GameError):
    """player is exist in game"""
    pass


class TurnError(GameError):
    """not player's turn"""
    pass


class UsedWordError(WordError):
    """word used before"""
    pass


class BadWordError(WordError):
    """word not in the dictionary"""
    pass


class BadLetterError(WordError):
    """start letter is wrong"""
    pass


class GameEnd(GameError):
    """game finished"""

    def __init__(self, game):
        self.game = game


class BadRoomIdError(SockError):
    """room dont exist"""
    pass
