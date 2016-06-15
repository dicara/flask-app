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

@author: Yuewei Sheng
@date:   June 14, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.full_analysis.FullAnalysisUtils import get_variants

#=============================================================================
# Public Static Variables
#=============================================================================
VARIANTS = "Variants"

#=============================================================================
# Class
#=============================================================================
class VariantsGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return VARIANTS

    @staticmethod
    def summary():
        return "Retrieve list of variants from experiment definition."

    @staticmethod
    def notes():
        return "Returns a list of the name, location and nucleic acid variation of \
                variants that exist in the experiment definition."

    @classmethod
    def parameters(cls):
        cls.exp_def_param = ParameterFactory.experiment_definition()

        parameters = [
                      cls.exp_def_param,
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        variants = [ {"variant": a} for a in get_variants(params_dict[cls.exp_def_param][0]) ]
        return (variants, None, None)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = VariantsGetFunction()
    print function
