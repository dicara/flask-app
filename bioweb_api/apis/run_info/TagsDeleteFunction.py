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
@date:   July 13th, 2017
'''

#=============================================================================
# Imports
#=============================================================================
import sys
import traceback

from bioweb_api.apis.AbstractDeleteFunction import AbstractDeleteFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.ApiConstants import RUN_REPORT_UUID, ERROR, UUID, TAGS, STATUS, \
    SUCCEEDED, FAILED
from bioweb_api import RUN_REPORT_COLLECTION

#=============================================================================
# Class
#=============================================================================
class TagsDeleteFunction(AbstractDeleteFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return TAGS

    @staticmethod
    def summary():
        return "Remove a tag from a run report."

    @staticmethod
    def notes():
        return "Remove a tag from a run report document."

    def response_messages(self):
        msgs = super(TagsDeleteFunction, self).response_messages()
        msgs.extend([
                     { "code": 400,
                       "message": "Run report does not exist."},
                    ])
        return msgs

    @classmethod
    def parameters(cls):
        cls.tag_parameter = ParameterFactory.tags("Run report tags.")
        cls.report_uuid_parameter = ParameterFactory.uuid(allow_multiple=False)

        parameters = [
                      cls.tag_parameter,
                      cls.report_uuid_parameter,
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        tag = None
        if cls.tag_parameter in params_dict:
            tag = params_dict[cls.tag_parameter][0]

        report_uuid = None
        if cls.report_uuid_parameter in params_dict:
            report_uuid = params_dict[cls.report_uuid_parameter][0]

        http_status_code = 200
        json_response = {RUN_REPORT_UUID: report_uuid, TAGS: [tag]}

        if cls._DB_CONNECTOR.find_one(RUN_REPORT_COLLECTION, UUID, report_uuid) is None:
            http_status_code = 400
        else:
            try:
                cls._DB_CONNECTOR.update(RUN_REPORT_COLLECTION,
                                         {UUID: report_uuid},
                                         {'$pull': {TAGS: tag}})
                json_response[STATUS] = SUCCEEDED
                APP_LOGGER.info("Removed tag name=%s from run report uuid=%s" %
                                (tag, report_uuid))
            except:
                APP_LOGGER.exception(traceback.format_exc())
                json_response[ERROR] = str(sys.exc_info()[1])
                json_response[STATUS] = FAILED
                http_status_code     = 500

        return json_response, http_status_code

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = TagsDeleteFunction()
    print function
