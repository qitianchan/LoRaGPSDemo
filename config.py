# -*- coding: utf-8 -*-
"""
    ashbin.configs.default
    ~~~~~~~~~~~~~~~~~~~~~~~

    This is the default configuration for FlaskBB that every site should have.
    You can override these configuration variables in another class.


"""
import os
from flask import url_for


class DefaultConfig(object):

    # Get the app root path
    #            <_basedir>
    # ../../ -->  flaskbb/flaskbb/configs/base.py
    _basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)))

    DEBUG = True
    TESTING = False

    # Logs
    # If SEND_LOGS is set to True, the admins (see the mail configuration) will
    # recieve the error logs per email.
    SEND_LOGS = False

    # The filename for the info and error logs. The logfiles are stored at
    # flaskbb/logs
    INFO_LOG = "info.log"
    ERROR_LOG = "error.log"

    # Default Database
    DATABASE_PATH = _basedir + '/' + 'loragpsdemo.sqlite'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

    # This will print all SQL statements
    SQLALCHEMY_ECHO = False

    # Security
    # This is the secret key that is used for session signing.
    # You can generate a secure key with os.urandom(24)
    SECRET_KEY = '\x99A\x8f\x0f\xe5tG\xe6f\t\xfe\xe1Y\xe9X,\xb6\xdf,\xea\x12q\xc9\xc5'

    # Protection against form post fraud
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = "\x99A\x8f\x0f\xe5tG\xe6f\t\xfe\xe1Y\xe9X,\xb6\xdf,\xea\x12q\xc9\xc5"

    MSG_FILE_LOG = os.path.join(_basedir, 'logs/message.log')
    SOCKETIO_FILE_LOG = os.path.join(_basedir, 'logs/socketio.log')


# Const Value
BASESTATION = 1
NODE = 2
BASESTATION_IMG_URI = 'image/mark_station.png'
NODE_IMG_URI = 'image/mark_node.png'

# Ourself Server websocket infomation
LORA_APP_EUI = 'FFFFFFFFFFFFFFFF'
LORA_TOKEN = 'Ik8T-cXls3TWhtNtjhzc5A'
LORA_HOST = '183.230.40.231'
LORA_PORT = 8100
NAMESPACE_PATH = '/test'

