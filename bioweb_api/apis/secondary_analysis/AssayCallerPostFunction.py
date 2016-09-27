'''
Copyright 2015 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Dan DiCara
@date:   Feb 13, 2015
'''

#=============================================================================
# Imports
#=============================================================================
import copy
import os
import shutil
import sys
import traceback

from uuid import uuid4
from datetime import datetime

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.utilities.io_utilities import make_clean_response, \
    silently_remove_file, safe_make_dirs, get_results_folder, get_results_url
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import SA_ASSAY_CALLER_COLLECTION, SA_IDENTITY_COLLECTION
from bioweb_api import TMP_PATH
from bioweb_api.apis.ApiConstants import UUID, JOB_NAME, JOB_STATUS, STATUS, \
    ID, FIDUCIAL_DYE, ASSAY_DYE, JOB_TYPE, JOB_TYPE_NAME, RESULT, \
    ERROR, SA_IDENTITY_UUID, SUBMIT_DATESTAMP, NUM_PROBES, TRAINING_FACTOR, \
    START_DATESTAMP, FINISH_DATESTAMP, URL, SCATTER_PLOT, SCATTER_PLOT_URL, \
    JOE, FAM, EXP_DEF_NAME, CTRL_THRESH, NUM_PROBES_DESCRIPTION, \
    TRAINING_FACTOR_DESCRIPTION, CTRL_THRESH_DESCRIPTION

from expdb import HotspotExperiment
from primary_analysis.command import InvalidFileError
from primary_analysis.experiment.experiment_definitions import ExperimentDefinitions
from secondary_analysis.assay_calling.assay_call_manager import AssayCallManager
from secondary_analysis.constants import AC_TRAINING_FACTOR, AC_CTRL_THRESHOLD

#=============================================================================
# Public Static Variables
#=============================================================================
ASSAY_CALLER = 'AssayCaller'


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
        return 'Run the equivalent of sa assay_caller.'

    @staticmethod
    def notes():
        return ''

    def response_messages(self):
        msgs = super(AssayCallerPostFunction, self).response_messages()
        msgs.extend([
                     { 'code': 403,
                       'message': 'Job name already exists. Delete the ' \
                                  'existing job or pick a new name.'},
                     { 'code': 404,
                       'message': 'Submission unsuccessful. No primary ' \
                       'analysis jobs found matching input criteria.'},
                    ])
        return msgs

    @classmethod
    def parameters(cls):
        cls.job_uuid_param  = ParameterFactory.job_uuid(SA_IDENTITY_COLLECTION)
        cls.job_name_param  = ParameterFactory.lc_string(JOB_NAME, 'Unique '\
                                                         'name to give this '
                                                         'job.')
        cls.exp_defs_param  = ParameterFactory.experiment_definition()
        cls.fid_dye_param   = ParameterFactory.dye(FIDUCIAL_DYE,
                                                   'Fiducial dye.',
                                                   default=JOE,
                                                   required=True)
        cls.assay_dye_param = ParameterFactory.dye(ASSAY_DYE, 'Assay dye.',
                                                   default=FAM,
                                                   required=True)
        cls.n_probes_param  = ParameterFactory.integer(NUM_PROBES,
                                                       NUM_PROBES_DESCRIPTION,
                                                       default=1, minimum=1,
                                                       required=True)
        cls.training_param  = ParameterFactory.integer(TRAINING_FACTOR,
                                                       TRAINING_FACTOR_DESCRIPTION,
                                                       default=AC_TRAINING_FACTOR, minimum=1,
                                                       required=True)
        cls.ctrl_thresh     = ParameterFactory.float(CTRL_THRESH,
                                                     CTRL_THRESH_DESCRIPTION,
                                                     default=AC_CTRL_THRESHOLD,
                                                     minimum=0.0, maximum=100.0)

        parameters = [
                      cls.job_uuid_param,
                      cls.job_name_param,
                      cls.exp_defs_param,
                      cls.fid_dye_param,
                      cls.assay_dye_param,
                      cls.n_probes_param,
                      cls.training_param,
                      cls.ctrl_thresh,
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        job_uuids       = params_dict[cls.job_uuid_param]
        job_name        = params_dict[cls.job_name_param][0]
        exp_def_name    = params_dict[cls.exp_defs_param][0]
        fiducial_dye    = params_dict[cls.fid_dye_param][0]
        assay_dye       = params_dict[cls.assay_dye_param][0]
        num_probes      = params_dict[cls.n_probes_param][0]
        training_factor = params_dict[cls.training_param][0]
        ctrl_thresh     = params_dict[cls.ctrl_thresh][0]

        json_response = {ASSAY_CALLER: []}

        # Ensure analysis job exists
        try:
            criteria        = {UUID: {'$in': job_uuids}}
            projection      = {ID: 0, RESULT: 1, UUID: 1}
            sa_identity_jobs = cls._DB_CONNECTOR.find(SA_IDENTITY_COLLECTION,
                                                     criteria, projection)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)

        # Process each archive
        status_codes  = []
        for i, sa_identity_job in enumerate(sa_identity_jobs):
            if len(sa_identity_jobs) == 1:
                cur_job_name = job_name
            else:
                cur_job_name = '%s-%d' % (job_name, i)


            status_code = 200

            if cur_job_name in cls._DB_CONNECTOR.distinct(SA_ASSAY_CALLER_COLLECTION,
                                                          JOB_NAME):
                status_code = 403
                json_response[ASSAY_CALLER].append({ERROR: 'Job exists.'})
            else:
                try:
                    if not os.path.isfile(sa_identity_job[RESULT]):
                        raise InvalidFileError(sa_identity_job[RESULT])

                    # Create helper functions
                    sac_callable = SaAssayCallerCallable(sa_identity_job[UUID],
                                                         exp_def_name,
                                                         assay_dye,
                                                         fiducial_dye,
                                                         num_probes,
                                                         training_factor,
                                                         ctrl_thresh,
                                                         cls._DB_CONNECTOR,
                                                         cur_job_name)
                    response = copy.deepcopy(sac_callable.document)
                    callback = make_process_callback(sac_callable.uuid,
                                                     sac_callable.outfile_path,
                                                     sac_callable.scatter_plot_path,
                                                     cls._DB_CONNECTOR)
                    # Add to queue
                    cls._EXECUTION_MANAGER.add_job(response[UUID], sac_callable,
                                                   callback)

                except:
                    APP_LOGGER.exception(traceback.format_exc())
                    response = {JOB_NAME: cur_job_name, ERROR: str(sys.exc_info()[1])}
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
    '''
    Callable that executes the assay caller command.
    '''
    def __init__(self, identity_uuid, exp_def_name, assay_dye, fiducial_dye,
                 num_probes, training_factor, ctrl_thresh, db_connector, job_name):
        identity_doc = db_connector.find_one(SA_IDENTITY_COLLECTION, UUID, identity_uuid)

        self.uuid = str(uuid4())
        self.exp_def_name          = exp_def_name
        self.analysis_file         = identity_doc[RESULT]
        self.num_probes            = num_probes
        self.training_factor       = training_factor
        self.assay_dye             = assay_dye
        self.fiducial_dye          = fiducial_dye
        self.db_connector          = db_connector
        self.job_name              = job_name
        self.ctrl_thresh           = ctrl_thresh

        results_folder             = get_results_folder()
        self.outfile_path          = os.path.join(results_folder, self.uuid)
        self.scatter_plot_path     = os.path.join(results_folder, self.uuid + '_scatter.png')
        self.tmp_path              = os.path.join(TMP_PATH, self.uuid)
        self.tmp_outfile_path      = os.path.join(self.tmp_path,
                                                  'assay_calls.txt')
        self.tmp_scatter_plot_path = os.path.join(self.tmp_path,
                                                  'assay_calls_scatter.png')
        self.document = {
                        EXP_DEF_NAME: exp_def_name,
                        FIDUCIAL_DYE: fiducial_dye,
                        ASSAY_DYE: assay_dye,
                        NUM_PROBES: num_probes,
                        TRAINING_FACTOR: training_factor,
                        CTRL_THRESH: ctrl_thresh,
                        UUID: self.uuid,
                        SA_IDENTITY_UUID: identity_uuid,
                        STATUS: JOB_STATUS.submitted,     # @UndefinedVariable
                        JOB_NAME: job_name,
                        JOB_TYPE_NAME: JOB_TYPE.sa_assay_calling, # @UndefinedVariable
                        SUBMIT_DATESTAMP: datetime.today(),
                       }
        if job_name in self.db_connector.distinct(SA_ASSAY_CALLER_COLLECTION, JOB_NAME):
            raise Exception('Job name %s already exists in assay caller collection' % job_name)

        self.db_connector.insert(SA_ASSAY_CALLER_COLLECTION, [self.document])


    def __call__(self):
        update = {'$set': {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}
        query = {UUID: self.uuid}
        self.db_connector.update(SA_ASSAY_CALLER_COLLECTION, query, update)

        try:
            safe_make_dirs(self.tmp_path)

            exp_def_fetcher = ExperimentDefinitions()
            exp_def_uuid = exp_def_fetcher.get_experiment_uuid(self.exp_def_name)
            exp_def = exp_def_fetcher.get_experiment_defintion(exp_def_uuid)
            experiment = HotspotExperiment.from_dict(exp_def)

            AssayCallManager(self.num_probes, in_file=self.analysis_file,
                             out_file=self.tmp_outfile_path,
                             scatter_plot_file=self.tmp_scatter_plot_path,
                             training_factor=self.training_factor,
                             assay=self.assay_dye, fiducial=self.fiducial_dye,
                             controls=experiment.controls.barcodes,
                             ctrl_thresh=self.ctrl_thresh,
                             n_jobs=8)

            if not os.path.isfile(self.tmp_outfile_path):
                raise Exception('Secondary analysis assay caller job ' +
                                'failed: output file not generated.')
            else:
                shutil.copy(self.tmp_outfile_path, self.outfile_path)
            if os.path.isfile(self.tmp_scatter_plot_path):
                shutil.copy(self.tmp_scatter_plot_path, self.scatter_plot_path)
        finally:
            # Regardless of success or failure, remove the copied archive directory
            shutil.rmtree(self.tmp_path, ignore_errors=True)


def make_process_callback(uuid, outfile_path, scatter_plot_path, db_connector):
    '''
    Return a closure that is fired when the job finishes. This
    callback updates the DB with completion status, result file location, and
    an error message if applicable.

    @param uuid:         Unique job id in database
    @param outfile_path: Path where the final identity results will live.
    @param plot_path:    Path where the final PNG plot should live.
    @param db_connector: Object that handles communication with the DB
    '''
    query = {UUID: uuid}
    def process_callback(future):
        try:
            _ = future.result()
            update = { '$set': {
                                 STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                 RESULT: outfile_path,
                                 URL: get_results_url(outfile_path),
                                 SCATTER_PLOT: scatter_plot_path,
                                 SCATTER_PLOT_URL: get_results_url(scatter_plot_path),
                                 FINISH_DATESTAMP: datetime.today(),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_ASSAY_CALLER_COLLECTION, query, {})) > 0:
                db_connector.update(SA_ASSAY_CALLER_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(scatter_plot_path)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            error_msg = str(sys.exc_info()[1])
            update    = { '$set': {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   RESULT: None,
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_ASSAY_CALLER_COLLECTION, query, {})) > 0:
                db_connector.update(SA_ASSAY_CALLER_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(scatter_plot_path)

    return process_callback

#===============================================================================
# Run Main
#===============================================================================
if __name__ == '__main__':
    function = AssayCallerPostFunction()
    print function
