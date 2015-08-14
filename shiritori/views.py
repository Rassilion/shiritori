#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, flash, g, jsonify
from shiritori import app, forms
from game import Game
import time
import json
from shiritori.models import user_datastore
from flask.ext.security import Security, current_user, auth_token_required

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

    try:
        print current_user.is_authenticated()
        print g.session
    except:
        pass
    return render_template('game.html')

@app.route('/dummy-api/', methods=['GET'])
@auth_token_required
def dummyAPI():
    ret_dict = {
        "Key1": "Value1",
        "Key2": "value2"
    }
    return jsonify(items=ret_dict)
