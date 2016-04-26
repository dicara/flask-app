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
from collections import defaultdict
import copy
from datetime import datetime
import sys
import traceback

from bioweb_api import FA_PROCESS_COLLECTION
from bioweb_api.apis.ApiConstants import EXP_DEF, ERROR, FINISH_DATESTAMP, \
    ID, UUID, JOB_NAME, MAJOR, MINOR, OFFSETS, USE_IID, FIDUCIAL_DYE, STATUS, \
    ASSAY_DYE, NUM_PROBES, AC_TRAINING_FACTOR, IGNORED_DYES, FILTERED_DYES, \
    PF_TRAINING_FACTOR, UI_THRESHOLD, ID_TRAINING_FACTOR, REQUIRED_DROPS, \
    NUM_PROBES_DESCRIPTION, TRAINING_FACTOR_DESCRIPTION, PF_TRAINING_FACTOR_DESCRIPTION, \
    UI_THRESHOLD_DESCRIPTION, REQ_DROPS_DESCRIPTION, DYES, DYE_LEVELS, ARCHIVE, \
    PA_MIN_NUM_IMAGES, CTRL_THRESH, CTRL_THRESH_DESCRIPTION, JOB_STATUS
from bioweb_api.apis.full_analysis.FullAnalysisWorkflow import FullAnalysisWorkFlowCallable
from bioweb_api.utilities.io_utilities import make_clean_response, get_archive_dirs
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from primary_analysis.experiment.experiment_definitions import ExperimentDefinitions
from primary_analysis.dye_model import DEFAULT_OFFSETS
from secondary_analysis.constants import PICOINJECTION_TRAINING_FACTOR
from secondary_analysis.constants import TRAINING_FACTOR as DEFAULT_ID_TRAINING_FACTOR
from secondary_analysis.constants import AC_TRAINING_FACTOR as DEFAULT_AC_TRAINING_FACTOR
from secondary_analysis.constants import ASSAY_DYE as DEFAULT_ASSAY_DYE
from secondary_analysis.constants import PICO_DYE as DEFAULT_PICO_DYE
from secondary_analysis.constants import UNINJECTED_THRESHOLD as DEFAULT_UNINJECTED_THRESHOLD
from secondary_analysis.constants import AC_CTRL_THRESHOLD as DEFAULT_AC_CTRL_THRESHOLD

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
                       'message': 'Job name already exists. Delete the ' \
                                  'existing job or pick a new name.'},
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

        # primary analysis parameters
        cls.archives_param = ParameterFactory.cs_string(ARCHIVE,
                                                        "Archive directory name.",
                                                        required=True)
        cls.dyes_param     = ParameterFactory.dyes(required=False)
        cls.device_param   = ParameterFactory.device(required=False,
                                                     default='beta7')
        cls.major_param    = ParameterFactory.integer(MAJOR,
                                                      'Major dye version',
                                                      minimum=0,
                                                      required=False,
                                                      default=2)
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

        # secondary analysis parameters
        cls.dye_levels_param    = ParameterFactory.dye_levels(required=False)
        cls.ignored_dyes_param  = ParameterFactory.dyes(name=IGNORED_DYES,
                                                       required=False)
        cls.filtered_dyes_param = ParameterFactory.dyes(name=FILTERED_DYES,
                                                        required=False)
        cls.fid_dye_param       = ParameterFactory.dye(FIDUCIAL_DYE,
                                                      'Fiducial dye.',
                                                      required=False,
                                                      default=DEFAULT_PICO_DYE)
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
        cls.prefilter_tf_param  = ParameterFactory.integer(PF_TRAINING_FACTOR,
                                                PF_TRAINING_FACTOR_DESCRIPTION,
                                                minimum=0,
                                                required=False,
                                                default=PICOINJECTION_TRAINING_FACTOR,)
        cls.ui_threshold_param  = ParameterFactory.float(UI_THRESHOLD,
                                                      UI_THRESHOLD_DESCRIPTION,
                                                      minimum=0.0,
                                                      required=False,
                                                      default=DEFAULT_UNINJECTED_THRESHOLD)

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

        # genotyper params
        cls.req_drops_param = ParameterFactory.integer(REQUIRED_DROPS,
                                                       REQ_DROPS_DESCRIPTION,
                                                       required=False,
                                                       minimum=0,
                                                       default=0)

        # full analysis parameters
        cls.fa_uuid_param = ParameterFactory.job_uuid(FA_PROCESS_COLLECTION, required=False)


        parameters = [
                      cls.archives_param,
                      cls.dyes_param,
                      cls.device_param,
                      cls.major_param,
                      cls.minor_param,
                      cls.job_name_param,
                      cls.offset,
                      cls.use_iid_param,
                      cls.fid_dye_param,
                      cls.assay_dye_param,
                      cls.n_probes_param,
                      cls.id_training_param,
                      cls.dye_levels_param,
                      cls.ignored_dyes_param,
                      cls.filtered_dyes_param,
                      cls.prefilter_tf_param,
                      cls.ui_threshold_param,
                      cls.ac_training_param,
                      cls.ctrl_thresh,
                      cls.req_drops_param,
                      cls.exp_def_param,
                      cls.fa_uuid_param
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

        # there are certain parameters that the user may not have sent
        # but that can come from the experiment definition, set them here
        try:
            if DYES not in parameters or \
               DYE_LEVELS not in parameters or \
               NUM_PROBES not in parameters:
                # get dyes and number of levels
                exp_defs = ExperimentDefinitions()
                exp_def_uuid = exp_defs.get_experiment_uuid(parameters[EXP_DEF])
                exp_def = exp_defs.get_experiment_defintion(exp_def_uuid)

                probes = exp_def['probes']
                controls = exp_def['controls']
                barcodes = [barcode for probe in probes for barcode in probe['barcodes']]
                dye_levels = defaultdict(int)
                for barcode in barcodes + controls:
                    for dye_name, lvl in barcode['dye_levels'].items():
                        dye_levels[dye_name] = max(dye_levels[dye_name], int(lvl+1))
                if DYES not in parameters:
                    parameters[DYES] = dye_levels.keys()
                if DYE_LEVELS not in parameters:
                    parameters[DYE_LEVELS] = dye_levels.items()
                if NUM_PROBES not in parameters:
                    parameters[NUM_PROBES] = len(probes) + len(controls)

        except:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)


        # set parameters for anything user might not have set
        if FILTERED_DYES not in parameters:
            parameters[FILTERED_DYES] = list()

        if IGNORED_DYES not in parameters:
            parameters[IGNORED_DYES] = list()

        # Ensure archive directory is valid
        try:
            archives = get_archive_dirs(parameters[ARCHIVE],
                                        min_num_images=PA_MIN_NUM_IMAGES)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)

        # Ensure at least one valid archive is found
        if len(archives) < 1:
            return make_clean_response(json_response, 404)

        fa_job_names = set(cls._DB_CONNECTOR.distinct(FA_PROCESS_COLLECTION, JOB_NAME))

        status_codes = list()
        for idx, archive in enumerate(archives):
            cur_job_name = "%s-%d" % (parameters[JOB_NAME], idx)

            status_code = 200
            if cur_job_name in fa_job_names:
                status_code = 403
                json_response[FULL_ANALYSIS].append({ERROR: 'Job exists.'})
            else:
                try:
                    cur_parameters = copy.deepcopy(parameters)
                    cur_parameters[JOB_NAME] = cur_job_name
                    cur_parameters[ARCHIVE] = archive

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
