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
import sys
import traceback
import os

from uuid import uuid4
from datetime import datetime

from bioweb_api.utilities.io_utilities import make_clean_response, get_archive_dirs
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.io_utilities import silently_remove_file
from bioweb_api import PA_PROCESS_COLLECTION, HOSTNAME, PORT, RESULTS_PATH
from bioweb_api.apis.ApiConstants import UUID, ARCHIVE, JOB_STATUS, STATUS, ID, \
    ERROR, JOB_NAME, SUBMIT_DATESTAMP, DYES, DEVICE, START_DATESTAMP, RESULT, \
    FINISH_DATESTAMP, URL, CONFIG_URL, JOB_TYPE, JOB_TYPE_NAME, CONFIG, \
    OFFSETS, MAJOR, MINOR, USE_IID
    
from bioweb_api.apis.primary_analysis.PrimaryAnalysisUtils import execute_process
    
from primary_analysis.dye_model import DEFAULT_OFFSETS

#===============================================================================
# Public Static Variables
#===============================================================================
PROCESS        = "Process"

#===============================================================================
# Private Static Variables
#===============================================================================
_MIN_NUM_IMAGES = 10 # Minimum number of images required to run 

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
        cls.archives_param = ParameterFactory.archive()
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
                      cls.archives_param,
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
        archive_name  = params_dict[cls.archives_param][0]
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
            archives = get_archive_dirs(archive_name, 
                                        min_num_images=_MIN_NUM_IMAGES)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)
        
        # Ensure at least one valid archive is found
        if len(archives) < 1:
            return make_clean_response(json_response, 404)
        
        # Process each archive
        status_codes  = []
        for i, archive in enumerate(archives):
            if len(archives) == 1:
                cur_job_name = job_name
            else:
                cur_job_name = "%s-%d" % (job_name, i)
                
            response = {
                        ARCHIVE: archive,
                        DYES: dyes,
                        DEVICE: device,
                        OFFSETS: offset,
                        USE_IID: use_iid,
                        UUID: str(uuid4()),
                        STATUS: JOB_STATUS.submitted,       # @UndefinedVariable
                        JOB_NAME: cur_job_name,
                        JOB_TYPE_NAME: JOB_TYPE.pa_process, # @UndefinedVariable
                        SUBMIT_DATESTAMP: datetime.today(),
                       }
            status_code = 200
            
            if cur_job_name in cls._DB_CONNECTOR.distinct(PA_PROCESS_COLLECTION, 
                                                      JOB_NAME):
                status_code = 403
            else:
                try:
                    outfile_path = os.path.join(RESULTS_PATH, response[UUID])
                    config_path  = outfile_path + ".cfg"
                    
                    # Create helper functions
                    abs_callable = PaProcessCallable(archive, dyes, device,
                                                     major, minor,
                                                     offset, use_iid, 
                                                     outfile_path, 
                                                     config_path,
                                                     response[UUID], 
                                                     cls._DB_CONNECTOR)
                    callback = make_process_callback(response[UUID], 
                                                     outfile_path, 
                                                     config_path,
                                                     cls._DB_CONNECTOR)
    
                    # Add to queue and update DB
                    cls._DB_CONNECTOR.insert(PA_PROCESS_COLLECTION, [response])
                    cls._EXECUTION_MANAGER.add_job(response[UUID], 
                                                   abs_callable, callback)
                except:
                    APP_LOGGER.exception(traceback.format_exc())
                    response[ERROR]  = str(sys.exc_info()[1])
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
                 outfile_path, config_path, uuid, db_connector):
        self.archive      = archive
        self.dyes         = dyes
        self.device       = device
        self.major        = major
        self.minor        = minor
        self.offsets      = range(-offset, offset)
        self.use_iid      = use_iid
        self.outfile_path = outfile_path
        self.config_path  = config_path
        self.db_connector = db_connector
        self.query        = {UUID: uuid}
    
    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}     
        self.db_connector.update(PA_PROCESS_COLLECTION, self.query, update)
        return execute_process(self.archive, self.dyes, self.device, self.major,
                               self.minor, self.offsets, self.use_iid, 
                               self.outfile_path, self.config_path, 
                               self.query[UUID])
        
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
            update = { "$set": { 
                                 STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                 RESULT: outfile_path,
                                 CONFIG: config_path,
                                 FINISH_DATESTAMP: datetime.today(),
                                 URL: "http://%s/results/%s/%s" % (HOSTNAME, PORT, uuid),
                                 CONFIG_URL: "http://%s/results/%s/%s.cfg" % (HOSTNAME, PORT, uuid),
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