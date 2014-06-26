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
from src import PROBES_COLLECTION, TARGETS_COLLECTION, VALIDATION_COLLECTION, \
    RESULTS_FOLDER
from src.apis.ApiConstants import UUID, FILEPATH, JOB_STATUS, STATUS, ID, \
    ERROR, JOB_NAME, PROBES, TARGETS, DATESTAMP, ABSORB, NUM
from src.analyses.probe_validation.absorption import execute_absorption

#=============================================================================
# Class
#=============================================================================
class AbsorptionPostFunction(AbstractPostFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Absorption"
   
    @staticmethod
    def summary():
        return "Check the absorption of a set of probes for a given set of targets."
    
    @staticmethod
    def notes():
        return "Probes and targets files must be uploaded using their upload " \
            "APIs prior to calling this function. Use the provided uuids " \
            "returned by the upload APIs to select the targets and probes " \
            "for which you are performing this validation."

    def response_messages(self):
        msgs = super(AbsorptionPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "Job name already exists. Delete the existing job or pick a new name."},
#                      { "code": 415, 
#                        "message": "File is not a valid FASTA file."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.file_uuid(PROBES, PROBES_COLLECTION),
                      ParameterFactory.file_uuid(TARGETS, TARGETS_COLLECTION),
                      ParameterFactory.boolean("absorb", "Check for absorbed probes."),
                      ParameterFactory.integer("num", "Minimum number of probes for a target.",
                                               default=3, minimum=1),
                      ParameterFactory.lc_string(JOB_NAME, "Unique name to give this job.")
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        probes_file_uuid  = params_dict[ParameterFactory.file_uuid("probes", PROBES_COLLECTION)][0]
        targets_file_uuid = params_dict[ParameterFactory.file_uuid("targets", TARGETS_COLLECTION)][0]
        absorb            = params_dict[ParameterFactory.boolean("absorb", "Check for absorbed probes.")][0]
        num               = params_dict[ParameterFactory.integer("num", "Minimum number of probes for a target.",
                                               default=3, minimum=1)][0]
        job_name          = params_dict[ParameterFactory.lc_string(JOB_NAME, "Unique name to give this job.")][0]
        
        json_response = {
                         PROBES: probes_file_uuid,
                         TARGETS: targets_file_uuid,
                         ABSORB: absorb,
                         NUM: num,
                         UUID: str(uuid4()),
                         STATUS: JOB_STATUS.submitted,      # @UndefinedVariable
                         JOB_NAME: job_name,
                         DATESTAMP: datetime.today(),
                        }
        http_status_code = 200
        
        if job_name in cls._DB_CONNECTOR.get_distinct(VALIDATION_COLLECTION, JOB_NAME):
            http_status_code     = 403
        else:
            try:
                # Gather inputs
                probes_path  = cls._DB_CONNECTOR.find_one(PROBES_COLLECTION, UUID, probes_file_uuid)[FILEPATH]
                targets_path = cls._DB_CONNECTOR.find_one(TARGETS_COLLECTION, UUID, targets_file_uuid)[FILEPATH]
                outfile_path = os.path.join(RESULTS_FOLDER, json_response[UUID])
                
                # Create helper functions
                callback     = make_absorption_callback(json_response[UUID], outfile_path, cls._DB_CONNECTOR)
                job_runner   = make_job_runner(targets_path, probes_path, outfile_path)
                
                # Add to queue and update DB
                cls._EXECUTION_MANAGER.add_job(json_response[UUID], callback, job_runner)
                cls._DB_CONNECTOR.insert(VALIDATION_COLLECTION, [json_response])
                del json_response[ID]
            except:
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500
        
        return make_response(jsonify(json_response), http_status_code)
    
def make_job_runner(targets_path, probes_path, outfile_path):
    def run():
        #TODO: Can we include db connector and set status to running 
        return execute_absorption(targets_path, probes_path, outfile_path)
    return run
        
def make_absorption_callback(uuid, outfile_path, db_connector):
    def absorption_callback(future):
        print "CALLBACK"
        try:
            result = future.result()
            query = { UUID: uuid}
            update = { "$set": {"status": "success", "result": outfile_path}}
            db_connector.update(VALIDATION_COLLECTION, query, update)
        except:
            query = { UUID: uuid}
            update = { "$set": {"status": "failed", "result": None}}
            db_connector.update(VALIDATION_COLLECTION, query, update)
    return absorption_callback
    
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = AbsorptionPostFunction()
    print function