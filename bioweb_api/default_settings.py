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

#===============================================================================
# Platform-Specific Configuration Settings
#
# Select VAGRANT, DEV, or PROD:
#     --  a Vagrant VM running Ubuntu 12.04
#     --  DEV on the bioweb server
#     --  PROD on the bioweb server
#
# DEV and PROD share everything but:
#
#     --  DB name, as Bioinformatics_dev or Bioinformatics
#     --  the port value, 8010 or 8020
#
#===============================================================================

PLATFORM = "VAGRANT"

if PLATFORM == "VAGRANT":

    # Database server settings
    HOSTNAME        = "192.168.33.11"  
    PORT            = 8020
    DATABASE_NAME   = "Bioinformatics_dev"
    # File storage locations for pa, sa jobs
    ROOT_DIR        = "/vagrant/mnt/"
    ARCHIVES_PATH   = "/vagrant/mnt/runs"
    # Data Directories
    HOME_DIR = os.path.join(ROOT_DIR, "gnubio-bioinformatics-rest_api")

elif PLATFORM == "DEV":

    # Database server settings
    HOSTNAME        = "bioweb"
    PORT            = 8020
    DATABASE_NAME   = "Bioinformatics_dev"
    # File storage locations for pa, sa jobs
    ROOT_DIR        = "/mnt/bigdisk/"
    ARCHIVES_PATH   = "/mnt/runs"
    # Data Directories
    HOME_DIR = os.path.join(ROOT_DIR, "api")

elif PLATFORM == "PROD":

    # Database server settings
    HOSTNAME        = "bioweb"
    PORT            = 8010
    DATABASE_NAME   = "Bioinformatics"
    # File storage locations for pa, sa jobs
    ROOT_DIR        = "/mnt/bigdisk/"
    ARCHIVES_PATH   = "/mnt/runs"
    # Data Directories
    HOME_DIR = os.path.join(ROOT_DIR, "api")

else:
    raise Exception("Unknown execution platform '%s' - get help!" % PLATFORM)
    
#===============================================================================
# Platform-Independent Configuration Settings
#===============================================================================

DATABASE_URL            = HOSTNAME
DATABASE_PORT           = 27017    # the Mongo port is well-known and pretty much constant

MAX_BUFFER_SIZE         = 2*1024*1024*1024 # Max file upload size: 2GB

TARGETS_UPLOAD_PATH     = os.path.join(HOME_DIR, "uploads", str(PORT), "targets")
PROBES_UPLOAD_PATH      = os.path.join(HOME_DIR, "uploads", str(PORT), "probes")
PLATES_UPLOAD_PATH      = os.path.join(HOME_DIR, "uploads", str(PORT), "plates")
RESULTS_PATH            = os.path.join(HOME_DIR, "results", str(PORT))
REFS_PATH               = os.path.join(HOME_DIR, "refs")
TMP_PATH                = os.path.join(HOME_DIR, "tmp")

TORNADO_LOG_FILE_PREFIX = os.path.join(HOME_DIR, "logs/tornado_%s.log" % str(PORT))

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
