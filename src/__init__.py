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
DEV                     = app.config['DEV']                 
HOSTNAME                = app.config['HOSTNAME']                 
PORT                    = app.config['PORT']
USER_HOME_DIR           = app.config['USER_HOME_DIR']
HOME_DIR                = app.config['HOME_DIR']
TARGETS_UPLOAD_PATH     = app.config['TARGETS_UPLOAD_PATH']
PROBES_UPLOAD_PATH      = app.config['PROBES_UPLOAD_PATH']
PLATES_UPLOAD_PATH      = app.config['PLATES_UPLOAD_PATH']
RESULTS_PATH            = app.config['RESULTS_PATH']
REFS_PATH               = app.config['REFS_PATH']
TMP_PATH                = app.config['TMP_PATH']
TORNADO_LOG_FILE_PREFIX = app.config['TORNADO_LOG_FILE_PREFIX']
ARCHIVES_PATH           = app.config['ARCHIVES_PATH']
TARGETS_COLLECTION      = app.config['TARGETS_COLLECTION']
PROBES_COLLECTION       = app.config['PROBES_COLLECTION']
PLATES_COLLECTION       = app.config['PLATES_COLLECTION']
VALIDATION_COLLECTION   = app.config['VALIDATION_COLLECTION']
ABSORPTION_COLLECTION   = app.config['ABSORPTION_COLLECTION']
PA_PROCESS_COLLECTION   = app.config['PA_PROCESS_COLLECTION']

from . import controller