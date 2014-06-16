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
import os

from src.apis.AbstractFunction import AbstractFunction
from src.apis.ApiConstants import METHODS
from src import PROBES_UPLOAD_FOLDER

#=============================================================================
# Class
#=============================================================================
class ProbesGet(AbstractFunction):
    
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
    
    @staticmethod
    def method():
        return METHODS.GET                                  # @UndefinedVariable
    
    @classmethod
    def parameters(cls):
        parameters = [
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        return (os.listdir(PROBES_UPLOAD_FOLDER), None, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbesGet()
    print function