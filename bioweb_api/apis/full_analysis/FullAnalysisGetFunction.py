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

@author: Nathan Brown
@date:   March 28, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.full_analysis.FullAnalysisPostFunction import FULL_ANALYSIS
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import FA_PROCESS_COLLECTION
from bioweb_api.apis.ApiConstants import ID, ERROR

#=============================================================================
# Class
#=============================================================================
class FullAnalysisGetFunction(AbstractGetFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return FULL_ANALYSIS
   
    @staticmethod
    def summary():
        return "Retrieve list of full analysis jobs."
    
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
        fa_documents = cls._DB_CONNECTOR.find(FA_PROCESS_COLLECTION, {})
        for doc in fa_documents:
            if ID in doc:
                del doc[ID]

        if fa_documents:
            column_names = fa_documents[0].keys()
        else:
            column_names = ['']
         
        return (fa_documents, column_names, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = FullAnalysisGetFunction()
    print function