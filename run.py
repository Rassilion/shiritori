#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from website import app

from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado import web
from sockjs.tornado import SockJSRouter
from game_server.game_server import ServerConnection
from guppy import hpy

from tornado.options import define, options

define("port", default=5000, help="run on the given port", type=int)


class MemoryHandler(web.RequestHandler):
    def get(self):
        h = hpy()
        r = h.heap()
        self.write('<pre>')
        self.write(unicode(r))
        r = r.more
        self.write(unicode(r))
        r = r.more
        self.write(unicode(r))
        self.write('</pre>')


def configureLogger():
    ''' Start the logger instance and configure it '''
    # Set debug level
    logLevel = 'DEBUG'
    logger = logging.getLogger()
    logger.setLevel(logLevel)

    # Format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(name)s -> %(message)s', '%Y-%m-%d %H:%M:%S')

    # Remove default handler to keep only clean one
    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)

    #
    # ----------------------------
    #   CREATE CONSOLE HANDLER
    # ----------------------------
    #

    # Create console handler
    consoleh = logging.StreamHandler()
    consoleh.setLevel(logLevel)
    consoleh.setFormatter(formatter)

    # Set our custom handler
    logger.addHandler(consoleh)


app.debug = True
wsgi_app = WSGIContainer(app)

EchoRouter = SockJSRouter(ServerConnection, '/game1')

# add flask to tornado urls
tornado_app = web.Application(
    EchoRouter.urls + [(r'/memory', MemoryHandler), ('.*', web.FallbackHandler, dict(fallback=wsgi_app)),
                       ], debug=True)

# start server
options.parse_command_line()
tornado_app.listen(options.port)

configureLogger()

# Print logger message
logging.debug('\n\nSystem start at: %s port: %s\nSystem log level: %s\n' % (datetime.utcnow(), options.port, 'DEBUG'))

IOLoop.instance().start()
