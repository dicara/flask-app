'''
Copyright 2016 Bio-Rad Laboratories, Inc.

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
@date:   Feb 16, 2016
'''

#=============================================================================
# Imports
#=============================================================================
import logging
import os
import shutil
import sys

from datetime import datetime
from uuid import uuid4

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import SA_GENOTYPER_COLLECTION, SA_ASSAY_CALLER_COLLECTION, \
    SA_IDENTITY_COLLECTION, RESULTS_PATH, TMP_PATH, HOSTNAME, PORT
from bioweb_api.apis.ApiConstants import JOB_NAME, UUID, ERROR, ID, \
    RESULT, EXP_DEF_NAME, EXP_DEF_UUID, SA_ASSAY_CALLER_UUID, SUBMIT_DATESTAMP,\
    SA_IDENTITY_UUID, IGNORED_DYES, FILTERED_DYES, REQUIRED_DROPS, \
    JOB_NAME_DESC, START_DATESTAMP, FINISH_DATESTAMP, URL, JOB_STATUS, \
    STATUS, JOB_TYPE, JOB_TYPE_NAME, VCF, PDF
from bioweb_api.utilities.io_utilities import make_clean_response, \
    silently_remove_file, safe_make_dirs
from bioweb_api.utilities.logging_utilities import APP_LOGGER

from expdb import HotspotExperiment
from primary_analysis.experiment.experiment_definitions import ExperimentDefinitions
from primary_analysis.command import InvalidFileError
from secondary_analysis.genotyping.genotype_analysis import GenotypeProcessor

#=============================================================================
# Public Static Variables
#=============================================================================
GENOTYPER = "Genotyper"

#=============================================================================
# Private Static Variables
#=============================================================================
log = logging.getLogger(__name__)
_REQ_DROPS_DESC = "Number of drops to use in genotyping (0 to use all available)."

#=============================================================================
# Class
#=============================================================================
class GenotyperPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return GENOTYPER
   
    @staticmethod
    def summary():
        return "Run the equivalent of sa genotyper."
    
    @staticmethod
    def notes():
        return ""

    def response_messages(self):
        msgs = super(GenotyperPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "Job name already exists. Delete the " \
                                  "existing job or pick a new name."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        cls.job_uuid_param  = ParameterFactory.job_uuid(SA_ASSAY_CALLER_COLLECTION)
        cls.job_name_param  = ParameterFactory.lc_string(JOB_NAME, JOB_NAME_DESC)
        cls.exp_defs_param  = ParameterFactory.experiment_definition()
        cls.req_drops_param = ParameterFactory.integer(REQUIRED_DROPS, 
                                                       _REQ_DROPS_DESC, 
                                                       required=True, default=0, 
                                                       minimum=0)

        parameters = [
                      cls.job_uuid_param,
                      cls.job_name_param,
                      cls.exp_defs_param,
                      cls.req_drops_param,
                      ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        job_uuids       = params_dict[cls.job_uuid_param]
        job_name        = params_dict[cls.job_name_param][0]
        exp_def_name    = params_dict[cls.exp_defs_param][0]
        required_drops  = params_dict[cls.req_drops_param][0]
        
        json_response = {GENOTYPER: []}
        
        # Retrieve assay caller job
        try:
            criteria          = {UUID: {"$in": job_uuids}}
            projection        = {ID: 0, RESULT: 1, UUID: 1, SA_IDENTITY_UUID: 1}
            assay_caller_jobs = cls._DB_CONNECTOR.find(SA_ASSAY_CALLER_COLLECTION, 
                                                       criteria, projection)
        except:
            APP_LOGGER.exception("Error retrieving provided assay caller job(s).")
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)
        
        # Retrieve experiment definition
        try:
            exp_defs     = ExperimentDefinitions()
            exp_def_uuid = exp_defs.get_experiment_uuid(exp_def_name)
        except:
            APP_LOGGER.exception("Error retrieving provided experiment definition.")
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)
            
        status_codes = list()
        for i, assay_caller_job in enumerate(assay_caller_jobs):
            if len(assay_caller_jobs) == 1:
                cur_job_name = job_name
            else:
                cur_job_name = "%s-%d" % (job_name, i)

            response = {
                        EXP_DEF_NAME: exp_def_name,
                        EXP_DEF_UUID: exp_def_uuid,
                        REQUIRED_DROPS: required_drops,
                        UUID: str(uuid4()),
                        SA_ASSAY_CALLER_UUID: assay_caller_job[UUID],
                        STATUS: JOB_STATUS.submitted,     # @UndefinedVariable
                        JOB_NAME: cur_job_name,
                        JOB_TYPE_NAME: JOB_TYPE.sa_genotyping, # @UndefinedVariable
                        SUBMIT_DATESTAMP: datetime.today(),
                       }
            status_code = 200
            
            if cur_job_name in cls._DB_CONNECTOR.distinct(SA_GENOTYPER_COLLECTION,
                                                          JOB_NAME):
                status_code = 403
            else:
                try:
                    outfile_path = os.path.join(RESULTS_PATH, response[UUID] + '.%s' % VCF)
                    ac_uuid = assay_caller_job[SA_IDENTITY_UUID]
                    record = cls._DB_CONNECTOR.find_one(SA_IDENTITY_COLLECTION, 
                        UUID, ac_uuid)
                    ignored_dyes = record[IGNORED_DYES] + record[FILTERED_DYES]
                    
                    if not os.path.isfile(assay_caller_job[RESULT]):
                        raise InvalidFileError(assay_caller_job[RESULT])

                    # Create helper functions
                    genotyper_callable = SaGenotyperCallable(exp_def_uuid,
                                                             assay_caller_job[RESULT],
                                                             outfile_path,
                                                             required_drops,
                                                             ignored_dyes,
                                                             response[UUID],
                                                             cls._DB_CONNECTOR)
                    callback = make_process_callback(response[UUID],
                                                     outfile_path,
                                                     cls._DB_CONNECTOR) 
                    
                    # Add to queue and update DB
                    cls._DB_CONNECTOR.insert(SA_GENOTYPER_COLLECTION, 
                                             [response])
                    cls._EXECUTION_MANAGER.add_job(response[UUID], 
                                                   genotyper_callable,
                                                   callback)

                    
                except:
                    APP_LOGGER.exception("Error processing Genotyper post request.")
                    response[ERROR] = str(sys.exc_info()[1])
                    status_code = 500
                finally:
                    if ID in response:
                        del response[ID]
           
            json_response[GENOTYPER].append(response)
            status_codes.append(status_code)


        # If all jobs submitted successfully, then 200 should be returned.
        # Otherwise, the maximum status code seems good enough.
        return make_clean_response(json_response, max(status_codes))
    
#===============================================================================
# Callable/Callback Functionality
#===============================================================================
class SaGenotyperCallable(object):
    """
    Callable that executes the genotyper command.
    """
    def __init__(self, exp_def_uuid, ac_result_path, outfile_path, 
                 required_drops, ignored_dyes, uuid, db_connector):
        self.exp_def_uuid     = exp_def_uuid
        self.ac_result_path   = ac_result_path
        self.outfile_path     = outfile_path
        self.required_drops   = required_drops
        self.ignored_dyes     = ignored_dyes
        self.db_connector     = db_connector
        self.query            = {UUID: uuid}
        self.tmp_path         = os.path.join(TMP_PATH, uuid)
        self.tmp_outfile_path = os.path.join(self.tmp_path, uuid + ".%s" % VCF)
        
    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}     
        self.db_connector.update(SA_GENOTYPER_COLLECTION, self.query, update)
        try:
            safe_make_dirs(self.tmp_path)
            
            exp_def_fetcher = ExperimentDefinitions()
            exp_def = exp_def_fetcher.get_experiment_defintion(self.exp_def_uuid)
            experiment = HotspotExperiment.from_dict(exp_def)
            GenotypeProcessor(experiment, None, self.tmp_outfile_path, 
                              required_drops=self.required_drops, 
                              in_file=self.ac_result_path,
                              ignored_dyes=self.ignored_dyes)            
            
            if not os.path.isfile(self.tmp_outfile_path):
                raise Exception("Secondary analysis genotyper job " +
                                "failed: output file not generated.")
            else:
                shutil.copy(self.tmp_outfile_path, self.outfile_path)
                shutil.copy(self.tmp_outfile_path[:-3] + PDF, self.outfile_path[:-3] + PDF)
        finally:
            # Regardless of success or failure, remove the copied archive directory
            shutil.rmtree(self.tmp_path, ignore_errors=True)

def make_process_callback(uuid, outfile_path, db_connector):
    """
    Return a closure that is fired when the job finishes. This 
    callback updates the DB with completion status, result file location, and
    an error message if applicable.
     
    @param uuid:         Unique job id in database
    @param outfile_path: Path where the final identity results will live.
    @param db_connector: Object that handles communication with the DB
    """
    query = {UUID: uuid}
    def process_callback(future):
        try:
            _ = future.result()
            update = { "$set": { 
                                 STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                 RESULT: outfile_path,
                                 PDF: outfile_path[:-3] + PDF,
                                 URL: "http://%s/results/%s/%s" % 
                                           (HOSTNAME, PORT, 
                                            os.path.basename(outfile_path)),
                                 FINISH_DATESTAMP: datetime.today(),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_GENOTYPER_COLLECTION, query, {})) > 0:
                db_connector.update(SA_GENOTYPER_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(outfile_path[:-3] + PDF)
        except:
            APP_LOGGER.exception("Error in Genotyper post request process callback.")
            error_msg = str(sys.exc_info()[1])
            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   RESULT: None,
                                   PDF: None,
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_GENOTYPER_COLLECTION, query, {})) > 0:
                db_connector.update(SA_GENOTYPER_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(outfile_path[:-3] + PDF)
         
    return process_callback

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = GenotyperPostFunction()
    print function      