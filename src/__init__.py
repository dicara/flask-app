from flask import Flask
app = Flask(__name__)
app.config.from_object('src.default_settings')
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

HOSTNAME                = app.config['HOSTNAME']                 
PORT                    = app.config['PORT']
HOME_DIR                = app.config['HOME_DIR']
UPLOAD_FOLDER           = app.config['UPLOAD_FOLDER']
TORNADO_LOG_FILE_PREFIX = app.config['TORNADO_LOG_FILE_PREFIX']

from . import controller