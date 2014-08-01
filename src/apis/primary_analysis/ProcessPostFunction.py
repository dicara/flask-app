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
import os

from flask import make_response, jsonify
from uuid import uuid4
from datetime import datetime

from src.apis.AbstractPostFunction import AbstractPostFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from src.utilities.io_utilities import silently_remove_file
from src import PA_PROCESS_COLLECTION, HOSTNAME, PORT, RESULTS_PATH
from src.apis.ApiConstants import UUID, ARCHIVE, JOB_STATUS, STATUS, ID, \
    ERROR, JOB_NAME, SUBMIT_DATESTAMP, DYES, DEVICE, START_DATESTAMP, RESULT, \
    FINISH_DATESTAMP, URL, JOB_TYPE, JOB_TYPE_NAME, CONFIG
    
from src.analyses.primary_analysis.PrimaryAnalysisUtils import execute_process

#=============================================================================
# Class
#=============================================================================
class ProcessPostFunction(AbstractPostFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Process"
   
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
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        cls.archives_param = ParameterFactory.archive()
        cls.dyes_param     = ParameterFactory.dyes()
        cls.devices_param  = ParameterFactory.device()
        cls.job_name_param = ParameterFactory.lc_string(JOB_NAME, "Unique "\
                                                        "name to give this "
                                                        "job.")
        
        parameters = [
                      cls.archives_param,
                      cls.dyes_param,
                      cls.devices_param,
                      cls.job_name_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        archive  = params_dict[cls.archives_param][0]
        dyes     = params_dict[cls.dyes_param]
        device   = params_dict[cls.devices_param][0]
        job_name = params_dict[cls.job_name_param][0]
        
        json_response = {
                         ARCHIVE: archive,
                         DYES: dyes,
                         DEVICE: device,
                         UUID: str(uuid4()),
                         STATUS: JOB_STATUS.submitted,      # @UndefinedVariable
                         JOB_NAME: job_name,
                         JOB_TYPE_NAME: JOB_TYPE.pa_process, # @UndefinedVariable
                         SUBMIT_DATESTAMP: datetime.today(),
                        }
        http_status_code = 200
        
        if job_name in cls._DB_CONNECTOR.distinct(PA_PROCESS_COLLECTION, 
                                                  JOB_NAME):
            http_status_code     = 403
        else:
            try:
                outfile_path = os.path.join(RESULTS_PATH, json_response[UUID])
                config_path  = outfile_path + ".cfg"
                
                # Create helper functions
                abs_callable = PaProcessCallable(archive, dyes, device, 
                                                 outfile_path, 
                                                 config_path,
                                                 json_response[UUID], 
                                                 cls._DB_CONNECTOR)
                callback     = make_process_callback(json_response[UUID], 
                                                     outfile_path, 
                                                     config_path,
                                                     cls._DB_CONNECTOR)

                # Add to queue and update DB
                cls._DB_CONNECTOR.insert(PA_PROCESS_COLLECTION, [json_response])
                cls._EXECUTION_MANAGER.add_job(json_response[UUID], 
                                               abs_callable, callback)
                del json_response[ID]
            except:
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500
        
        return make_response(jsonify(json_response), http_status_code)
#===============================================================================
# Callable/Callback Functionality
#===============================================================================
class PaProcessCallable(object):
    """
    Callable that executes the absorption command.
    """
    def __init__(self, archive, dyes, device, outfile_path, config_path, uuid, 
                 db_connector):
        self.archive      = archive
        self.dyes         = dyes
        self.device       = device
        self.outfile_path = outfile_path
        self.config_path  = config_path
        self.db_connector = db_connector
        self.query        = {UUID: uuid}
    
    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}     
        self.db_connector.update(PA_PROCESS_COLLECTION, self.query, update)
        return execute_process(self.archive, self.dyes, self.device, 
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
            update = { "$set": {STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                RESULT: outfile_path,
                                CONFIG: config_path,
                                FINISH_DATESTAMP: datetime.today(),
                                URL: "http://%s/results/%s/%s" % (HOSTNAME, PORT, uuid)}}
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