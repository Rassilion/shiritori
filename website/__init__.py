#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from website.admin import init_admin
init_admin(app)



# asset management
# env = Environment(app)
# # asser setup
# assets = Environment(app)
# # Tell flask-assets where to look for our coffeescript and sass files.
# dir = os.path.dirname(Config.basedir)
# env.load_path = [
#     # os.path.join(dir, 'sass'),
#     os.path.join(dir, 'typescript'),
#     os.path.join(dir, 'bower_components')
# ]
#
# js = Bundle(
#     'jquery/dist/jquery.js',
#     filters='jsmin',
#     output='js_all.js'
# )
# ts = Bundle(
#         'typings/jquery/jquery.d.ts',
#         'game.ts',
#         filters='typescript',
#     output='ts_all.js'
#     )
# assets.register('js_all', js)
# assets.register('ts_all', ts)
#
# env.register(
#     'css_all',
#     Bundle(
#         'all.sass',
#         filters='sass',
#         output='css_all.css'
#     )
# )

from views import *
