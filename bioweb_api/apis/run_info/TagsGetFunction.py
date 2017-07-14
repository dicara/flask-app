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
import sys
import traceback

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.ApiConstants import ERROR, TAGS
from bioweb_api import RUN_REPORT_COLLECTION

#=============================================================================
# Class
#=============================================================================
class TagsGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return TAGS

    @staticmethod
    def summary():
        return "Get existing run report tags."

    @staticmethod
    def notes():
        return "Get existing run report tags stored in database."

    @classmethod
    def parameters(cls):
        parameters = []
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        try:
            reports = cls._DB_CONNECTOR.find(RUN_REPORT_COLLECTION,
                                             {TAGS: {'$exists': True}})
            user_tags = set(t for r in reports for t in r[TAGS])
            return (list(user_tags), [], None)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            return ([{ERROR: str(sys.exc_info()[1])}], [ERROR], None)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = TagsGetFunction()
    print function
