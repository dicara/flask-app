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

#=============================================================================
# Imports
#=============================================================================
from collections import OrderedDict

from src.apis.AbstractGetFunction import AbstractGetFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from src import VALIDATION_COLLECTION
from src.apis.ApiConstants import UUID, STATUS, ID, JOB_NAME, PROBES, \
    TARGETS, DATESTAMP, ABSORB, NUM

#=============================================================================
# Class
#=============================================================================
class ValidationGetFunction(AbstractGetFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Validation"
   
    @staticmethod
    def summary():
        return "Retrieve list of validation jobs."
    
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
        columns            = OrderedDict()
        columns[ID]        = 0
        columns[JOB_NAME]  = 1
        columns[UUID]      = 1
        columns[STATUS]    = 1
        columns[DATESTAMP] = 1
        columns[PROBES]    = 1
        columns[TARGETS]   = 1
        columns[ABSORB]    = 1
        columns[NUM]       = 1
        
        column_names = columns.keys()  
        column_names.remove(ID)         
        
        data = cls._DB_CONNECTOR.find(VALIDATION_COLLECTION, {}, columns)
         
        return (data, column_names, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ValidationGetFunction()
    print function