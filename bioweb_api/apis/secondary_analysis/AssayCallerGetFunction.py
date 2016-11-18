'''
Copyright 2015 Bio-Rad Laboratories, Inc.

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
@date:   Feb 17, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from collections import OrderedDict

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import SA_ASSAY_CALLER_COLLECTION
from bioweb_api.apis.ApiConstants import UUID, JOB_NAME, STATUS, \
    ID, FIDUCIAL_DYE, ASSAY_DYE, JOB_TYPE_NAME, RESULT, \
    ERROR, SA_IDENTITY_UUID, SUBMIT_DATESTAMP, NUM_PROBES, TRAINING_FACTOR, \
    START_DATESTAMP, SCATTER_PLOT, SCATTER_PLOT_URL, AC_MODEL, \
    FINISH_DATESTAMP, URL, EXP_DEF_NAME, EXP_DEF_UUID, CTRL_THRESH
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import ASSAY_CALLER

#=============================================================================
# Class
#=============================================================================
class AssayCallerGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return ASSAY_CALLER

    @staticmethod
    def summary():
        return "Retrieve list of secondary analysis assay caller jobs."

    @staticmethod
    def notes():
        return ""

    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        columns                   = OrderedDict()
        columns[ID]               = 0
        columns[JOB_NAME]         = 1
        columns[JOB_TYPE_NAME]    = 1
        columns[UUID]             = 1
        columns[EXP_DEF_NAME]     = 1
        columns[EXP_DEF_UUID]     = 1
        columns[SA_IDENTITY_UUID] = 1
        columns[FIDUCIAL_DYE]     = 1
        columns[ASSAY_DYE]        = 1
        columns[NUM_PROBES]       = 1
        columns[TRAINING_FACTOR]  = 1
        columns[CTRL_THRESH]      = 1
        columns[STATUS]           = 1
        columns[SUBMIT_DATESTAMP] = 1
        columns[START_DATESTAMP]  = 1
        columns[FINISH_DATESTAMP] = 1
        columns[ERROR]            = 1
        columns[RESULT]           = 1
        columns[URL]              = 1
        columns[SCATTER_PLOT]     = 1
        columns[SCATTER_PLOT_URL] = 1
        columns[AC_MODEL]         = 1

        column_names = columns.keys()
        column_names.remove(ID)

        data = cls._DB_CONNECTOR.find(SA_ASSAY_CALLER_COLLECTION, {}, columns)

        return (data, column_names, None)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = AssayCallerGetFunction()
    print function
