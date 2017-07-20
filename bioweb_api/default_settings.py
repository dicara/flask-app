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
# Platform-Dependent Configuration Settings
#===============================================================================
HOSTNAME                = "localhost"
PORT                    = 8020
DATABASE_NAME           = "Bioinformatics_dev"
DATABASE_URL            = HOSTNAME
HOME_DIR                = os.path.join(expanduser("~"), "gnubio-bioinformatics-rest_api")
TARGETS_UPLOAD_PATH     = os.path.join(HOME_DIR, "uploads", str(PORT), "targets")
PROBES_UPLOAD_PATH      = os.path.join(HOME_DIR, "uploads", str(PORT), "probes")
PLATES_UPLOAD_PATH      = os.path.join(HOME_DIR, "uploads", str(PORT), "plates")
RESULTS_PATH            = os.path.join(HOME_DIR, "results", str(PORT))
REFS_PATH               = os.path.join(HOME_DIR, "refs")
TMP_PATH                = os.path.join(HOME_DIR, "tmp")
TORNADO_LOG_FILE_PREFIX = os.path.join(HOME_DIR, "logs/tornado_%s.log" % str(PORT))
MAX_WORKERS             = 6

#===============================================================================
# Platform-Independent Configuration Settings
#===============================================================================
ARCHIVES_PATH           = "/mnt/runs"
RUN_REPORT_PATH         = "/mnt/runs/run_reports"
MODIFIED_ARCHIVES_PATH  = "/mnt/runs/run_analysis/modifiedH5"
DATABASE_PORT           = 27017             # the Mongo port is well-known and pretty much constant
MAX_BUFFER_SIZE         = 2*1024*1024*1024  # Max file upload size: 2GB

ALTERNATE_ARCHIVES_PATH = ["/mnt/old-data"]

# MongoDb Collections
TARGETS_COLLECTION           = "targets"
PROBES_COLLECTION            = "probes"
PLATES_COLLECTION            = "plates"
VALIDATION_COLLECTION        = "validation"
ABSORPTION_COLLECTION        = "absorption"
PA_PROCESS_COLLECTION        = "pa_process"
FA_PROCESS_COLLECTION        = "fa_process"
PA_PLOTS_COLLECTION          = "pa_plots"
PA_CONVERT_IMAGES_COLLECTION = "pa_convert_images"
SA_IDENTITY_COLLECTION       = "sa_identity"
SA_ASSAY_CALLER_COLLECTION   = "sa_assay_caller"
SA_GENOTYPER_COLLECTION      = "sa_genotyper"
DYES_COLLECTION              = "dyes"
DEVICES_COLLECTION           = "devices"
ARCHIVES_COLLECTION          = "archives"
HDF5_COLLECTION              = "HDF5s"
PROBE_EXPERIMENTS_COLLECTION = "probe_experiments"
PROBE_METADATA_COLLECTION    = "probe_metadata"
IMAGES_COLLECTION            = "images_collection"
RUN_REPORT_COLLECTION        = "run_reports"
EXP_DEF_COLLECTION           = "exp_def"
SA_EXPLORATORY_COLLECTION    = "sa_exploratory"
