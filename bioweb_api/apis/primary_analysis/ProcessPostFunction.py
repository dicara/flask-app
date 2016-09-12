'''
Copyright 2014 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Dan DiCara
@date:   Jun 1, 2014
'''

#=============================================================================
# Imports
#=============================================================================
import copy
from datetime import datetime
import os
import sys
import time
import traceback
import yaml

import h5py
import numpy
from uuid import uuid4

from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.io_utilities import silently_remove_file
from bioweb_api import PA_PROCESS_COLLECTION, HOSTNAME, PORT, RESULTS_PATH
from bioweb_api.apis.ApiConstants import UUID, ARCHIVE, JOB_STATUS, STATUS, ID, \
    ERROR, JOB_NAME, SUBMIT_DATESTAMP, DYES, DEVICE, START_DATESTAMP, RESULT, \
    FINISH_DATESTAMP, URL, CONFIG_URL, JOB_TYPE, JOB_TYPE_NAME, CONFIG, \
    OFFSETS, MAJOR, MINOR, USE_IID, IS_HDF5

from bioweb_api.apis.primary_analysis.PrimaryAnalysisUtils import execute_process, \
    parse_pa_data_src, get_hdf5_dataset_path

from primary_analysis.dye_model import DEFAULT_OFFSETS

#===============================================================================
# Public Static Variables
#===============================================================================
PROCESS        = "Process"

#===============================================================================
# Private Static Variables
#===============================================================================


#===============================================================================
# Class
#===============================================================================
class ProcessPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return PROCESS

    @staticmethod
    def summary():
        return "Run the equivalent of pa process."

    @staticmethod
    def notes():
        return ""

    def response_messages(self):
        msgs = super(ProcessPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403,
                       "message": "Job name already exists. Delete the " \
                                  "existing job or pick a new name."},
                     { "code": 404,
                       "message": "Submission unsuccessful. At least 10 "\
                                  "images must exist in archive."},
                    ])
        return msgs

    @classmethod
    def parameters(cls):
        cls.pa_data_src_param = ParameterFactory.pa_data_source()
        cls.dyes_param     = ParameterFactory.dyes()
        cls.device_param   = ParameterFactory.device()
        cls.major_param    = ParameterFactory.integer(MAJOR, "Major dye " \
                                                      "profile version",
                                                      minimum=0)
        cls.minor_param    = ParameterFactory.integer(MINOR, "Minor dye " \
                                                      "profile version",
                                                      minimum=0)
        cls.job_name_param = ParameterFactory.lc_string(JOB_NAME, "Unique "\
                                                        "name to give this "
                                                        "job.")
        cls.offset         = ParameterFactory.integer(OFFSETS, "Offset used " \
            "to infer a dye model. The inference will offset the dye profiles " \
            "in a range of (-<offset>,<offset>] to determine the optimal " \
            "offset.", default=abs(DEFAULT_OFFSETS[0]), minimum=1)
        cls.use_iid_param  = ParameterFactory.boolean(USE_IID, "Use IID Peak " \
                                                      "Detection.",
                                                      default_value=False)

        parameters = [
                      cls.pa_data_src_param,
                      cls.dyes_param,
                      cls.device_param,
                      cls.major_param,
                      cls.minor_param,
                      cls.job_name_param,
                      cls.offset,
                      cls.use_iid_param,
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        pa_data_src_name  = params_dict[cls.pa_data_src_param][0]
        dyes          = params_dict[cls.dyes_param]
        device        = params_dict[cls.device_param][0]
        job_name      = params_dict[cls.job_name_param][0]
        offset        = params_dict[cls.offset][0]
        use_iid       = params_dict[cls.use_iid_param][0]

        major = None
        if cls.major_param in params_dict:
            major = params_dict[cls.major_param][0]
        minor = None
        if cls.minor_param in params_dict:
            minor = params_dict[cls.minor_param][0]

        json_response = {PROCESS: []}

        # Ensure archive directory is valid
        try:
            archives = parse_pa_data_src(pa_data_src_name)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)

        # Ensure at least one valid archive is found
        if len(archives) < 1:
            return make_clean_response(json_response, 404)

        pa_job_names = set(cls._DB_CONNECTOR.distinct(PA_PROCESS_COLLECTION, JOB_NAME))

        # Process each archive
        status_codes  = []
        for i, (name, is_hdf5) in enumerate(archives):
            if len(archives) == 1:
                cur_job_name = job_name
            else:
                cur_job_name = "%s-%d" % (job_name, i)

            status_code = 200
            if cur_job_name in pa_job_names:
                status_code = 403
                json_response[PROCESS].append({ERROR: 'Job exists.'})
            else:
                try:
                    pa_callable = PaProcessCallable(name, dyes, device,
                                                     major, minor,
                                                     offset, use_iid,
                                                     cls._DB_CONNECTOR,
                                                     cur_job_name, is_hdf5)
                    response = copy.deepcopy(pa_callable.document)
                    callback = make_process_callback(pa_callable.uuid,
                                                     pa_callable.outfile_path,
                                                     pa_callable.config_path,
                                                     cls._DB_CONNECTOR)


                    # Add to queue
                    cls._EXECUTION_MANAGER.add_job(response[UUID],
                                                   pa_callable, callback)
                except:
                    APP_LOGGER.exception(traceback.format_exc())
                    response = {JOB_NAME: cur_job_name, ERROR: str(sys.exc_info()[1])}
                    status_code = 500
                finally:
                    if ID in response:
                        del response[ID]
                    json_response[PROCESS].append(response)

            status_codes.append(status_code)

        # If all jobs submitted successfully, then 200 should be returned.
        # Otherwise, the maximum status code seems good enough.
        return make_clean_response(json_response, max(status_codes))

#===============================================================================
# Callable/Callback Functionality
#===============================================================================
class PaProcessCallable(object):
    """
    Callable that executes the process command.
    """
    def __init__(self, archive, dyes, device, major, minor, offset, use_iid,
                 db_connector, job_name, is_hdf5):
        """
        @param archive:             String, path to archive, could be HDF5 or image.
        @param dyes:                List of strings specifying dye names.
        @param device:              String, device name, used by primary analysis
                                    to retrieve profiles.
        @param major:               Integer, major dye profile version to
                                    retrieve from primary analysis database.
        @param minor:               Integer, minor dye profile version to
                                    retrieve from primary analysis database.
        @param offset:              Integer, pixel offset.
        @param use_iid:             Bool, use iid peak detection.
        @param db_connector:        DB_CONNECTOR instance.
        @param job_name:            String specifying job name.
        @param is_hdf5:             Bool indicates if archive is an HDF5 file.
        """
        self.uuid         = str(uuid4())
        self.is_hdf5      = is_hdf5
        self.archive      = archive
        self.dyes         = dyes
        self.device       = device
        self.major        = major
        self.minor        = minor
        self.offsets      = range(-offset, offset)
        self.use_iid      = use_iid

        date_folder       = os.path.join(RESULTS_PATH, time.strftime('%m_%d_%Y'))
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
        self.outfile_path = os.path.join(date_folder, self.uuid)
        self.config_path  = self.outfile_path + '.cfg'
        self.db_connector = db_connector
        self.document     = {ARCHIVE: archive,
                             IS_HDF5: is_hdf5,
                             DYES: dyes,
                             DEVICE: device,
                             OFFSETS: offset,
                             USE_IID: use_iid,
                             UUID: self.uuid,
                             STATUS: JOB_STATUS.submitted, # @UndefinedVariable
                             JOB_NAME: job_name,
                             JOB_TYPE_NAME: JOB_TYPE.pa_process, # @UndefinedVariable
                             SUBMIT_DATESTAMP: datetime.today()}

        self.db_connector.insert(PA_PROCESS_COLLECTION, [self.document])

    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}
        query = {UUID: self.uuid}
        self.db_connector.update(PA_PROCESS_COLLECTION, query, update)
        if self.is_hdf5:
            hdf5_path = get_hdf5_dataset_path(self.archive)
            dataset = h5py.File(hdf5_path)[self.archive]
            columns = dataset.attrs['columns']
            decomp_dyes = [c.replace('-decomp', '') for c in columns if '-decomp' in c]

            # make config file
            config_file_contents = {
                'dye_map':{
                    'dyes': decomp_dyes,
                    'major': self.major,
                    'minor': self.minor,
                    'device': str(self.device),
                }
            }
            with open(self.config_path, 'w') as fh:
                yaml.dump(config_file_contents, fh)

            self.db_connector.update(PA_PROCESS_COLLECTION,
                                     {UUID: self.uuid},
                                     {"$set": {DYES: decomp_dyes}})

            # write data to disk
            numpy.savetxt(self.outfile_path, dataset.value, fmt='%.1f',
                          delimiter='\t', header='\t'.join(columns), comments='')
        else:
            execute_process(self.archive, self.dyes, self.device, self.major,
                            self.minor, self.offsets, self.use_iid,
                            self.outfile_path, self.config_path,
                            self.uuid)

def make_process_callback(uuid, outfile_path, config_path, db_connector):
    """
    Return a closure that is fired when the job finishes. This
    callback updates the DB with completion status, result file location, and
    an error message if applicable.

    @param uuid: Unique job id in database
    @param outfile_path - Path where the final analysis.txt file should live.
    @param config_path  - Path where the final configuration file should live.
    @param db_connector: Object that handles communication with the DB
    """
    query = {UUID: uuid}
    def process_callback(future):
        try:
            _ = future.result()
            folder = os.path.basename(os.path.dirname(outfile_path))
            update = { "$set": {
                                 STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                 RESULT: outfile_path,
                                 CONFIG: config_path,
                                 FINISH_DATESTAMP: datetime.today(),
                                 URL: "http://%s/results/%s/%s/%s" % (HOSTNAME, PORT, folder, uuid),
                                 CONFIG_URL: "http://%s/results/%s/%s/%s.cfg" % (HOSTNAME, PORT, folder, uuid),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(PA_PROCESS_COLLECTION, query, {})) > 0:
                db_connector.update(PA_PROCESS_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(config_path)
        except:
            error_msg = str(sys.exc_info()[1])
            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   RESULT: None,
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(PA_PROCESS_COLLECTION, query, {})) > 0:
                db_connector.update(PA_PROCESS_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(config_path)

    return process_callback

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProcessPostFunction()
    print function
