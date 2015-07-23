#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, flash, g
from shiritori import app, forms
from game import Game
import time


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


game_list = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    form = forms.CreateForm()
    if form.validate_on_submit():
        id = form.id.data
        game_list[id] = Game(id)
    return render_template('index.html', list=game_list.keys(), form=form)


@app.route('/game/<int:id>', methods=['GET', 'POST'])
def game(id):
    form = forms.GameForm()
    if form.validate_on_submit():
        if game_list[id].p1_move(form.word.data):
            form.word.data = game_list[id].letter
            flash(u"devam")
        else:
            flash(u"yanlış")
    return render_template('game.html', form=form, game=game_list[id])
