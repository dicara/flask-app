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
@date:   Apr 11, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.ApiConstants import ID, RUN_REPORT
from bioweb_api.apis.run_info.RunInfoUtils import get_run_reports, update_run_reports

#=============================================================================
# Class
#=============================================================================
class RunInfoGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return RUN_REPORT

    @staticmethod
    def summary():
        return "Retrieve list of run reports."

    @staticmethod
    def notes():
        return "Returns a list of instrumental run reports that exist in " \
            "the run report datastore."

    @classmethod
    def parameters(cls):
        cls.refresh_parameter = ParameterFactory.boolean("refresh",
                                                         "Refresh available " \
                                                         "run reports.",
                                                         default_value=False)
        cls.cart_sn_parameter = ParameterFactory.cartridge_sn()
        parameters = [
                      cls.cart_sn_parameter,
                      cls.refresh_parameter,
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        if cls.refresh_parameter in params_dict and \
           params_dict[cls.refresh_parameter][0]:
            update_run_reports()

        if cls.cart_sn_parameter in params_dict and \
            params_dict[cls.cart_sn_parameter][0]:
            return get_run_reports(params_dict[cls.cart_sn_parameter][0])
        else:
            return get_run_reports()

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = RunInfoGetFunction()
    print function
