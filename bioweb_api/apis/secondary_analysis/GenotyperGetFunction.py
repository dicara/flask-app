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

@author: Dan DiCara
@date:   Feb 17, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from collections import OrderedDict

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import SA_GENOTYPER_COLLECTION
from bioweb_api.apis.ApiConstants import UUID, JOB_NAME, STATUS, ID, \
    JOB_TYPE_NAME, RESULT, ERROR, SUBMIT_DATESTAMP, START_DATESTAMP, \
    FINISH_DATESTAMP, URL, REQUIRED_DROPS, SA_ASSAY_CALLER_UUID, EXP_DEF_NAME, \
    EXP_DEF_UUID, PDF, PDF_URL, PNG, PNG_URL, PNG_SUM, PNG_SUM_URL
from bioweb_api.apis.secondary_analysis.GenotyperPostFunction import GENOTYPER

#=============================================================================
# Class
#=============================================================================
class GenotyperGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return GENOTYPER
   
    @staticmethod
    def summary():
        return "Retrieve list of secondary analysis genotyper jobs."
    
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
        columns                       = OrderedDict()
        columns[ID]                   = 0
        columns[JOB_NAME]             = 1
        columns[JOB_TYPE_NAME]        = 1
        columns[UUID]                 = 1
        columns[EXP_DEF_NAME]         = 1
        columns[EXP_DEF_UUID]         = 1
        columns[REQUIRED_DROPS]       = 1
        columns[SA_ASSAY_CALLER_UUID] = 1
        columns[STATUS]               = 1
        columns[SUBMIT_DATESTAMP]     = 1
        columns[START_DATESTAMP]      = 1
        columns[FINISH_DATESTAMP]     = 1
        columns[ERROR]                = 1
        columns[RESULT]               = 1
        columns[PDF]                  = 1
        columns[PDF_URL]              = 1
        columns[PNG]                  = 1
        columns[PNG_URL]              = 1
        columns[PNG_SUM]              = 1
        columns[PNG_SUM_URL]          = 1
        columns[URL]                  = 1

        column_names = columns.keys()  
        column_names.remove(ID)         
        
        data = cls._DB_CONNECTOR.find(SA_GENOTYPER_COLLECTION, {}, columns)
         
        return (data, column_names, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = GenotyperGetFunction()
    print function            