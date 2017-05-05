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

from werkzeug.utils import secure_filename

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.ApiConstants import UPLOAD_FILE, FILENAMES, RUN_REPORT_UUID, \
    ERROR, HDF5_PATH
from bioweb_api.apis.run_info.RunInfoUtils import add_datasets, allowed_file
from bioweb_api import MODIFIED_ARCHIVES_PATH, HDF5_COLLECTION
from bioweb_api.utilities.io_utilities import make_clean_response

#=============================================================================
# Class
#=============================================================================
class UploadFilePostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return UPLOAD_FILE

    @staticmethod
    def summary():
        return "Upload a HDF5/image stack file."

    @staticmethod
    def notes():
        return "Upload a HDF5/image stack file and associate it with a run report."

    def response_messages(self):
        msgs = super(UploadFilePostFunction, self).response_messages()
        msgs.extend([
                     { "code": 400,
                       "message": "One or more file(s) do not exist or not a valid HDF5 file."},
                     { "code": 403,
                       "message": "One or more file(s) already associated with other run report(s)."},
                    ])
        return msgs

    @classmethod
    def parameters(cls):
        cls.filenames_parameter = ParameterFactory.filenames()
        cls.report_uuid_parameter = ParameterFactory.uuid(allow_multiple=False)

        parameters = [
                      cls.filenames_parameter,
                      cls.report_uuid_parameter,
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        if cls.filenames_parameter in params_dict:
            filenames = params_dict[cls.filenames_parameter][0].split(',')
        else:
            filenames = list()

        if cls.report_uuid_parameter in params_dict:
            report_uuid = params_dict[cls.report_uuid_parameter][0]
        else:
            report_uuid = None

        http_status_code = 200
        json_response = {RUN_REPORT_UUID: report_uuid, FILENAMES: filenames}

        filepaths = [os.path.join(MODIFIED_ARCHIVES_PATH, secure_filename(fn))
                     for fn in filenames]
        if not filenames or not report_uuid or not all(allowed_file(fp) for fp in filepaths):
            http_status_code = 400
        elif any(cls._DB_CONNECTOR.find_one(HDF5_COLLECTION,
                                            HDF5_PATH,
                                            {'$regex': fn + '$'})
                is not None for fn in filenames):
            http_status_code = 403
        else:
            try:
                run_report = add_datasets(filepaths, report_uuid)
                json_response.update(run_report)
            except:
                APP_LOGGER.exception(traceback.format_exc())
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500

        return make_clean_response(json_response, http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = UploadFilePostFunction()
    print function
