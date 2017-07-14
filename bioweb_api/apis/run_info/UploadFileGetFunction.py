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

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.ApiConstants import UPLOAD_FILE, ERROR
from bioweb_api import MODIFIED_ARCHIVES_PATH
from bioweb_api.apis.run_info.RunInfoUtils import allowed_file

#=============================================================================
# Class
#=============================================================================
class UploadFileGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return UPLOAD_FILE

    @staticmethod
    def summary():
        return "Get modified HDF5 files."

    @staticmethod
    def notes():
        return "Get available HDF5 files in archive location."

    @classmethod
    def parameters(cls):
        parameters = []
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        try:
            valid_files = [fp for fp in os.listdir(MODIFIED_ARCHIVES_PATH)
                           if allowed_file(os.path.join(MODIFIED_ARCHIVES_PATH, fp))]
            return (valid_files, [], None)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            return ([{ERROR: str(sys.exc_info()[1])}], [ERROR], None)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = UploadFileGetFunction()
    print function
