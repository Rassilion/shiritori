#!/usr/bin/env python
# -*- coding: utf-8 -*-
from shiritori import app

from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado import web
from sockjs.tornado import SockJSRouter, SockJSConnection
from shiritori.game import ServerConnection
from tornado.log import enable_pretty_logging
enable_pretty_logging()

app.debug = True
wsgi_app = WSGIContainer(app)

EchoRouter = SockJSRouter(ServerConnection, '/game1')

# add flask to tornado urls
tornado_app = web.Application(EchoRouter.urls + [('.*', web.FallbackHandler, dict(fallback=wsgi_app)),
                                                 ])
tornado_app.listen(5000)
IOLoop.instance().start()
