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

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import PROBES_COLLECTION
from bioweb_api.apis.ApiConstants import FORMAT, FILENAME, FILEPATH, ID, URL, \
    DATESTAMP, TYPE, UUID

#=============================================================================
# Class
#=============================================================================
class ProbesGetFunction(AbstractGetFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Probes"
   
    @staticmethod
    def summary():
        return "Retrieve list of available probes files."
    
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
        columns[UUID]      = 1
        columns[FILENAME]  = 1
        columns[FILEPATH]  = 1
        columns[URL]       = 1
        columns[DATESTAMP] = 1
        columns[FORMAT]    = 1
        columns[TYPE]      = 1
        
        column_names = columns.keys()  
        column_names.remove(ID)         
        
        data = cls._DB_CONNECTOR.find(PROBES_COLLECTION, {}, columns)
         
        return (data, column_names, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbesGetFunction()
    print function