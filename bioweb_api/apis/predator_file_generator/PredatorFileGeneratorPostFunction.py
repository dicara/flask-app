'''
Copyright 2017 Bio-Rad Laboratories, Inc.

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
@date:   Feb 8, 2017
'''

#=============================================================================
# Imports
#=============================================================================
import os
import sys
import tempfile
import traceback

from datetime import datetime
import numpy

from bioweb_api import RESULTS_PATH, HOSTNAME, PORT, HOME_DIR
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import ERROR, DATESTAMP, MIX_VOL, \
    TOTAL_VOL, NBARCODES
from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from predator.barcode import BarcodeGenerator
from predator.dye import DyeStockLibraryGenerator
from predator.csvgenerator import CsvGenerator
from predator.predatorplate import PredatorPlateGenerator


#=============================================================================
# Public Static Variables
#=============================================================================
GENERATE_SCRIPTS = 'GenerateScripts'

#=============================================================================
# Class
#=============================================================================
class PredatorFileGeneratorPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return GENERATE_SCRIPTS
   
    @staticmethod
    def summary():
        return 'Test a set of simulated data for cluster collisions'
    
    @staticmethod
    def notes():
        return ''
    
    @classmethod
    def parameters(cls):
        cls._design_param = ParameterFactory.design('Library design data.',
                                                          required=True)
        cls._mix_volume_param = ParameterFactory.float(MIX_VOL,
                                                'Float specifying the mix volume in ul',
                                                default=0.0,
                                                required=False)
        cls._total_volume_param = ParameterFactory.float(TOTAL_VOL,
                                                'Float specifying total volume in ul',
                                                default=0.0,
                                                required=False)
        cls._nbarcodes_param = ParameterFactory.integer(NBARCODES,
                                                'Integer specifying the number of barcodes to generate',
                                                required=True)

        parameters = [
                      cls._design_param,
                      cls._mix_volume_param,
                      cls._total_volume_param,
                      cls._nbarcodes_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):

        design_data      = params_dict[cls._design_param]
        mix_vol          = params_dict[cls._mix_volume_param][0]
        total_vol        = params_dict[cls._total_volume_param][0]
        nbarcodes        = params_dict[cls._nbarcodes_param][0]
        json_response    = {
                            DATESTAMP: datetime.today(),
                           }
        http_status_code = 200

        def parse_design(design_data):
            design_dict = dict()
            for dye in design_data:
                dye_data = dye.split(':')
                name = dye_data[0]
                lot = dye_data[1]
                potency = float(dye_data[2])
                intensities = map(int, dye_data[3:])
                design_dict[name] = {'lot_number': lot, 'levels': [i/potency for i in intensities]}
            return design_dict

        try:
            design = parse_design(design_data)

            requested_nbarcodes = numpy.product([len(design[dye]['levels']) for dye in design])
            if nbarcodes != requested_nbarcodes:
                raise Exception('Requested number of barcodes: %d does not match specified number: %d'
                                % (requested_nbarcodes, nbarcodes))

            bg = BarcodeGenerator.from_design(design)
            barcodes = bg.generate()

            # determine the dye stocks needed based on the dyes in the library
            dslg = DyeStockLibraryGenerator(mix_vol, total_vol, barcodes)
            ds_lib = dslg.generate()

            # convert the library to a list of predator plate objects
            ppg = PredatorPlateGenerator(mix_vol, total_vol, barcodes, ds_lib)
            pplates = ppg.generate()

            # convert the information in the predator plates into csv files
            cg = CsvGenerator(ds_lib, pplates)
            predator_files_dir_path = os.path.join(RESULTS_PATH, 'predator_files')
            if not os.path.exists(predator_files_dir_path):
                os.makedirs(predator_files_dir_path)
            output_dir_path = tempfile.mkdtemp(dir=predator_files_dir_path, prefix='predator_files')
            output_zip_file_path = cg.generate(output_path=output_dir_path)
            rel_path = os.path.relpath(output_zip_file_path, HOME_DIR)

            json_response['predator_files_url'] = "http://%s/%s" % (HOSTNAME, rel_path)

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
    function = PredatorFileGeneratorPostFunction()
    print function        