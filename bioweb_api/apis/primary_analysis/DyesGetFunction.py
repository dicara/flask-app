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
@date:   Jul 23, 2014
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.primary_analysis.PrimaryAnalysisUtils import get_dyes, update_dyes

#=============================================================================
# Class
#=============================================================================
class DyesGetFunction(AbstractGetFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Dyes"
   
    @staticmethod
    def summary():
        return "Retrieve list of available dyes."
    
    @staticmethod
    def notes():
        return "Returns information about dyes in the dye profile datastore."
    
    @classmethod
    def parameters(cls):
        cls.refresh_parameter = ParameterFactory.boolean("refresh", 
                                                         "Refresh available dyes.",
                                                         default_value=False)
        parameters = [
                      cls.refresh_parameter,
                      ParameterFactory.format(),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        if cls.refresh_parameter in params_dict and \
           params_dict[cls.refresh_parameter][0]:
            update_dyes()
            
        dyes = [{"dye": dye} for dye in get_dyes()]
        return (dyes, None, None)
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = DyesGetFunction()
    print function