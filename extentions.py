# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

io = SocketIO()
db = SQLAlchemy()