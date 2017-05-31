'''
Copyright 2017 Bio-Rad Laboratories, Inc.

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
@date:   Feb 17, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import AC_METHOD, AC_METHOD_DESCRIPTION
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import ASSAY_CALLER

from secondary_analysis.assay_calling.classifier_utils import available_models

#=============================================================================
# Public Variables
#=============================================================================
MODELS = 'models'

#=============================================================================
# Class
#=============================================================================
class AssayCallerModelGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return ASSAY_CALLER + '/' + MODELS

    @staticmethod
    def summary():
        return "Retrieve list of assay caller submodel names."

    @staticmethod
    def notes():
        return ""

    @classmethod
    def parameters(cls):
        cls.ac_method = ParameterFactory.ac_method(AC_METHOD, AC_METHOD_DESCRIPTION)
        parameters = [
                      cls.ac_method,
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        ac_method = params_dict[cls.ac_method][0]
        model_file_dict = available_models(ac_method)

        return (sorted(model_file_dict.keys()), None, None)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = AssayCallerModelGetFunction()
    print function
