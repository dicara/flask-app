#=============================================================================
# Imports
#=============================================================================
from flask import Flask
from pymongo import MongoClient

#=============================================================================
# Create Flask app and read in configuration files
#=============================================================================
app = Flask(__name__)
app.config.from_object('src.default_settings')
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#=============================================================================
# Connect to MongoDB
#=============================================================================
CLIENT = MongoClient(app.config['DATABASE_URL'], app.config['DATABASE_PORT'])
DB     = CLIENT[app.config['DATABASE_NAME']]

#=============================================================================
# Parse configuration
#=============================================================================
HOSTNAME                = app.config['HOSTNAME']                 
PORT                    = app.config['PORT']
USER_HOME_DIR           = app.config['USER_HOME_DIR']
HOME_DIR                = app.config['HOME_DIR']
TARGETS_UPLOAD_FOLDER   = app.config['TARGETS_UPLOAD_FOLDER']
PROBES_UPLOAD_FOLDER    = app.config['PROBES_UPLOAD_FOLDER']
REFS_FOLDER             = app.config['REFS_FOLDER']
TORNADO_LOG_FILE_PREFIX = app.config['TORNADO_LOG_FILE_PREFIX']
TARGETS_COLLECTION      = app.config['TARGETS_COLLECTION']
PROBES_COLLECTION       = app.config['PROBES_COLLECTION']
VALIDATION_COLLECTION   = app.config['VALIDATION_COLLECTION']

from . import controller