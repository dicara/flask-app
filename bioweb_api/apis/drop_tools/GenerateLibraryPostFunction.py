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

from bioweb_api import HOSTNAME, PORT
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import ERROR, DATESTAMP, NBARCODES, MIX_VOL, \
    TOTAL_VOL, DESIGN, NDYES, PICO1_DYE
from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.drop_tools.library_generation_utilities import LibraryDesign


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
        cls._ndyes_param = ParameterFactory.integer(NDYES, 'Number of dyes to use for design.')
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
        cls._pico1_dye_param = ParameterFactory.cs_string(PICO1_DYE,
                                                          'Picoinjection 1 dye',
                                                          required=False)
        parameters = [
                      cls._dyes_lots_param,
                      cls._ndyes_param,
                      cls._nbarcodes_param,
                      cls._mix_volume_param,
                      cls._total_volume_param,
                      cls._pico1_dye_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):

        def make_predator_url(design, _args):
            url = 'http://%s:%d/api/v1/PredatorFileGenerator/GenerateScripts?' % (HOSTNAME, PORT)
            # make design argument
            design_arg = list()
            for dye in design['barcode_dyes']:
                potency = str(design['barcode_dyes'][dye]['potency'])
                lot = str(design['barcode_dyes'][dye]['lot_number'])
                intensities = map(str, design['barcode_dyes'][dye]['intensities'])
                design_arg.append(':'.join([dye, lot, potency] + intensities))

            _args[DESIGN] = ','.join(design_arg)
            return url + '&'.join('='.join(i) for i in _args.items())

        def parse_dye_lots(dyes_lots_data):
            dye_lot_nlvls = list()
            for dl in dyes_lots_data:
                dl_data = dl.split(':')
                name = dl_data[0]
                lot = dl_data[1]
                # user may not have specified number of levels
                try:
                    nlvls = int(dl_data[2])
                except:
                    nlvls = None
                dye_lot_nlvls.append((name, lot, nlvls,))

            return dye_lot_nlvls

        requested_ndyes = None
        if cls._ndyes_param in params_dict:
            requested_ndyes = params_dict[cls._ndyes_param][0]

        dyes_lots = parse_dye_lots(params_dict[cls._dyes_lots_param])
        nbarcodes = params_dict[cls._nbarcodes_param][0]
        mix_vol = params_dict[cls._mix_volume_param][0]
        total_vol = params_dict[cls._total_volume_param][0]
        pico1_dye=None
        if cls._pico1_dye_param in params_dict:
            pico1_dye = params_dict[cls._pico1_dye_param][0]

        http_status_code = 200
        json_response    = {DATESTAMP: datetime.today()}

        try:
            ld = LibraryDesign(requested_dye_lots=dyes_lots, requested_nbarcodes=nbarcodes,
                               requested_ndyes=requested_ndyes, pico1_dye=pico1_dye)
            designs = ld.generate()

            if designs:
                if mix_vol > 0.0 and total_vol > 0.0:
                    for design in designs:
                        other_args = {MIX_VOL: str(mix_vol), TOTAL_VOL: str(total_vol), NBARCODES: str(nbarcodes)}
                        design['mix_vol'] = mix_vol
                        design['total_vol'] = total_vol
                        design['nbarcodes'] = nbarcodes
                        design['predator_url'] = make_predator_url(design, other_args)

                json_response['designs'] = designs
            else:
                json_response[ERROR] = 'Unable to generate design.'

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