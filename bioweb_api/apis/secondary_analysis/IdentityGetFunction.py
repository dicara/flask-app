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
@date:   Feb 4, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from collections import OrderedDict

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import SA_IDENTITY_COLLECTION
from bioweb_api.apis.ApiConstants import UUID, JOB_NAME, STATUS, \
    ID, PICO2_DYE, ASSAY_DYE, JOB_TYPE_NAME, RESULT, CONFIG, \
    ERROR, PA_PROCESS_UUID, SUBMIT_DATESTAMP, NUM_PROBES, TRAINING_FACTOR, \
    START_DATESTAMP, PLOT, PLOT_URL, FINISH_DATESTAMP, URL, DYE_LEVELS, \
    IGNORED_DYES, UI_THRESHOLD, PLATE_PLOT_URL, USE_PICO1_FILTER, \
    REPORT_URL, REPORT, TEMPORAL_PLOT_URL, PICO1_DYE
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import IDENTITY

#=============================================================================
# Class
#=============================================================================
class IdentityGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return IDENTITY
   
    @staticmethod
    def summary():
        return "Retrieve list of secondary analysis identity jobs."
    
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
        columns                     = OrderedDict()
        columns[ID]                 = 0
        columns[JOB_NAME]           = 1
        columns[JOB_TYPE_NAME]      = 1
        columns[UUID]               = 1
        columns[PA_PROCESS_UUID]    = 1
        columns[USE_PICO1_FILTER]   = 1
        columns[PICO1_DYE]          = 1
        columns[PICO2_DYE]          = 1
        columns[ASSAY_DYE]          = 1
        columns[NUM_PROBES]         = 1
        columns[TRAINING_FACTOR]    = 1
        columns[DYE_LEVELS]         = 1
        columns[IGNORED_DYES]       = 1
        columns[UI_THRESHOLD]       = 1
        columns[STATUS]             = 1
        columns[SUBMIT_DATESTAMP]   = 1
        columns[START_DATESTAMP]    = 1
        columns[FINISH_DATESTAMP]   = 1
        columns[ERROR]              = 1
        columns[RESULT]             = 1
        columns[URL]                = 1
        columns[PLOT]               = 1
        columns[PLOT_URL]           = 1
        columns[PLATE_PLOT_URL]     = 1
        columns[TEMPORAL_PLOT_URL]  = 1
        columns[CONFIG]             = 1
        columns[REPORT_URL]         = 1
        columns[REPORT]             = 1

        column_names = columns.keys()  
        column_names.remove(ID)         
        
        data = cls._DB_CONNECTOR.find(SA_IDENTITY_COLLECTION, {}, columns)
         
        return (data, column_names, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = IdentityGetFunction()
    print function        
