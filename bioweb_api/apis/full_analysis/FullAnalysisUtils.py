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
from random import choice
from string import ascii_letters

from bioweb_api.apis.ApiConstants import ID, PA_DOCUMENT, ID_DOCUMENT, \
     AC_DOCUMENT, GT_DOCUMENT, OFFSETS, ID_TRAINING_FACTOR, \
     PF_TRAINING_FACTOR, UI_THRESHOLD, AC_TRAINING_FACTOR, CTRL_THRESH, \
     REQUIRED_DROPS, DIFF_PARAMS, TRAINING_FACTOR
from primary_analysis.dye_model import DEFAULT_OFFSETS
from secondary_analysis.constants import PICOINJECTION_TRAINING_FACTOR as DEFAULT_PF_TRAINING_FACTOR
from secondary_analysis.constants import ID_TRAINING_FACTOR_MAX as DEFAULT_ID_TRAINING_FACTOR
from secondary_analysis.constants import AC_TRAINING_FACTOR as DEFAULT_AC_TRAINING_FACTOR
from secondary_analysis.constants import UNINJECTED_THRESHOLD as DEFAULT_UNINJECTED_THRESHOLD
from secondary_analysis.constants import AC_CTRL_THRESHOLD as DEFAULT_AC_CTRL_THRESHOLD

#=============================================================================
# Local static variables
#=============================================================================
PARAM_MAP = {OFFSETS:               PA_DOCUMENT,
             ID_TRAINING_FACTOR:    ID_DOCUMENT,
             PF_TRAINING_FACTOR:    ID_DOCUMENT,
             UI_THRESHOLD:          ID_DOCUMENT,
             AC_TRAINING_FACTOR:    AC_DOCUMENT,
             CTRL_THRESH:           AC_DOCUMENT,
             REQUIRED_DROPS:        GT_DOCUMENT}

DEFAULTS = {OFFSETS:            abs(DEFAULT_OFFSETS[0]),
            ID_TRAINING_FACTOR: DEFAULT_ID_TRAINING_FACTOR,
            PF_TRAINING_FACTOR: DEFAULT_PF_TRAINING_FACTOR,
            UI_THRESHOLD:       DEFAULT_UNINJECTED_THRESHOLD,
            AC_TRAINING_FACTOR: DEFAULT_AC_TRAINING_FACTOR,
            CTRL_THRESH:        DEFAULT_AC_CTRL_THRESHOLD,
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

def is_param_diff(doc, doc_name, parameters):
    """
    Check whether the input parameters are different from those in specified doc
    of previous job
    @param doc:                 A job document
    @param doc_name:            Document type of a job document, e.g., PA_DOCUMENT
    @param parameters:          New input parameters
    """
    for param in PARAM_MAP:
        if param in parameters:
            if PARAM_MAP[param] != doc_name: continue
            param_name = convert_param_name(param)
            if param_name in doc and parameters[param] != doc[param_name]:
                return True
    return False

generate_random_str = lambda length : ''.join(choice(ascii_letters) for _ in xrange(length))
