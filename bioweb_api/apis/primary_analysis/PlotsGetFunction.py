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
@date:   Jan 28, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from collections import OrderedDict

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import PA_PLOTS_COLLECTION
from bioweb_api.apis.ApiConstants import UUID, STATUS, ID, JOB_TYPE_NAME, \
    SUBMIT_DATESTAMP, START_DATESTAMP, FINISH_DATESTAMP, ERROR, PLOT, \
    PLOT_URL, PA_PROCESS_UUID

#=============================================================================
# Class
#=============================================================================
class PlotsGetFunction(AbstractGetFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Plots"
   
    @staticmethod
    def summary():
        return "Retrieve list of primary analysis plots jobs."
    
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
        columns[JOB_TYPE_NAME]    = 1
        columns[UUID]             = 1
        columns[PA_PROCESS_UUID]  = 1
        columns[STATUS]           = 1
        columns[SUBMIT_DATESTAMP] = 1
        columns[START_DATESTAMP]  = 1
        columns[FINISH_DATESTAMP] = 1
        columns[ERROR]            = 1
        columns[PLOT]             = 1
        columns[PLOT_URL]         = 1
        
        column_names = columns.keys()  
        column_names.remove(ID)         
        
        data = cls._DB_CONNECTOR.find(PA_PLOTS_COLLECTION, {}, columns)
         
        return (data, column_names, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = PlotsGetFunction()
    print function