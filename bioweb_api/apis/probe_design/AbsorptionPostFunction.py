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
from probe_design.absorption import execute_absorption

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import PROBES_COLLECTION, TARGETS_COLLECTION, ABSORPTION_COLLECTION, \
    RESULTS_PATH, HOSTNAME, PORT, REFS_PATH, USER_HOME_DIR
from bioweb_api.apis.ApiConstants import UUID, FILEPATH, JOB_STATUS, STATUS, ID, \
    ERROR, JOB_NAME, PROBES, TARGETS, RESULT, URL, SUBMIT_DATESTAMP, \
    START_DATESTAMP, FINISH_DATESTAMP, JOB_TYPE, JOB_TYPE_NAME
    
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
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.file_uuid(PROBES, PROBES_COLLECTION),
                      ParameterFactory.file_uuid(TARGETS, TARGETS_COLLECTION),
                      ParameterFactory.cs_string(JOB_NAME, "Unique name to give this job.")
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        probes_file_uuid  = params_dict[ParameterFactory.file_uuid("probes", PROBES_COLLECTION)][0]
        targets_file_uuid = params_dict[ParameterFactory.file_uuid("targets", TARGETS_COLLECTION)][0]
        job_name          = params_dict[ParameterFactory.cs_string(JOB_NAME, "Unique name to give this job.")][0]
        
        json_response = {
                         PROBES: probes_file_uuid,
                         TARGETS: targets_file_uuid,
                         UUID: str(uuid4()),
                         STATUS: JOB_STATUS.submitted,      # @UndefinedVariable
                         JOB_NAME: job_name,
                         JOB_TYPE_NAME: JOB_TYPE.absorption, # @UndefinedVariable
                         SUBMIT_DATESTAMP: datetime.today(),
                        }
        http_status_code = 200
        
        if job_name in cls._DB_CONNECTOR.distinct(ABSORPTION_COLLECTION, JOB_NAME):
            http_status_code     = 403
        else:
            try:
                # Gather inputs
                ref_genome_path = os.path.join(REFS_PATH, "genome.fa")
                if not os.path.isfile(ref_genome_path):
                    raise Exception("Invalid reference genome: %s" % ref_genome_path)
                blat_path = os.path.join(USER_HOME_DIR, "bin", "blat")
                if not os.path.isfile(blat_path):
                    raise Exception("Invalid blat location: %s" % blat_path)
                probes_path  = cls._DB_CONNECTOR.find_one(PROBES_COLLECTION, UUID, probes_file_uuid)[FILEPATH]
                targets_path = cls._DB_CONNECTOR.find_one(TARGETS_COLLECTION, UUID, targets_file_uuid)[FILEPATH]
                outfile_path = os.path.join(RESULTS_PATH, json_response[UUID])
                
                # Create helper functions
                abs_callable = AbsorbtionCallable(blat_path, ref_genome_path, targets_path, probes_path, outfile_path, json_response[UUID], cls._DB_CONNECTOR)
                callback     = make_absorption_callback(json_response[UUID], outfile_path, cls._DB_CONNECTOR)
                
                # Add to queue and update DB
                cls._DB_CONNECTOR.insert(ABSORPTION_COLLECTION, [json_response])
                cls._EXECUTION_MANAGER.add_job(json_response[UUID], abs_callable, callback)
                del json_response[ID]
            except:
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500
        
        return make_response(jsonify(json_response), http_status_code)

#===============================================================================
# Callable/Callback Functionality
#===============================================================================
class AbsorbtionCallable(object):
    """
    Callable that executes the absorption command.
    """
    def __init__(self, blat_path, ref_genome_path, targets_path, probes_path, 
                 outfile_path, uuid, db_connector):
        self.blat_path       = blat_path
        self.ref_genome_path = ref_genome_path
        self.targets_path    = targets_path
        self.probes_path     = probes_path
        self.outfile_path    = outfile_path
        self.db_connector    = db_connector
        self.query           = {UUID: uuid}
    
    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}     
        self.db_connector.update(ABSORPTION_COLLECTION, self.query, update)
        return execute_absorption(self.blat_path, self.ref_genome_path, 
                                  self.targets_path, self.probes_path, 
                                  self.outfile_path)
        
def make_absorption_callback(uuid, outfile_path, db_connector):
    """
    Return a closure that is fired when the absorption job finishes. This 
    callback updates the DB with completion status, result file location, and
    an error message if applicable.
    
    :param uuid: Unique job id in database
    :param outfile_path: Path to generated results file
    :param db_connector: Object that handles communication with the DB
    """
    query = {UUID: uuid}
    def absorption_callback(future):
        try:
            _ = future.result()
            update = { "$set": {STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                RESULT: outfile_path,
                                FINISH_DATESTAMP: datetime.today(),
                                URL: "http://%s/results/%s/%s" % (HOSTNAME, PORT, uuid)}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(ABSORPTION_COLLECTION, query, {})) > 0:
                db_connector.update(ABSORPTION_COLLECTION, query, update)
            elif os.path.isfile(outfile_path):
                os.remove(outfile_path)
        except:
            error_msg = str(sys.exc_info()[1])
            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   RESULT: None, 
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(ABSORPTION_COLLECTION, query, {})) > 0:
                db_connector.update(ABSORPTION_COLLECTION, query, update)
            elif os.path.isfile(outfile_path):
                os.remove(outfile_path)
    return absorption_callback
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = AbsorptionPostFunction()
    print function