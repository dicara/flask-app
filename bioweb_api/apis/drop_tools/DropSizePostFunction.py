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

from datetime import datetime
import numpy
from uuid import uuid4

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import ERROR, DATESTAMP, UUID, DROP_AVE_DIAMETER, \
    DROP_STD_DIAMETER, DYE_METRICS
from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.apis.drop_tools.DropSizeIntensityConverter import make_centroids, \
    make_clusters, check_collision


#=============================================================================
# Public Static Variables
#=============================================================================
DROP_SIZE = 'DropSize'

#=============================================================================
# Class
#=============================================================================
class DropSizePostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return DROP_SIZE
   
    @staticmethod
    def summary():
        return 'Test a set of simulated data for cluster collisions'
    
    @staticmethod
    def notes():
        return ''

    def response_messages(self):
        msgs = super(DropSizePostFunction, self).response_messages()
        return msgs
    
    @classmethod
    def parameters(cls):
        cls._dyes_metrics      = ParameterFactory.dye_metrics()
        cls._drop_ave_diameter = ParameterFactory.float(DROP_AVE_DIAMETER,
                                                        'Float specifying average drop diameter',
                                                        required=True)
        cls._drop_std_diameter = ParameterFactory.float(DROP_STD_DIAMETER,
                                                        'Float specifying drop diameter standard deviation',
                                                        required=True)

        parameters = [
                      cls._drop_ave_diameter,
                      cls._dyes_metrics,
                      cls._drop_std_diameter
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):

        dye_metrics      = params_dict[cls._dyes_metrics]
        drop_ave         = params_dict[cls._drop_ave_diameter][0]
        drop_std         = params_dict[cls._drop_std_diameter][0]
        http_status_code = 200
        uuid             = str(uuid4())
        json_response    = {
                            UUID: uuid,
                            DATESTAMP: datetime.today(),
                           }
        try:
            dye_names = list()
            nlvls = list()
            intensities = list()
            for dye_name, nlvl, low, high in dye_metrics:
                dye_names.append(dye_name)
                nlvls.append(nlvl)
                intensities.append((low, high))

            centroids = make_centroids(nlvls, intensities)
            clusters = make_clusters(centroids, drop_ave=drop_ave, drop_std=drop_std)
            collisions = check_collision(clusters)

            json_response[DROP_AVE_DIAMETER]     = drop_ave
            json_response[DROP_STD_DIAMETER]     = drop_std
            json_response[DYE_METRICS]  = map(list, dye_metrics)
            json_response['collisions'] = collisions
            json_response['nclusters']  = numpy.product(nlvls)

        except IOError:
            http_status_code     = 415
            json_response[ERROR] = str(sys.exc_info()[1])
        except:
            http_status_code     = 500
            json_response[ERROR] = str(sys.exc_info()[1])

        return make_clean_response(json_response, http_status_code)
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == '__main__':
    function = DropSizePostFunction()
    print function        