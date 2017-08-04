'''
Copyright 2016 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Nathan Brown
@date:   March 28, 2016
'''

#=============================================================================
# Imports
#=============================================================================
import copy
from datetime import datetime
import sys
import traceback

from bioweb_api import FA_PROCESS_COLLECTION
from bioweb_api.apis.ApiConstants import ERROR, FINISH_DATESTAMP, \
    ID, UUID, JOB_NAME, MAJOR, MINOR, OFFSETS, USE_IID, PICO2_DYE, STATUS, \
    ASSAY_DYE, NUM_PROBES, AC_TRAINING_FACTOR, IGNORED_DYES, FILTERED_DYES, \
    UI_THRESHOLD, ID_TRAINING_FACTOR, REQUIRED_DROPS, CONTINUOUS_PHASE, \
    NUM_PROBES_DESCRIPTION, TRAINING_FACTOR_DESCRIPTION, CONTINUOUS_PHASE_DESCRIPTION, \
    UI_THRESHOLD_DESCRIPTION, REQ_DROPS_DESCRIPTION, ARCHIVE, DEFAULT_DEV_MODE, \
    PA_DATA_SOURCE, CTRL_THRESH, CTRL_THRESH_DESCRIPTION, JOB_STATUS, VARIANT_MASK, \
    IS_HDF5, MAX_UNINJECTED_RATIO, MAX_UI_RATIO_DESCRIPTION, IGNORE_LOWEST_BARCODE, \
    IGNORE_LOWEST_BARCODE_DESCRIPTION, CTRL_FILTER, CTRL_FILTER_DESCRIPTION, \
    AC_METHOD_DESCRIPTION, AC_METHOD, USE_PICO1_FILTER, DEV_MODE, \
    USE_PICO1_FILTER_DESCRIPTION, PICO1_DYE, AC_MODEL, AC_MODEL_DESCRIPTION, \
    DRIFT_COMPENSATE, DEFAULT_DRIFT_COMPENSATE, USE_PICO2_FILTER, USE_PICO2_FILTER_DESCRIPTION, \
    PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT, GT_DOCUMENT, EP_DOCUMENT, URL, EXP_DEF, \
    SUCCEEDED, BEST_EXIST_JOB

from bioweb_api.apis.full_analysis.FullAnalysisWorkflow import FullAnalysisWorkFlowCallable
from bioweb_api.apis.full_analysis.FullAnalysisUtils import convert_param_name
from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.primary_analysis.PrimaryAnalysisUtils import parse_pa_data_src
from primary_analysis.dye_model import DEFAULT_OFFSETS

from secondary_analysis.constants import ID_TRAINING_FACTOR as DEFAULT_ID_TRAINING_FACTOR
from secondary_analysis.constants import AC_TRAINING_FACTOR as DEFAULT_AC_TRAINING_FACTOR
from secondary_analysis.constants import ASSAY_DYE as DEFAULT_ASSAY_DYE
from secondary_analysis.constants import PICO2_DYE as DEFAULT_PICO2_DYE
from secondary_analysis.constants import UNINJECTED_THRESHOLD as DEFAULT_UNINJECTED_THRESHOLD
from secondary_analysis.constants import UNINJECTED_RATIO as DEFAULT_UNINJECTED_RATIO
from secondary_analysis.constants import AC_CTRL_THRESHOLD as DEFAULT_AC_CTRL_THRESHOLD
from secondary_analysis.assay_calling.classifier_utils import available_models, \
    MODEL_FILES

FULL_ANALYSIS = 'FullAnalysis'

#===============================================================================
# Class
#===============================================================================
class FullAnalysisPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return FULL_ANALYSIS

    @staticmethod
    def summary():
        return 'Run full analysis jobs.'

    @staticmethod
    def notes():
        return ''

    def response_messages(self):
        msgs = super(FullAnalysisPostFunction, self).response_messages()
        msgs.extend([
                     { 'code': 403,
                       'message': 'Job with the same parameters already exists.'},
                     { 'code': 404,
                       'message': 'Submission unsuccessful.'},
                    ])
        return msgs

    @classmethod
    def parameters(cls):
        # required parameters
        cls.job_name_param = ParameterFactory.lc_string(JOB_NAME,
                                                        'Unique name for this job.',
                                                        required=True)
        cls.exp_def_param   = ParameterFactory.experiment_definition()
        cls.mask_param     = ParameterFactory.cs_string(VARIANT_MASK,
                                                        'Mask code for variant selection.',
                                                        required=False)

        # primary analysis parameters
        cls.pa_data_src_param = ParameterFactory.cs_string(PA_DATA_SOURCE,
                                                        "Primary analysis data source (HDF5 or image stack).",
                                                        required=True)
        cls.dyes_param     = ParameterFactory.dyes(required=False)
        cls.device_param   = ParameterFactory.device(required=False,
                                                     default='katahdin')
        cls.major_param    = ParameterFactory.integer(MAJOR,
                                                      'Major dye version',
                                                      minimum=0,
                                                      required=False,
                                                      default=1)
        cls.minor_param    = ParameterFactory.integer(MINOR,
                                                      'Minor dye version',
                                                      minimum=0,
                                                      required=False,
                                                      default=0)
        cls.offset         = ParameterFactory.integer(OFFSETS,
                                                      'Offset used to infer a dye model.',
                                                      default=abs(DEFAULT_OFFSETS[0]),
                                                      minimum=1,
                                                      required=False)
        cls.use_iid_param  = ParameterFactory.boolean(USE_IID,
                                                      'Use IID Peak Detection.',
                                                      default_value=False,
                                                      required=False)

        # identity parameters
        cls.dye_levels_param    = ParameterFactory.dye_levels(required=False)
        cls.ignored_dyes_param  = ParameterFactory.dyes(name=IGNORED_DYES,
                                                       required=False)
        cls.filtered_dyes_param = ParameterFactory.dyes(name=FILTERED_DYES,
                                                        required=False)
        cls.pico1_dye_param       = ParameterFactory.dye(PICO1_DYE,
                                                      'picoinjection 1 dye.',
                                                      required=False,
                                                      default=None)
        cls.pico2_dye_param       = ParameterFactory.dye(PICO2_DYE,
                                                      'picoinjection 2 dye.',
                                                      required=False,
                                                      default=DEFAULT_PICO2_DYE)
        cls.assay_dye_param     = ParameterFactory.dye(ASSAY_DYE,
                                                      'Assay dye.',
                                                      required=False,
                                                      default=DEFAULT_ASSAY_DYE)
        cls.n_probes_param      = ParameterFactory.integer(NUM_PROBES,
                                                        NUM_PROBES_DESCRIPTION,
                                                        minimum=4,
                                                        required=False)
        cls.id_training_param   = ParameterFactory.integer(ID_TRAINING_FACTOR,
                                                   TRAINING_FACTOR_DESCRIPTION,
                                                   minimum=1,
                                                   required=False,
                                                   default=DEFAULT_ID_TRAINING_FACTOR,)
        cls.ui_threshold_param  = ParameterFactory.float(UI_THRESHOLD,
                                                      UI_THRESHOLD_DESCRIPTION,
                                                      minimum=0.0,
                                                      required=False,
                                                      default=DEFAULT_UNINJECTED_THRESHOLD)
        cls.continuous_phase_param   = ParameterFactory.boolean(CONTINUOUS_PHASE,
                                                          CONTINUOUS_PHASE_DESCRIPTION,
                                                          default_value=False,
                                                          required=False)
        cls.max_ui_ratio_param  = ParameterFactory.float(MAX_UNINJECTED_RATIO,
                                                         MAX_UI_RATIO_DESCRIPTION,
                                                         default=DEFAULT_UNINJECTED_RATIO,
                                                         minimum=0.0)
        cls.ignore_lowest_barcode = ParameterFactory.boolean(IGNORE_LOWEST_BARCODE,
                                                             IGNORE_LOWEST_BARCODE_DESCRIPTION,
                                                             default_value=True,
                                                             required=False)
        cls.use_pico1_filter = ParameterFactory.boolean(USE_PICO1_FILTER,
                                                        USE_PICO1_FILTER_DESCRIPTION,
                                                        default_value=True,
                                                        required=False)
        cls.use_pico2_filter = ParameterFactory.boolean(USE_PICO2_FILTER,
                                                        USE_PICO2_FILTER_DESCRIPTION,
                                                        default_value=True,
                                                        required=False)
        cls.dev_mode_param   = ParameterFactory.boolean(DEV_MODE,
                                                        'Use development mode (more forgiving of mistakes).',
                                                        default_value=DEFAULT_DEV_MODE,
                                                        required=False)
        cls.drift_compensate_param   = ParameterFactory.boolean(DRIFT_COMPENSATE,
                                                        'Compensate for data drift.',
                                                        default_value=DEFAULT_DRIFT_COMPENSATE,
                                                        required=False)

        # assay caller params
        cls.ac_training_param = ParameterFactory.integer(AC_TRAINING_FACTOR,
                                                       TRAINING_FACTOR_DESCRIPTION,
                                                       minimum=1,
                                                       required=False,
                                                       default=DEFAULT_AC_TRAINING_FACTOR)

        cls.ctrl_thresh     = ParameterFactory.float(CTRL_THRESH,
                                                     CTRL_THRESH_DESCRIPTION,
                                                     default=DEFAULT_AC_CTRL_THRESHOLD,
                                                     minimum=0.0, maximum=100.0)

        cls.ctrl_filter     = ParameterFactory.boolean(CTRL_FILTER,
                                                       CTRL_FILTER_DESCRIPTION,
                                                       default_value=False,
                                                       required=True)
        cls.ac_method = ParameterFactory.ac_method(AC_METHOD,
                                                   AC_METHOD_DESCRIPTION)
        cls.ac_model     = ParameterFactory.cs_string(AC_MODEL,
                                                      AC_MODEL_DESCRIPTION,
                                                      required=False,
                                                      enum=[m for model_dict in MODEL_FILES.values()
                                                            for m in model_dict])

        # genotyper params
        cls.req_drops_param = ParameterFactory.integer(REQUIRED_DROPS,
                                                       REQ_DROPS_DESCRIPTION,
                                                       required=False,
                                                       minimum=0,
                                                       default=0)

        parameters = [
                      cls.pa_data_src_param,
                      cls.dyes_param,
                      cls.device_param,
                      cls.major_param,
                      cls.minor_param,
                      cls.job_name_param,
                      cls.offset,
                      cls.use_iid_param,
                      cls.pico1_dye_param,
                      cls.pico2_dye_param,
                      cls.assay_dye_param,
                      cls.n_probes_param,
                      cls.id_training_param,
                      cls.dye_levels_param,
                      cls.ignored_dyes_param,
                      cls.dev_mode_param,
                      cls.drift_compensate_param,
                      cls.use_pico1_filter,
                      cls.use_pico2_filter,
                      cls.filtered_dyes_param,
                      cls.ui_threshold_param,
                      cls.continuous_phase_param,
                      cls.max_ui_ratio_param,
                      cls.ignore_lowest_barcode,
                      cls.ac_training_param,
                      cls.ctrl_thresh,
                      cls.ctrl_filter,
                      cls.ac_method,
                      cls.ac_model,
                      cls.req_drops_param,
                      cls.exp_def_param,
                      cls.mask_param,
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        json_response = {FULL_ANALYSIS: []}

        parameters = dict()
        for param in params_dict:
            param_value = params_dict[param]
            # unpack them from the list if length is 1
            parameters[param.name] = param_value[0] if len(param_value) == 1 else param_value

        # Ensure archive directory is valid
        try:
            archives = parse_pa_data_src(parameters[PA_DATA_SOURCE])
        except:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)

        # Ensure at least one valid archive is found
        if len(archives) < 1:
            return make_clean_response(json_response, 404)

        status_codes = list()
        len_archives = len(archives)
        for idx, (name, is_hdf5) in enumerate(archives):
            cur_job_name = "%s-%d" % (parameters[JOB_NAME], idx + 1) if len_archives > 1 \
                           else parameters[JOB_NAME]
            exist_fa_jobs = cls._DB_CONNECTOR.find(FA_PROCESS_COLLECTION,
                                    {ARCHIVE: name})

            status_code = 200
            if any(all(has_duplicate_params(parameters, job, doc)
                    for doc in [PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT, GT_DOCUMENT])
                    for job in exist_fa_jobs):
                status_code = 403
                json_response[FULL_ANALYSIS].append({ERROR: 'Job exists.'})
            else:
                try:
                    cur_parameters = copy.deepcopy(parameters)
                    cur_parameters[JOB_NAME] = cur_job_name
                    cur_parameters[ARCHIVE] = name
                    cur_parameters[IS_HDF5] = is_hdf5
                    cur_parameters[BEST_EXIST_JOB] = find_best_exising_job(
                                                    parameters, exist_fa_jobs)

                    fa_workflow = FullAnalysisWorkFlowCallable(parameters=cur_parameters,
                                                               db_connector=cls._DB_CONNECTOR)
                    response = fa_workflow.document
                    callback = make_process_callback(fa_workflow.uuid, cls._DB_CONNECTOR)

                    cls._EXECUTION_MANAGER.add_job(response[UUID],
                                                   fa_workflow, callback)
                except:
                    APP_LOGGER.exception(traceback.format_exc())
                    response = {JOB_NAME: cur_job_name, ERROR: str(sys.exc_info()[1])}
                    status_code = 500
                finally:
                    if ID in response:
                        del response[ID]
                    json_response[FULL_ANALYSIS].append(response)

            status_codes.append(status_code)

        return make_clean_response(json_response, max(status_codes))

def has_duplicate_params(parameters, exist_job, doc=PA_DOCUMENT):
    """
    Check whether the specified full analysis parameters are used in an existing job.

    @param parameters:          full analysis parameters
    @param exist_job:           an existing full analysis job
    """
    if parameters[EXP_DEF] != exist_job[EXP_DEF]: return False
    # if this is an old job whose TSV files have been deleted, always rerun
    if doc in [PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT] and \
            doc in exist_job and URL in exist_job[doc] and \
            exist_job[doc][URL] is None:
        return False

    if doc == PA_DOCUMENT:
        params_to_check = [OFFSETS]
    elif doc == ID_DOCUMENT:
        params_to_check = [UI_THRESHOLD, MAX_UNINJECTED_RATIO, USE_PICO1_FILTER,
                           USE_PICO2_FILTER, IGNORE_LOWEST_BARCODE, DEV_MODE,
                           DRIFT_COMPENSATE, PICO1_DYE]
    elif doc == AC_DOCUMENT:
        params_to_check = [AC_TRAINING_FACTOR, CTRL_THRESH, CTRL_FILTER, AC_METHOD,
                           AC_MODEL]
    elif doc == GT_DOCUMENT:
        params_to_check = [REQUIRED_DROPS]
    else:
        params_to_check = []

    if doc in exist_job and any(parameters.get(param) != \
            exist_job[doc].get(convert_param_name(param))
            for param in params_to_check):
        return False
    return True

def find_best_exising_job(parameters, jobs):
    """
    From a list of existing full analysis jobs, find the best one for rerun.

    @param parameters:          full analysis parameters
    @param jobs:                a list of full analysis jobs
    """
    if not jobs: return None
    max_num_subjobs = 0
    best_job = None

    def count_subjobs(job):
        count = 0
        for doc in [PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT, GT_DOCUMENT, EP_DOCUMENT]:
            if doc in job and job[doc].get(STATUS) == SUCCEEDED:
                # if this is an old job and its TSV files have been deleted
                if doc in [PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT] and \
                    job[doc][URL] is None: return 0
                # only count a subjob if having the same parameters
                if has_duplicate_params(parameters, job, doc):
                    count += 1
        return count

    for job in jobs:
        num_subjobs = count_subjobs(job)
        if num_subjobs > max_num_subjobs:
            max_num_subjobs = num_subjobs
            best_job = job
    return best_job

def make_process_callback(uuid, db_connector):
    """
    Return a closure that is fired when the job finishes. This
    callback updates the DB with completion status, result file location, and
    an error message if applicable.

    @param uuid: Unique job id in database
    @param db_connector: Object that handles communication with the DB
    """
    query = {UUID: uuid}
    def process_callback(future):
        try:
            _ = future.result()
            update = { "$set": {
                                 STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                 FINISH_DATESTAMP: datetime.today(),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(FA_PROCESS_COLLECTION, query, {})) > 0:
                db_connector.update(FA_PROCESS_COLLECTION, query, update)
        except:
            error_msg = str(sys.exc_info()[1])
            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(FA_PROCESS_COLLECTION, query, {})) > 0:
                db_connector.update(FA_PROCESS_COLLECTION, query, update)

    return process_callback


#===============================================================================
# Run Main
#===============================================================================
if __name__ == '__main__':
    function = FullAnalysisPostFunction()
    print function
