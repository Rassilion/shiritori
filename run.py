#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from datetime import datetime
from shiritori import app

from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado import web
from sockjs.tornado import SockJSRouter, SockJSConnection
from shiritori.game import ServerConnection


def configureLogger(logFolder, logFile):
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

    # Create missing folder if needed
    if not os.path.exists(logFolder):
        os.makedirs(logFolder, 0700)

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

    #
    # ----------------------------
    #   CREATE FILE HANDLER
    # ----------------------------
    #
    fileh = logging.FileHandler(logFile, 'a')
    fileh.setLevel(logLevel)
    fileh.setFormatter(formatter)

    # Set our custom handler
    logger.addHandler(fileh)


app.debug = True
wsgi_app = WSGIContainer(app)

EchoRouter = SockJSRouter(ServerConnection, '/game1')

# add flask to tornado urls
tornado_app = web.Application(EchoRouter.urls + [('.*', web.FallbackHandler, dict(fallback=wsgi_app)),
                                                 ])
tornado_app.listen(5000)

logFile = './application.log'
logFolder = os.path.dirname(logFile)
configureLogger(logFolder, logFile)

# Print logger message
logging.debug('\n\nSystem start at: %s\nSystem log level: %s\n' % (datetime.now(), 'DEBUG'))

IOLoop.instance().start()
