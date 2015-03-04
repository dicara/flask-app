'''
Copyright 2014 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Dan DiCara
@date:   Jun 1, 2014
'''

#===============================================================================
# Imports
#===============================================================================
import os
from os.path import expanduser

#===============================================================================
# Configuration Settings
#===============================================================================
DEV           = True
HOSTNAME      = "localhost"
# HOSTNAME      = "bioweb"
USER_HOME_DIR = expanduser("~")
ROOT_DIR      = "/mnt/bigdisk/"

if DEV:
    PORT = 8020
    DATABASE_NAME = "Bioinformatics_dev"
else:
    PORT = 8010
    DATABASE_NAME = "Bioinformatics"
    
DATABASE_URL  = HOSTNAME
DATABASE_PORT = 27017

# Directories
if HOSTNAME == "bioweb":
    HOME_DIR = os.path.join(ROOT_DIR, "api")
else:
    HOME_DIR = os.path.join(USER_HOME_DIR, "gnubio-bioinformatics-rest_api")

TARGETS_UPLOAD_PATH     = os.path.join(HOME_DIR, "uploads", str(PORT), "targets")
PROBES_UPLOAD_PATH      = os.path.join(HOME_DIR, "uploads", str(PORT), "probes")
PLATES_UPLOAD_PATH      = os.path.join(HOME_DIR, "uploads", str(PORT), "plates")
RESULTS_PATH            = os.path.join(HOME_DIR, "results", str(PORT))
REFS_PATH               = os.path.join(HOME_DIR, "refs")
TMP_PATH                = os.path.join(HOME_DIR, "tmp")
TORNADO_LOG_FILE_PREFIX = os.path.join(HOME_DIR, "logs/tornado_%s.log" % str(PORT))
ARCHIVES_PATH           = "/mnt/runs"

# MongoDb Collections
TARGETS_COLLECTION           = "targets"
PROBES_COLLECTION            = "probes"
PLATES_COLLECTION            = "plates"
VALIDATION_COLLECTION        = "validation"
ABSORPTION_COLLECTION        = "absorption"
PA_PROCESS_COLLECTION        = "pa_process"
PA_PLOTS_COLLECTION          = "pa_plots"
PA_CONVERT_IMAGES_COLLECTION = "pa_convert_images"
SA_IDENTITY_COLLECTION       = "sa_identity"
SA_ASSAY_CALLER_COLLECTION   = "sa_assay_caller"
DYES_COLLECTION              = "dyes"
DEVICES_COLLECTION           = "devices"
ARCHIVES_COLLECTION          = "archives"
PROBE_EXPERIMENTS_COLLECTION = "probe_experiments"
PROBE_METADATA_COLLECTION    = "probe_metadata"
IMAGES_COLLECTION            = "images_collection"