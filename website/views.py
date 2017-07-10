#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, flash, g, jsonify,request,make_response
from website import app, forms,db
import time
from website.models import user_datastore,Game
from flask_security import Security, current_user

# initilize flask-security
security = Security(app, user_datastore)


@app.before_first_request
def test():
    pass


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/game', methods=['GET', 'POST'])
def game():
    return render_template('game.html')


@app.route('/api/save_game', methods=['POST'])
def save_game():
    if request.json:
        # TODO save db
        print request.json
    return jsonify({'status':'ok'})



