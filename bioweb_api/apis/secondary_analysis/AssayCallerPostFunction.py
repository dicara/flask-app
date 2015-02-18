'''
Copyright 2015 Bio-Rad Laboratories, Inc.

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
@date:   Feb 13, 2015
'''

#=============================================================================
# Imports
#=============================================================================
import os
import shutil
import sys

from uuid import uuid4
from datetime import datetime

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.utilities.io_utilities import make_clean_response, \
    silently_remove_file, safe_make_dirs
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import SA_ASSAY_CALLER_COLLECTION, PA_PROCESS_COLLECTION, \
    TMP_PATH, RESULTS_PATH, HOSTNAME, PORT
from bioweb_api.apis.ApiConstants import UUID, JOB_NAME, JOB_STATUS, STATUS, \
    ID, FIDUCIAL_DYE, ASSAY_DYE, JOB_TYPE, JOB_TYPE_NAME, RESULT, CONFIG, \
    ERROR, PA_PROCESS_UUID, SUBMIT_DATESTAMP, NUM_PROBES, TRAINING_FACTOR, \
    START_DATESTAMP, FINISH_DATESTAMP, URL, KDE_PLOT, KDE_PLOT_URL, \
    SCATTER_PLOT, SCATTER_PLOT_URL, THRESHOLD, COV_TYPE, OUTLIERS, JOE, FAM
    
from secondary_analysis.constants import COVARIANCE_TYPES
from secondary_analysis.assay_calling.assay_call_manager import AssayCallManager

from primary_analysis.command import InvalidFileError

#=============================================================================
# Public Static Variables
#=============================================================================
ASSAY_CALLER = "AssayCaller"

#=============================================================================
# Private Static Variables
#=============================================================================
_NUM_PROBES_DESCRIPTION = "Number of unique probes used to determine size of " \
    "the required training set."
_TRAINING_FACTOR_DESCRIPTION = "Used to compute the size of the training " \
    "set: size = num_probes*training_factor."
_THRESHOLD_DESCRIPTION = "The minimum value accepted for fiducial. Values " \
    "lower than this indicate uninjected"
_OUTLIER_DESCRIPTION = "Detect and remove outliers."
_COV_TYPE_DESCRIPTION = "Type of covariance parameters to use in deriving " \
    "the GMM."

#=============================================================================
# Class
#=============================================================================
class AssayCallerPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return ASSAY_CALLER
   
    @staticmethod
    def summary():
        return "Run the equivalent of sa assay_caller."
    
    @staticmethod
    def notes():
        return ""
    
    def response_messages(self):
        msgs = super(AssayCallerPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "Job name already exists. Delete the " \
                                  "existing job or pick a new name."},
                     { "code": 404, 
                       "message": "Submission unsuccessful. No primary " \
                       "analysis jobs found matching input criteria."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        cls.job_uuid_param  = ParameterFactory.job_uuid(PA_PROCESS_COLLECTION)
        #IDENTITY JOBS AS WELL???
        cls.job_name_param  = ParameterFactory.lc_string(JOB_NAME, "Unique "\
                                                         "name to give this "
                                                         "job.")
        cls.fid_dye_param   = ParameterFactory.dye(FIDUCIAL_DYE, 
                                                   "Fiducial dye.",
                                                   default=JOE,
                                                   required=True)
        cls.assay_dye_param = ParameterFactory.dye(ASSAY_DYE, "Assay dye.",
                                                   default=FAM,
                                                   required=True)
        cls.n_probes_param  = ParameterFactory.integer(NUM_PROBES, 
                                                       _NUM_PROBES_DESCRIPTION,
                                                       default=1, minimum=1,
                                                       required=True)
        cls.training_param  = ParameterFactory.integer(TRAINING_FACTOR, 
                                                       _TRAINING_FACTOR_DESCRIPTION,
                                                       default=10, minimum=1,
                                                       required=True)
        cls.threshold_param = ParameterFactory.float(THRESHOLD,
                                                     _THRESHOLD_DESCRIPTION,
                                                     default=2500.0,
                                                     required=True)
        cls.outliers_param  = ParameterFactory.boolean(OUTLIERS,
                                                       _OUTLIER_DESCRIPTION,
                                                       default_value=False,
                                                       required=True)
        cls.cov_type_param  = ParameterFactory.lc_string(COV_TYPE, 
                                                         _COV_TYPE_DESCRIPTION,
                                                         enum=COVARIANCE_TYPES,
                                                         default=COVARIANCE_TYPES[-1],
                                                         required=True)
        
        parameters = [
                      cls.job_uuid_param,
                      cls.job_name_param,
                      cls.fid_dye_param,
                      cls.assay_dye_param,
                      cls.n_probes_param,
                      cls.training_param,
                      cls.threshold_param,
                      cls.outliers_param,
                      cls.cov_type_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        job_uuids       = params_dict[cls.job_uuid_param]
        job_name        = params_dict[cls.job_name_param][0]
        fiducial_dye    = params_dict[cls.fid_dye_param][0]
        assay_dye       = params_dict[cls.assay_dye_param][0]
        num_probes      = params_dict[cls.n_probes_param][0]
        training_factor = params_dict[cls.training_param][0]
        threshold       = params_dict[cls.threshold_param][0]
        outliers        = params_dict[cls.outliers_param][0]
        cov_type        = params_dict[cls.cov_type_param][0]
        
        json_response = {ASSAY_CALLER: []}

        # Ensure analysis job exists
        try:
            criteria        = {UUID: {"$in": job_uuids}}
            projection      = {ID: 0, RESULT: 1, UUID: 1, CONFIG: 1}
            pa_process_jobs = cls._DB_CONNECTOR.find(PA_PROCESS_COLLECTION, 
                                                     criteria, projection)
        except:
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)
        
        # Process each archive
        status_codes  = []
        for i, pa_process_job in enumerate(pa_process_jobs):
            if len(pa_process_jobs) == 1:
                cur_job_name = job_name
            else:
                cur_job_name = "%s-%d" % (job_name, i)

            response = {
                        FIDUCIAL_DYE: fiducial_dye,
                        ASSAY_DYE: assay_dye,
                        NUM_PROBES: num_probes,
                        TRAINING_FACTOR: training_factor,
                        THRESHOLD: threshold,
                        OUTLIERS: outliers,
                        COV_TYPE: cov_type,
                        UUID: str(uuid4()),
                        PA_PROCESS_UUID: pa_process_job[UUID],
                        STATUS: JOB_STATUS.submitted,     # @UndefinedVariable
                        JOB_NAME: cur_job_name,
                        JOB_TYPE_NAME: JOB_TYPE.sa_assay_calling, # @UndefinedVariable
                        SUBMIT_DATESTAMP: datetime.today(),
                       }
            status_code = 200
            
            if cur_job_name in cls._DB_CONNECTOR.distinct(SA_ASSAY_CALLER_COLLECTION, 
                                                          JOB_NAME):
                status_code = 403
            else:
                try:
                    outfile_path  = os.path.join(RESULTS_PATH, response[UUID])
                    kde_plot_path = os.path.join(RESULTS_PATH, 
                                                 response[UUID] + "_kde.png")
                    scatter_plot_path = os.path.join(RESULTS_PATH, 
                                                response[UUID] + "_scatter.png")
                    
                    if not os.path.isfile(pa_process_job[RESULT]):
                        raise InvalidFileError(pa_process_job[RESULT])
                    
                    # Create helper functions
                    sac_callable = SaAssayCallerCallable(pa_process_job[RESULT],
                                                         assay_dye,
                                                         fiducial_dye,
                                                         num_probes, 
                                                         training_factor,
                                                         threshold,
                                                         outliers,
                                                         cov_type,
                                                         outfile_path, 
                                                         kde_plot_path,
                                                         scatter_plot_path,
                                                         response[UUID], 
                                                         cls._DB_CONNECTOR)
                    callback = make_process_callback(response[UUID], 
                                                     outfile_path,
                                                     kde_plot_path,
                                                     scatter_plot_path,
                                                     cls._DB_CONNECTOR)
                    # Add to queue and update DB
                    cls._DB_CONNECTOR.insert(SA_ASSAY_CALLER_COLLECTION, 
                                             [response])
                    cls._EXECUTION_MANAGER.add_job(response[UUID], sac_callable,
                                                   callback)
                    
                except:
                    response[ERROR] = str(sys.exc_info()[1])
                    status_code = 500
                finally:
                    if ID in response:
                        del response[ID]
                    
            json_response[ASSAY_CALLER].append(response)
            status_codes.append(status_code)
        
        # If all jobs submitted successfully, then 200 should be returned.
        # Otherwise, the maximum status code seems good enough.
        return make_clean_response(json_response, max(status_codes))
                    
#===============================================================================
# Callable/Callback Functionality
#===============================================================================
class SaAssayCallerCallable(object):
    """
    Callable that executes the absorption command.
    """
    def __init__(self, analysis_file, assay_dye, fiducial_dye, num_probes, 
                 training_factor, threshold, outliers, cov_type, outfile_path,
                 kde_plot_path, scatter_plot_path, uuid, db_connector):
        self.analysis_file         = analysis_file
        self.assay_dye             = assay_dye
        self.fiducial_dye          = fiducial_dye
        self.num_probes            = num_probes
        self.training_factor       = training_factor
        self.threshold             = threshold
        self.outliers              = outliers
        self.cov_type              = cov_type
        self.outfile_path          = outfile_path
        self.kde_plot_path         = kde_plot_path
        self.scatter_plot_path     = scatter_plot_path
        self.db_connector          = db_connector
        self.query                 = {UUID: uuid}
        self.tmp_path              = os.path.join(TMP_PATH, uuid)
        self.tmp_outfile_path      = os.path.join(self.tmp_path, 
                                                  "assay_calls.txt")
        self.tmp_kde_plot_path     = os.path.join(self.tmp_path, 
                                                  "assay_calls_kde.png")
        self.tmp_scatter_plot_path = os.path.join(self.tmp_path, 
                                                  "assay_calls_scatter.png")
     
    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}     
        self.db_connector.update(SA_ASSAY_CALLER_COLLECTION, self.query, update)
        
        try:
            safe_make_dirs(self.tmp_path)
            
            AssayCallManager(self.num_probes, in_file=self.analysis_file, 
                             out_file=self.tmp_outfile_path, 
                             kde_plot_file=self.tmp_kde_plot_path,
                             scatter_plot_file=self.tmp_scatter_plot_path,
                             training_size=self.training_factor,
                             assay=self.assay_dye, fiducial=self.fiducial_dye,
                             threshold=self.threshold, outliers=self.outliers,
                             cov_type=self.cov_type)
            
            if not os.path.isfile(self.tmp_outfile_path):
                raise Exception("Secondary analysis assay caller job " +
                                "failed: output file not generated.")
            else:
                shutil.copy(self.tmp_outfile_path, self.outfile_path)
            if os.path.isfile(self.tmp_kde_plot_path):
                shutil.copy(self.tmp_kde_plot_path, self.kde_plot_path)
            if os.path.isfile(self.tmp_scatter_plot_path):
                shutil.copy(self.tmp_scatter_plot_path, self.scatter_plot_path)
        finally:
            # Regardless of success or failure, remove the copied archive directory
            shutil.rmtree(self.tmp_path, ignore_errors=True)
        
         
def make_process_callback(uuid, outfile_path, kde_plot_path, scatter_plot_path, 
                          db_connector):
    """
    Return a closure that is fired when the job finishes. This 
    callback updates the DB with completion status, result file location, and
    an error message if applicable.
     
    @param uuid:         Unique job id in database
    @param outfile_path: Path where the final identity results will live.
    @param plot_path:    Path where the final PNG plot should live.
    @param db_connector: Object that handles communication with the DB
    """
    query = {UUID: uuid}
    def process_callback(future):
        try:
            _ = future.result()
            update = { "$set": { 
                                 STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                 RESULT: outfile_path,
                                 URL: "http://%s/results/%s/%s" % 
                                           (HOSTNAME, PORT, 
                                            os.path.basename(outfile_path)),
                                 KDE_PLOT: kde_plot_path,
                                 KDE_PLOT_URL: "http://%s/results/%s/%s" % 
                                           (HOSTNAME, PORT, 
                                            os.path.basename(kde_plot_path)),
                                 SCATTER_PLOT: scatter_plot_path,
                                 SCATTER_PLOT_URL: "http://%s/results/%s/%s" % 
                                           (HOSTNAME, PORT, 
                                            os.path.basename(scatter_plot_path)),
                                 FINISH_DATESTAMP: datetime.today(),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_ASSAY_CALLER_COLLECTION, query, {})) > 0:
                db_connector.update(SA_ASSAY_CALLER_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(kde_plot_path)
                silently_remove_file(scatter_plot_path)
        except:
            error_msg = str(sys.exc_info()[1])
            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   RESULT: None,
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_ASSAY_CALLER_COLLECTION, query, {})) > 0:
                db_connector.update(SA_ASSAY_CALLER_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(kde_plot_path)
                silently_remove_file(scatter_plot_path)
         
    return process_callback
            
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = AssayCallerPostFunction()
    print function      