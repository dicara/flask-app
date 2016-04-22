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
@date:   Apr 21, 2016
'''

#=============================================================================
# Imports
#=============================================================================
import sys
import traceback

from bioweb_api import FA_PROCESS_COLLECTION, RUN_REPORT_COLLECTION
from bioweb_api.apis.ApiConstants import UUID, ERROR, RUN_REPORT
from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.run_info.constants import FA_UUID_MAP, FA_UUID, METHOD, \
                                            ARCHIVE_IDX

#===============================================================================
# Class
#===============================================================================
class RunInfoPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return RUN_REPORT

    @staticmethod
    def summary():
        return 'Update database with full analysis uuid.'

    @staticmethod
    def notes():
        return ''

    def response_messages(self):
        msgs = super(RunInfoPostFunction, self).response_messages()
        msgs.extend([
                     { 'code': 404,
                       'message': 'Update failed.'},
                    ])
        return msgs

    @classmethod
    def parameters(cls):
        cls.rr_uuid_param     = ParameterFactory.uuid()
        cls.archive_idx_param = ParameterFactory.integer(ARCHIVE_IDX, "Index of "\
                                                        "archive in image stack list",
                                                        required=True)
        cls.fa_uuid_param     = ParameterFactory.lc_string(FA_UUID, "UUID of "\
                                                           "full analysis job")
        cls.method_param      = ParameterFactory.lc_string(METHOD, "Method of "\
                                                          "updating",
                                                          required=True)

        parameters = [
                      cls.rr_uuid_param,
                      cls.archive_idx_param,
                      cls.fa_uuid_param,
                      cls.method_param,
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        rr_uuid         = params_dict[cls.rr_uuid_param][0]
        archive_idx     = params_dict[cls.archive_idx_param][0]
        fa_uuid         = params_dict[cls.fa_uuid_param][0]
        method          = params_dict[cls.method_param][0]

        json_response = {RUN_REPORT: []}

        try:
            query = {UUID: rr_uuid}
            update = None
            field = '.'.join([FA_UUID_MAP, str(archive_idx)])
            if method == "add":
                update = {"$set": {field: fa_uuid}}
            elif method == "delete":
                update = {"$unset": {field: 1}}
            else:
                APP_LOGGER.exception("Unknown update method")
            if update is not None:
                cls._DB_CONNECTOR.update(RUN_REPORT_COLLECTION, query, update)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)
        finally:
            response = {UUID: rr_uuid, ARCHIVE_IDX: archive_idx, FA_UUID: fa_uuid,
                        METHOD: method}
            json_response[RUN_REPORT].append(response)

        return make_clean_response(json_response, 200)
