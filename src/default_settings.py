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
# Configuration Settings
#===============================================================================
DEV      = True
HOSTNAME = "localhost"
# HOSTNAME = "bioweb"

if DEV:
    PORT = 8020
else:
    PORT = 8010
    
if HOSTNAME == "localhost":
#     HOME_DIR = "/Users/dandicara/Documents/flask_api"
    HOME_DIR = "/home/ddicara/Documents/flask_api"
else:
    HOME_DIR = "/home/ddicara/gnubio-bioinformatics-rest_api"
    
TARGETS_UPLOAD_FOLDER   = os.path.join(HOME_DIR, "uploads", str(PORT), "targets")
PROBES_UPLOAD_FOLDER    = os.path.join(HOME_DIR, "uploads", str(PORT), "probes")
TORNADO_LOG_FILE_PREFIX = os.path.join(HOME_DIR, "logs/tornado_%s.log" % 
                                       str(PORT))