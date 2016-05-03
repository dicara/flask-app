'''
Copyright 2016 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Yuewei Sheng
@date:   April 25th, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.ApiConstants import ID, ERROR, PA_DOCUMENT, ID_DOCUMENT, \
     AC_DOCUMENT, GT_DOCUMENT, MAJOR, MINOR, OFFSETS, ID_TRAINING_FACTOR, \
     PF_TRAINING_FACTOR, UI_THRESHOLD, AC_TRAINING_FACTOR, CTRL_THRESH, \
     REQUIRED_DROPS, ARCHIVE, DIFF_PARAMS, TRAINING_FACTOR

#=============================================================================
# Local static variables
#=============================================================================
PARAM_MAP = {MAJOR: PA_DOCUMENT, MINOR:PA_DOCUMENT, OFFSETS: PA_DOCUMENT,
             ID_TRAINING_FACTOR: ID_DOCUMENT, PF_TRAINING_FACTOR: ID_DOCUMENT,
             UI_THRESHOLD: ID_DOCUMENT, AC_TRAINING_FACTOR: AC_DOCUMENT,
             CTRL_THRESH: AC_DOCUMENT, REQUIRED_DROPS: GT_DOCUMENT}

DEFAULTS = {MAJOR:              2,
            MINOR:              0,
            OFFSETS:            30,
            ID_TRAINING_FACTOR: 1000,
            PF_TRAINING_FACTOR: 100,
            UI_THRESHOLD:       4000,
            AC_TRAINING_FACTOR: 100,
            CTRL_THRESH:        5,
            REQUIRED_DROPS:     0}

def convert_param_name(param):
    return TRAINING_FACTOR if param in [ID_TRAINING_FACTOR, AC_TRAINING_FACTOR] \
            else param

def update_fa_docs(documents):
    """
    Identity parameters in full analysis jobs that are different from default values
    """
    if not documents: return []
    for doc in documents:
        if ID in doc:
            del doc[ID]
        diff_params = dict()
        for param, doc_name in PARAM_MAP.items():
            if doc_name not in doc: continue
            param_name = convert_param_name(param)
            if param_name in doc[doc_name]:
                val = doc[doc_name][param_name]
                if val != DEFAULTS[param]:
                    diff_params[param] = val
                doc[DIFF_PARAMS] = diff_params

    return documents

def is_param_diff(doc, parameters):
    """
    Check whether the input parameters are different from those in specified doc
    of previous job
    @param doc:                 A job document, e.g., PA_DOCUMENT
    @param parameters:          New input parameters
    """
    for param in PARAM_MAP:
        if param in parameters:
            param_name = convert_param_name(param)
            if param_name in doc and parameters[param] != doc[param_name]:
                return True
    return False