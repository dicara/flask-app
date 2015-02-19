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
@date:   Feb 18, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.primary_analysis.PrimaryAnalysisUtils import get_applications
from bioweb_api.apis.ApiConstants import APPLICATION

#=============================================================================
# Class
#=============================================================================
class ApplicationGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Applications"
   
    @staticmethod
    def summary():
        return "Retrieve list of available probe experiment design applications."
    
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
        applications = [{APPLICATION: app} for app in get_applications()]
        return (applications, None, None)
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ApplicationGetFunction()
    print function