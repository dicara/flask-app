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
import pandas
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
from bioweb_api import SA_ASSAY_CALLER_COLLECTION, SA_IDENTITY_COLLECTION, \
    FA_PROCESS_COLLECTION, RUN_REPORT_COLLECTION, RUN_REPORT_PATH
from bioweb_api import TMP_PATH
from bioweb_api.apis.ApiConstants import UUID, JOB_NAME, JOB_STATUS, STATUS, \
    ID, PICO2_DYE, ASSAY_DYE, JOB_TYPE, JOB_TYPE_NAME, RESULT, \
    ERROR, SA_IDENTITY_UUID, SUBMIT_DATESTAMP, NUM_PROBES, TRAINING_FACTOR, \
    START_DATESTAMP, FINISH_DATESTAMP, URL, SCATTER_PLOT, SCATTER_PLOT_URL, \
    EXP_DEF_NAME, CTRL_THRESH, TRAINING_FACTOR_DESCRIPTION, \
    CTRL_THRESH_DESCRIPTION, CTRL_FILTER, CTRL_FILTER_DESCRIPTION, AC_METHOD, \
    AC_METHOD_DESCRIPTION, PICO1_DYE, DYES_SCATTER_PLOT, \
    DYES_SCATTER_PLOT_URL, AC_MODEL, AC_MODEL_DESCRIPTION, ARCHIVE, \
    IMAGE_STACKS, ID_DOCUMENT
from bioweb_api.apis.run_info.constants import DIR_PATH

from primary_analysis.command import InvalidFileError
from primary_analysis.pa_utils import sniff_delimiter
from gbutils.exp_def.exp_def_handler import ExpDefHandler
from secondary_analysis.assay_calling.assay_call_manager import AssayCallManager
from secondary_analysis.constants import AC_TRAINING_FACTOR, AC_CTRL_THRESHOLD
from secondary_analysis.assay_calling.assay_caller_plotting import generate_dye_scatterplots
from secondary_analysis.assay_calling.classifier_utils import available_models, \
    MODEL_FILES
from secondary_analysis.parsers.system_listener_parser import (
    ChannelOffsetTopicParser, 
    ClampTempTopicParser, 
    DynamicAlignStepsParser, 
    OldChannelOffsetTopicParser,
    SystemListenerParser,
)

#=============================================================================
# Public Static Variables
#=============================================================================
ASSAY_CALLER = 'AssayCaller'
SYS_LISTENER = 'sysListener.json'

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
        cls.training_param  = ParameterFactory.integer(TRAINING_FACTOR,
                                                       TRAINING_FACTOR_DESCRIPTION,
                                                       default=AC_TRAINING_FACTOR, minimum=1,
                                                       required=True)
        cls.ctrl_thresh     = ParameterFactory.float(CTRL_THRESH,
                                                     CTRL_THRESH_DESCRIPTION,
                                                     default=AC_CTRL_THRESHOLD,
                                                     minimum=0.0, maximum=100.0)
        cls.ctrl_filter     = ParameterFactory.boolean(CTRL_FILTER,
                                                       CTRL_FILTER_DESCRIPTION,
                                                       default_value=False,
                                                       required=True)
        cls.ac_method       = ParameterFactory.ac_method(AC_METHOD, AC_METHOD_DESCRIPTION)
        cls.ac_model        = ParameterFactory.cs_string(AC_MODEL,
                                                         AC_MODEL_DESCRIPTION,
                                                         required=False,
                                                         enum=[m for model_dict in MODEL_FILES.values()
                                                               for m in model_dict])

        parameters = [
                      cls.job_uuid_param,
                      cls.job_name_param,
                      cls.exp_defs_param,
                      cls.training_param,
                      cls.ctrl_thresh,
                      cls.ctrl_filter,
                      cls.ac_method,
                      cls.ac_model,
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        job_uuids       = params_dict[cls.job_uuid_param]
        job_name        = params_dict[cls.job_name_param][0]
        exp_def_name    = params_dict[cls.exp_defs_param][0]
        training_factor = params_dict[cls.training_param][0]
        ctrl_thresh     = params_dict[cls.ctrl_thresh][0]
        ctrl_filter     = params_dict[cls.ctrl_filter][0]
        ac_method = params_dict[cls.ac_method][0]

        ac_model = None
        if cls.ac_model in params_dict and params_dict[cls.ac_model][0]:
            ac_model = params_dict[cls.ac_model][0]

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
                                                         training_factor,
                                                         ctrl_thresh,
                                                         cls._DB_CONNECTOR,
                                                         cur_job_name,
                                                         ctrl_filter,
                                                         ac_method,
                                                         ac_model)
                    response = copy.deepcopy(sac_callable.document)
                    callback = make_process_callback(sac_callable.uuid,
                                                     sac_callable.outfile_path,
                                                     sac_callable.scatter_plot_path,
                                                     sac_callable.dyes_plot_path,
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
    def __init__(self, identity_uuid, exp_def_name, training_factor,
                 ctrl_thresh, db_connector, job_name, ctrl_filter,
                 ac_method, ac_model):

        identity_doc = db_connector.find_one(SA_IDENTITY_COLLECTION, UUID, identity_uuid)

        self.uuid = str(uuid4())
        self.exp_def_name          = exp_def_name
        self.analysis_file         = identity_doc[RESULT]
        self.num_probes            = identity_doc[NUM_PROBES]
        self.training_factor       = training_factor
        self.pico1_dye             = identity_doc[PICO1_DYE]
        self.pico2_dye             = identity_doc[PICO2_DYE]
        self.assay_dye             = identity_doc[ASSAY_DYE]
        self.db_connector          = db_connector
        self.job_name              = job_name
        self.ctrl_thresh           = ctrl_thresh
        self.ctrl_filter           = ctrl_filter
        self.ac_method             = ac_method
        self.ac_model              = ac_model

        results_folder             = get_results_folder()
        self.outfile_path          = os.path.join(results_folder, self.uuid)
        self.scatter_plot_path     = os.path.join(results_folder, self.uuid + '_scatter.png')
        self.dyes_plot_path        = os.path.join(results_folder, self.uuid + '_dyes_scatter.png')
        self.tmp_path              = os.path.join(TMP_PATH, self.uuid)
        self.tmp_outfile_path      = os.path.join(self.tmp_path,
                                                  'assay_calls.txt')
        self.tmp_scatter_plot_path = os.path.join(self.tmp_path,
                                                  'assay_calls_scatter.png')
        self.tmp_sys_listener_path = os.path.join(self.tmp_path, SYS_LISTENER)
        self.tmp_dyes_plot_path    = os.path.join(self.tmp_path,
                                                  'assay_calls_dyes_scatter.png')
        self.document = {
                        EXP_DEF_NAME: exp_def_name,
                        PICO1_DYE: self.pico1_dye,
                        PICO2_DYE: self.pico2_dye,
                        ASSAY_DYE: self.assay_dye,
                        NUM_PROBES: self.num_probes,
                        TRAINING_FACTOR: training_factor,
                        CTRL_THRESH: ctrl_thresh,
                        UUID: self.uuid,
                        SA_IDENTITY_UUID: identity_uuid,
                        STATUS: JOB_STATUS.submitted,     # @UndefinedVariable
                        JOB_NAME: job_name,
                        JOB_TYPE_NAME: JOB_TYPE.sa_assay_calling, # @UndefinedVariable
                        SUBMIT_DATESTAMP: datetime.today(),
                        CTRL_FILTER: ctrl_filter,
                        AC_METHOD: ac_method,
                        AC_MODEL: ac_model,
                       }
        if job_name in self.db_connector.distinct(SA_ASSAY_CALLER_COLLECTION, JOB_NAME):
            raise Exception('Job name %s already exists in assay caller collection' % job_name)

        self.db_connector.insert(SA_ASSAY_CALLER_COLLECTION, [self.document])


    def __call__(self):
        update = {'$set': {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}
        query = {UUID: self.uuid}
        self.db_connector.update(SA_ASSAY_CALLER_COLLECTION, query, update)

        def gen_dye_scatterplot(dyes, sys_listener_path):
            try:
                analysis_df = pandas.read_table(self.analysis_file,
                    sep=sniff_delimiter(self.analysis_file))
                ac_df = pandas.read_table(self.tmp_outfile_path,
                    sep=sniff_delimiter(self.tmp_outfile_path))
                analysis_df['assay'] = False
                analysis_df.loc[analysis_df['identity'].notnull(), 'assay'] = ac_df['assay'].values

                # System listener inputs
                dyn_align_offsets = {}
                temps = {}
                steps = {}
                if sys_listener_path is not None:
                    sys_listener_dir = os.path.dirname(sys_listener_path)
                    clamp_temp_tp = ClampTempTopicParser()
                    old_channel_offset_tp = OldChannelOffsetTopicParser()
                    channel_offset_tp = ChannelOffsetTopicParser()
                    dyn_align_steps_tp = DynamicAlignStepsParser()
                    topic_parsers = [clamp_temp_tp, old_channel_offset_tp, 
                        channel_offset_tp, dyn_align_steps_tp]
                    sys_listener_parser = SystemListenerParser(sys_listener_dir, 
                        topic_parsers=topic_parsers)
                    temps = sys_listener_parser.get_topic_results(clamp_temp_tp.topic)
                    dyn_align_offsets = sys_listener_parser.get_topic_results(channel_offset_tp.topic)
                    if len(dyn_align_offsets) < 1:
                        APP_LOGGER.info("Using old channel offset parser...")
                        dyn_align_offsets = sys_listener_parser.get_topic_results(old_channel_offset_tp.topic)
                    else:
                        APP_LOGGER.info("Using new channel offset parser...")
                    steps = sys_listener_parser.get_topic_results(dyn_align_steps_tp.topic)

                generate_dye_scatterplots(analysis_df, dyes,
                    self.tmp_dyes_plot_path, self.job_name, self.pico1_dye,
                    dyn_align_offsets=dyn_align_offsets, temps=temps, 
                    steps=steps)
                shutil.copy(self.tmp_dyes_plot_path, self.dyes_plot_path)
                APP_LOGGER.info("Dyes scatter plot generated for %s." % \
                    self.job_name)
            except:
                APP_LOGGER.exception("Dyes scatter plot generation failed.")

        try:
            safe_make_dirs(self.tmp_path)

            exp_def_fetcher = ExpDefHandler()
            experiment = exp_def_fetcher.get_experiment_definition(self.exp_def_name)

            model_file_dict = available_models(self.ac_method)
            if self.ac_model is None:
                classifier_file = None
            else:
                if self.ac_model in model_file_dict:
                    classifier_file = model_file_dict[self.ac_model]
                else:
                    APP_LOGGER.exception("Assay caller model %s is unavailable for method %s."
                                         % (self.ac_method ,self.ac_model))
                    raise Exception("Assay caller model %s is unavailable for method %s."
                                    % (self.ac_method ,self.ac_model))

            AssayCallManager(self.num_probes, in_file=self.analysis_file,
                             out_file=self.tmp_outfile_path,
                             scatter_plot_file=self.tmp_scatter_plot_path,
                             training_factor=self.training_factor,
                             assay=self.assay_dye,
                             fiducial=self.pico2_dye,
                             controls=experiment.negative_controls.barcodes,
                             ctrl_thresh=self.ctrl_thresh,
                             n_jobs=8,
                             controls_filtering=self.ctrl_filter,
                             assay_type=self.ac_method,
                             classifier_file=classifier_file)

            if not os.path.isfile(self.tmp_outfile_path):
                raise Exception('Secondary analysis assay caller job ' +
                                'failed: output file not generated.')

            shutil.copy(self.tmp_outfile_path, self.outfile_path)
            gen_dye_scatterplot(experiment.dyes, self.get_sys_listener_path())

            if os.path.isfile(self.tmp_scatter_plot_path):
                shutil.copy(self.tmp_scatter_plot_path, self.scatter_plot_path)
        finally:
            # Regardless of success or failure, remove the copied archive directory
            shutil.rmtree(self.tmp_path, ignore_errors=True)

    def get_sys_listener_path(self):
        """
        Return system listener path if found, otherwise return None.
        """
        full_analysis_doc = self.db_connector.find_one(FA_PROCESS_COLLECTION, 
            '.'.join([ID_DOCUMENT, UUID]), self.document[SA_IDENTITY_UUID])
        if full_analysis_doc is None: 
            return None

        run_report = self.db_connector.find_one(RUN_REPORT_COLLECTION,
            IMAGE_STACKS, full_analysis_doc[ARCHIVE])
        if run_report is None:
            return None

        report_dir = run_report.get(DIR_PATH)
        if report_dir is None:
            return None

        sys_listener_path = os.path.join(RUN_REPORT_PATH, report_dir,
            SYS_LISTENER)
        if os.path.isfile(sys_listener_path):
            shutil.copy(sys_listener_path, self.tmp_sys_listener_path)
            return self.tmp_sys_listener_path

        return None


def make_process_callback(uuid, outfile_path, scatter_plot_path,
    dyes_scatter_plot_path, db_connector):
    '''
    Return a closure that is fired when the job finishes. This
    callback updates the DB with completion status, result file location, and
    an error message if applicable.

    @param uuid:         Unique job id in database
    @param outfile_path: Path where the final assay caller results will live.
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
                                 DYES_SCATTER_PLOT: dyes_scatter_plot_path,
                                 DYES_SCATTER_PLOT_URL: get_results_url(dyes_scatter_plot_path),
                                 FINISH_DATESTAMP: datetime.today(),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_ASSAY_CALLER_COLLECTION, query, {})) > 0:
                db_connector.update(SA_ASSAY_CALLER_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(scatter_plot_path)
                silently_remove_file(dyes_scatter_plot_path)
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
                silently_remove_file(dyes_scatter_plot_path)

    return process_callback

#===============================================================================
# Run Main
#===============================================================================
if __name__ == '__main__':
    function = AssayCallerPostFunction()
    print function
