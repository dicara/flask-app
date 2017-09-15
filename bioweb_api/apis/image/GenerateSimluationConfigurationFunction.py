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
@date:   Mar 4, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory

from primary_analysis.experiment.experiment_definitions import ExperimentDefinitions
from primary_analysis.pa_utils import generate_simulation_config

#=============================================================================
# Public Static Variables
#=============================================================================

#=============================================================================
# Private Static Variables
#=============================================================================

#=============================================================================
# Class
#=============================================================================
class GenerateSimulationConfigurationFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "GenerateSimulationConfiguration"
   
    @staticmethod
    def summary():
        return "Generate an image simulation configuration file."
    
    @staticmethod
    def notes():
        return ""
    
    def response_messages(self):
        msgs = super(GenerateSimulationConfigurationFunction, self).response_messages()
        msgs.extend([
                     { "code": 404, 
                       "message": "Submission unsuccessful. No experiment " \
                       "definition found matching input criteria."},
                    ])
    
    @classmethod
    def parameters(cls):
        cls._exp_defs_param   = ParameterFactory.experiment_definition()

        parameters = [
                      cls._exp_defs_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        exp_def_name = params_dict[cls._exp_defs_param][0]
        
        try:
            exp_defs         = ExperimentDefinitions()
            exp_def_uuid     = exp_defs.get_experiment_uuid(exp_def_name)
            generate_simulation_config(exp_def, config_path)
            if not exp_def_uuid:
                http_status_code = 404
                json_response[ERROR] = "Couldn't locate UUID for " \
                    "experiment definition."
            else:
        

        