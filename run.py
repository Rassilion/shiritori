#!/usr/bin/env python
# -*- coding: utf-8 -*-
from shiritori import socketio,app

if __name__ == '__main__':
    app.debug = True
    socketio.run(app)
