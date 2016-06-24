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

import os
import sys
import tempfile
import traceback

from datetime import datetime

from bioweb_api import TMP_PATH, HOSTNAME, PORT
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import ERROR, DATESTAMP, NBARCODES, MIX_VOL, TOTAL_VOL
from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.drop_tools.library_generation_utilities import LibraryDesign
from predator.barcode import BarcodeGenerator
from predator.dye import DyeStockLibraryGenerator
from predator.csvgenerator import CsvGenerator
from predator.predatorplate import PredatorPlateGenerator


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
        cls._mix_volume_param = ParameterFactory.float(MIX_VOL,
                                                'Float specifying the mix volume in ul',
                                                default=0.0,
                                                required=False)
        cls._total_volume_param = ParameterFactory.float(TOTAL_VOL,
                                                'Float specifying total volume in ul',
                                                default=0.0,
                                                required=False)

        parameters = [
                      cls._dyes_lots_param,
                      cls._nbarcodes_param,
                      cls._mix_volume_param,
                      cls._total_volume_param
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):

        dyes_lots        = params_dict[cls._dyes_lots_param]
        nbarcodes        = params_dict[cls._nbarcodes_param][0]
        mix_vol          = params_dict[cls._mix_volume_param][0]
        total_vol        = params_dict[cls._total_volume_param][0]
        http_status_code = 200
        json_response    = {
                            DATESTAMP: datetime.today(),
                           }

        try:
            ld = LibraryDesign(dyes_lots, nbarcodes)
            design, dye_names, levels = ld.generate()

            if mix_vol > 0.0 and total_vol > 0.0:
                bg = BarcodeGenerator.from_design({'barcode': design}, fiducial=False)
                barcodes = bg.generate()

                # determine the dye stocks needed based on the dyes in the library
                dslg = DyeStockLibraryGenerator(mix_vol, total_vol, barcodes)
                ds_lib = dslg.generate()

                # convert the library to a list of predator plate objects
                ppg = PredatorPlateGenerator(mix_vol, total_vol, barcodes, ds_lib)
                pplates = ppg.generate()

                # convert the information in the predator plates into csv files
                cg = CsvGenerator(ds_lib, pplates)
                output_dir_path = tempfile.mkdtemp(dir=TMP_PATH, prefix='predator_files')
                output_zip_path = cg.generate(output_path=output_dir_path)
                json_response['predator_files_url'] = "http://%s/tmp/%s" % \
                    (HOSTNAME, os.path.basename(output_zip_path))

            json_response[NBARCODES] = nbarcodes
            json_response['design']  = design
            json_response['dyes']    = dye_names
            json_response['levels']  = levels

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