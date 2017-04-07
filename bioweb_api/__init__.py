#=============================================================================
# Imports
#=============================================================================
from flask import Flask

#=============================================================================
# Create Flask app and read in configuration files
#=============================================================================
app = Flask(__name__)
app.config.from_object('bioweb_api.default_settings')
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#=============================================================================
# Parse configuration
#=============================================================================
HOSTNAME                     = app.config['HOSTNAME']
MAX_BUFFER_SIZE              = app.config['MAX_BUFFER_SIZE']
PORT                         = app.config['PORT']
DATABASE_URL                 = app.config['DATABASE_URL']
DATABASE_NAME                = app.config['DATABASE_NAME']
DATABASE_PORT                = app.config['DATABASE_PORT']
HOME_DIR                     = app.config['HOME_DIR']
TARGETS_UPLOAD_PATH          = app.config['TARGETS_UPLOAD_PATH']
PROBES_UPLOAD_PATH           = app.config['PROBES_UPLOAD_PATH']
PLATES_UPLOAD_PATH           = app.config['PLATES_UPLOAD_PATH']
RESULTS_PATH                 = app.config['RESULTS_PATH']
REFS_PATH                    = app.config['REFS_PATH']
TMP_PATH                     = app.config['TMP_PATH']
TORNADO_LOG_FILE_PREFIX      = app.config['TORNADO_LOG_FILE_PREFIX']
MAX_WORKERS                  = app.config['MAX_WORKERS']
ARCHIVES_PATH                = app.config['ARCHIVES_PATH']
RUN_REPORT_PATH              = app.config['RUN_REPORT_PATH']
MODIFIED_ARCHIVES_PATH       = app.config['MODIFIED_ARCHIVES_PATH']
TARGETS_COLLECTION           = app.config['TARGETS_COLLECTION']
PROBES_COLLECTION            = app.config['PROBES_COLLECTION']
PLATES_COLLECTION            = app.config['PLATES_COLLECTION']
VALIDATION_COLLECTION        = app.config['VALIDATION_COLLECTION']
ABSORPTION_COLLECTION        = app.config['ABSORPTION_COLLECTION']
PA_PROCESS_COLLECTION        = app.config['PA_PROCESS_COLLECTION']
FA_PROCESS_COLLECTION        = app.config['FA_PROCESS_COLLECTION']
PA_PLOTS_COLLECTION          = app.config['PA_PLOTS_COLLECTION']
PA_CONVERT_IMAGES_COLLECTION = app.config['PA_CONVERT_IMAGES_COLLECTION']
SA_IDENTITY_COLLECTION       = app.config['SA_IDENTITY_COLLECTION']
SA_ASSAY_CALLER_COLLECTION   = app.config['SA_ASSAY_CALLER_COLLECTION']
SA_GENOTYPER_COLLECTION      = app.config['SA_GENOTYPER_COLLECTION']
DYES_COLLECTION              = app.config['DYES_COLLECTION']
DEVICES_COLLECTION           = app.config['DEVICES_COLLECTION']
ARCHIVES_COLLECTION          = app.config['ARCHIVES_COLLECTION']
HDF5_COLLECTION              = app.config['HDF5_COLLECTION']
PROBE_EXPERIMENTS_COLLECTION = app.config['PROBE_EXPERIMENTS_COLLECTION']
PROBE_METADATA_COLLECTION    = app.config['PROBE_METADATA_COLLECTION']
IMAGES_COLLECTION            = app.config['IMAGES_COLLECTION']
RUN_REPORT_COLLECTION        = app.config['RUN_REPORT_COLLECTION']
EXP_DEF_COLLECTION           = app.config['EXP_DEF_COLLECTION']

from . import controller
