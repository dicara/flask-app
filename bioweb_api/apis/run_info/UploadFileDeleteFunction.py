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

@author: Yuewei Sheng
@date:   April 5th, 2017
'''

#=============================================================================
# Imports
#=============================================================================
import os
import sys
import traceback

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.ApiConstants import UPLOAD_FILE, RUN_REPORT_UUID, \
    ERROR, HDF5_DATASET, UUID, IMAGE_STACKS
from bioweb_api import HDF5_COLLECTION, RUN_REPORT_COLLECTION
from bioweb_api.utilities.io_utilities import make_clean_response

#=============================================================================
# Class
#=============================================================================
class UploadFileDeleteFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return UPLOAD_FILE + '/delete'

    @staticmethod
    def summary():
        return "Unassociate a HDF5/image stack file."

    @staticmethod
    def notes():
        return "Unassociate a HDF5/image stack file from a run report."

    def response_messages(self):
        msgs = super(UploadFileDeleteFunction, self).response_messages()
        msgs.extend([
                     { "code": 400,
                       "message": "Run report does not exist."},
                    ])
        return msgs

    @classmethod
    def parameters(cls):
        cls.dataset_parameter = ParameterFactory.pa_data_source()
        cls.report_uuid_parameter = ParameterFactory.uuid(allow_multiple=False)

        parameters = [
                      cls.dataset_parameter,
                      cls.report_uuid_parameter,
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        if cls.dataset_parameter in params_dict:
            dataset = params_dict[cls.dataset_parameter][0]
        else:
            dataset = None

        if cls.report_uuid_parameter in params_dict:
            report_uuid = params_dict[cls.report_uuid_parameter][0]
        else:
            report_uuid = None

        http_status_code = 200
        json_response = {RUN_REPORT_UUID: report_uuid, HDF5_DATASET: dataset}

        if cls._DB_CONNECTOR.find_one(RUN_REPORT_COLLECTION, UUID, report_uuid) is None:
            http_status_code = 400
        else:
            try:
                cls._DB_CONNECTOR.update(RUN_REPORT_COLLECTION,
                                         {UUID: report_uuid},
                                         {'$pull': {IMAGE_STACKS: {'name': dataset, 'upload': True}}})
                cls._DB_CONNECTOR.remove(HDF5_COLLECTION,
                                         {HDF5_DATASET: dataset})
                APP_LOGGER.info("Removed dataset name=%s from run report uuid=%s" %
                                (dataset, report_uuid))
            except:
                APP_LOGGER.exception(traceback.format_exc())
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500

        return make_clean_response(json_response, http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = UploadFileDeleteFunction()
    print function
