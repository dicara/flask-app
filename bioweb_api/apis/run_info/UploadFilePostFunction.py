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
    ERROR, HDF5_PATH, UUID, IMAGE_STACKS, HDF5_DATASET, ID
from bioweb_api.apis.run_info.RunInfoUtils import get_datasets_from_files, allowed_file
from bioweb_api import MODIFIED_ARCHIVES_PATH, HDF5_COLLECTION, RUN_REPORT_COLLECTION
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
                       "message": "One or more file(s) already associated with other run report(s) \
                                   or contains datasets with names existing in database."},
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
        filenames = list()
        if cls.filenames_parameter in params_dict:
            filenames = params_dict[cls.filenames_parameter][0].split(',')

        report_uuid = None
        if cls.report_uuid_parameter in params_dict:
            report_uuid = params_dict[cls.report_uuid_parameter][0]

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
                fp_to_datasets, duplicate = get_datasets_from_files(filepaths)
                if not fp_to_datasets or not duplicate:
                    http_status_code = 403
                else:
                    new_hdf5_records = [{HDF5_PATH: fp, HDF5_DATASET: dsname, "upload": True}
                                        for fp in fp_to_datasets for dsname in fp_to_datasets[fp]]
                    cls._DB_CONNECTOR.insert(HDF5_COLLECTION, new_hdf5_records)
                    APP_LOGGER.info('Updated database with %d new HDF5 files' % len(new_hdf5_records))

                    run_report = cls._DB_CONNECTOR.find_one(RUN_REPORT_COLLECTION, UUID, report_uuid)
                    if run_report:
                        exist_datasets = set([d for d in run_report[IMAGE_STACKS]
                                              if isinstance(d, str) or isinstance(d, unicode)])
                        new_datasets = set()
                        for datasets in fp_to_datasets.values():
                            new_datasets = new_datasets | datasets
                        new_datasets = list(new_datasets - exist_datasets)
                        if new_datasets:
                            cls._DB_CONNECTOR.update(RUN_REPORT_COLLECTION,
                                             {UUID: report_uuid},
                                             {'$addToSet': {IMAGE_STACKS:
                                                {'$each': [{'name': d, 'upload': True} for d in new_datasets]}}})
                            APP_LOGGER.info("Updated run report uuid=%s with %d HDF5 datasets."
                                            % (report_uuid, len(new_datasets)))

                        del run_report[ID]
                        json_response.update({"run_report": run_report, "uploaded": new_datasets})
                    else:
                        json_response.update({"error": "Run report uuid=%s does not exist." % report_uuid})
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
