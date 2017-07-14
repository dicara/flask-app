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
@date:   July 12th, 2017
'''

#=============================================================================
# Imports
#=============================================================================
import sys
import traceback

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.ApiConstants import RUN_REPORT_UUID, ERROR, UUID, TAGS, \
    STATUS, SUCCEEDED, FAILED
from bioweb_api import RUN_REPORT_COLLECTION
from bioweb_api.utilities.io_utilities import make_clean_response

#=============================================================================
# Class
#=============================================================================
class TagsPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return TAGS

    @staticmethod
    def summary():
        return "Add tags to a run report."

    @staticmethod
    def notes():
        return "Add custom tags to a run report. Tags can be sample type, amplicons, " \
               "barcode library, or user-specified."

    def response_messages(self):
        msgs = super(TagsPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 400,
                       "message": "Run report uuid is missing or run report does not exist."},
                    ])
        return msgs

    @classmethod
    def parameters(cls):
        cls.tags_parameter = ParameterFactory.tags("Run report tags.")
        cls.report_uuid_parameter = ParameterFactory.uuid(allow_multiple=False)

        parameters = [
                      cls.tags_parameter,
                      cls.report_uuid_parameter,
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        tags = list()
        if cls.tags_parameter in params_dict:
            tags = [t for t in params_dict[cls.tags_parameter] if t]

        report_uuid = None
        if cls.report_uuid_parameter in params_dict:
            report_uuid = params_dict[cls.report_uuid_parameter][0]

        http_status_code = 200
        json_response = {RUN_REPORT_UUID: report_uuid, TAGS: tags}

        report = cls._DB_CONNECTOR.find_one(RUN_REPORT_COLLECTION,
                                            UUID, report_uuid)
        if report_uuid is None or report is None:
            http_status_code = 400
        else:
            try:
                # tags are case insensitive
                exist_lc_tags = set(t.lower() for t in report[TAGS])
                new_tags = [t for t in tags if t.lower() not in exist_lc_tags]

                cls._DB_CONNECTOR.update(RUN_REPORT_COLLECTION,
                                 {UUID: report_uuid},
                                 {'$addToSet': {TAGS: {'$each': new_tags}}})
                APP_LOGGER.info("Updated run report uuid=%s with tags %s."
                                % (report_uuid, tags))

                json_response[STATUS] = SUCCEEDED
            except:
                APP_LOGGER.exception(traceback.format_exc())
                json_response[STATUS] = FAILED
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500

        return make_clean_response(json_response, http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = TagsPostFunction()
    print function
