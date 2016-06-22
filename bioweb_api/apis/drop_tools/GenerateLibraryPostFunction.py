'''
Copyright 2015 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Nathan Brown
@date:   May 22, 2015
'''

#=============================================================================
# Imports
#=============================================================================

import sys
import traceback

from datetime import datetime

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import ERROR, DATESTAMP, NBARCODES
from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.apis.drop_tools.library_generation_utilities import LibraryDesign

from bioweb_api.utilities.logging_utilities import APP_LOGGER

#=============================================================================
# Public Static Variables
#=============================================================================
GENERATE_LIBRARY = 'GenerateLibrary'

#=============================================================================
# Class
#=============================================================================
class GenerateLibraryPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return GENERATE_LIBRARY
   
    @staticmethod
    def summary():
        return 'Test a set of simulated data for cluster collisions'
    
    @staticmethod
    def notes():
        return ''
    
    @classmethod
    def parameters(cls):
        cls._dyes_lots_param = ParameterFactory.dyes_lots()
        cls._nbarcodes_param = ParameterFactory.integer(NBARCODES,
                                                'Integer specifying the number of barcodes to generate',
                                                required=True)

        parameters = [
                      cls._dyes_lots_param,
                      cls._nbarcodes_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):

        dyes             = params_dict[cls._dyes_param]
        nbarcodes        = params_dict[cls._nbarcodes_param][0]
        http_status_code = 200
        json_response    = {
                            DATESTAMP: datetime.today(),
                           }
        try:
            ld = LibraryDesign(dyes, nbarcodes)
            design, dyes, levels = ld.generate()

            json_response[NBARCODES]    = nbarcodes
            json_response['design']     = design
            json_response['dyes']       = dyes
            json_response['levels']     = levels

        except IOError:
            APP_LOGGER.exception(traceback.format_exc())
            http_status_code     = 415
            json_response[ERROR] = str(sys.exc_info()[1])
        except:
            APP_LOGGER.exception(traceback.format_exc())
            http_status_code     = 500
            json_response[ERROR] = str(sys.exc_info()[1])

        return make_clean_response(json_response, http_status_code)
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == '__main__':
    function = GenerateLibraryPostFunction()
    print function        