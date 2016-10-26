'''
Copyright 2014 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed: on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Dan DiCara
@date:   Feb 3, 2015
'''

#=============================================================================
# Imports
#=============================================================================
import copy
import os
import shutil
import sys
import traceback
import yaml

from uuid import uuid4
from datetime import datetime

from bioweb_api.utilities.io_utilities import make_clean_response, silently_remove_file, \
    safe_make_dirs, get_results_folder, get_results_url
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import SA_IDENTITY_COLLECTION, PA_PROCESS_COLLECTION, TMP_PATH
from bioweb_api.apis.ApiConstants import UUID, JOB_NAME, JOB_STATUS, STATUS, \
    ID, FIDUCIAL_DYE, ASSAY_DYE, JOB_TYPE, JOB_TYPE_NAME, RESULT, CONFIG, \
    ERROR, PA_PROCESS_UUID, SUBMIT_DATESTAMP, NUM_PROBES, TRAINING_FACTOR, \
    START_DATESTAMP, PLOT, PLOT_URL, FINISH_DATESTAMP, URL, DYE_LEVELS, \
    IGNORED_DYES, UI_THRESHOLD, REPORT, CONTINUOUS_PHASE, CONTINUOUS_PHASE_DESCRIPTION, \
    REPORT_URL, FILTERED_DYES, NUM_PROBES_DESCRIPTION, TRAINING_FACTOR_DESCRIPTION, \
    UI_THRESHOLD_DESCRIPTION, PLATE_PLOT_URL, DYES, MAX_UNINJECTED_RATIO, \
    MAX_UI_RATIO_DESCRIPTION, TEMPORAL_PLOT_URL, IGNORE_LOWEST_BARCODE, \
    IGNORE_LOWEST_BARCODE_DESCRIPTION
from primary_analysis.command import InvalidFileError
from secondary_analysis.constants import FACTORY_ORGANIC, ID_MODEL_METRICS, \
    UNINJECTED_THRESHOLD, UNINJECTED_RATIO, ID_PLOT_SUFFIX, ID_PLATES_PLOT_SUFFIX, \
    ID_TEMPORAL_PLOT_SUFFIX

from secondary_analysis.constants import ID_TRAINING_FACTOR_MAX as DEFAULT_ID_TRAINING_FACTOR
from secondary_analysis.identity.identity import Identity

#=============================================================================
# Public Static Variables
#=============================================================================
IDENTITY = "Identity"

#=============================================================================
# Private Static Variables
#=============================================================================


#=============================================================================
# Class
#=============================================================================
class IdentityPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return IDENTITY

    @staticmethod
    def summary():
        return "Run the equivalent of pa identity."

    @staticmethod
    def notes():
        return ""

    def response_messages(self):
        msgs = super(IdentityPostFunction, self).response_messages()
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
        cls.job_name_param  = ParameterFactory.lc_string(JOB_NAME, "Unique "\
                                                         "name to give this "
                                                         "job.")
        cls.fid_dye_param      = ParameterFactory.dye(FIDUCIAL_DYE,
                                                      "Fiducial dye.")
        cls.assay_dye_param    = ParameterFactory.dye(ASSAY_DYE, "Assay dye.")
        cls.n_probes_param     = ParameterFactory.integer(NUM_PROBES,
                                                        NUM_PROBES_DESCRIPTION,
                                                        default=0, minimum=0)
        cls.training_param     = ParameterFactory.integer(TRAINING_FACTOR,
                                                   TRAINING_FACTOR_DESCRIPTION,
                                                   default=DEFAULT_ID_TRAINING_FACTOR,
                                                   minimum=1)
        cls.dye_levels_param   = ParameterFactory.dye_levels()
        cls.ignored_dyes_param = ParameterFactory.dyes(name=IGNORED_DYES,
                                                       required=False)
        cls.filtered_dyes_param = ParameterFactory.dyes(name=FILTERED_DYES,
                                                        required=False)
        cls.ui_threshold_param = ParameterFactory.float(UI_THRESHOLD,
                                                      UI_THRESHOLD_DESCRIPTION,
                                                      default=UNINJECTED_THRESHOLD,
                                                      minimum=0.0)
        cls.continuous_phase_param   = ParameterFactory.boolean(CONTINUOUS_PHASE,
                                                          CONTINUOUS_PHASE_DESCRIPTION,
                                                          default_value=False,
                                                          required=False)
        cls.max_ui_ratio_param = ParameterFactory.float(MAX_UNINJECTED_RATIO,
                                                        MAX_UI_RATIO_DESCRIPTION,
                                                        default=UNINJECTED_RATIO,
                                                        minimum=0.0)
        cls.ignore_lowest_barcode = ParameterFactory.boolean(IGNORE_LOWEST_BARCODE,
                                                             IGNORE_LOWEST_BARCODE_DESCRIPTION,
                                                             default_value=True,
                                                             required=False)

        parameters = [
                      cls.job_uuid_param,
                      cls.job_name_param,
                      cls.fid_dye_param,
                      cls.assay_dye_param,
                      cls.n_probes_param,
                      cls.training_param,
                      cls.dye_levels_param,
                      cls.ignored_dyes_param,
                      cls.filtered_dyes_param,
                      cls.ui_threshold_param,
                      cls.continuous_phase_param,
                      cls.max_ui_ratio_param,
                      cls.ignore_lowest_barcode,
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        job_uuids       = params_dict[cls.job_uuid_param]
        job_name        = params_dict[cls.job_name_param][0]

        fiducial_dye=None
        if cls.fid_dye_param in params_dict:
            fiducial_dye    = params_dict[cls.fid_dye_param][0]
        assay_dye = None
        if cls.assay_dye_param in params_dict:
            assay_dye       = params_dict[cls.assay_dye_param][0]
        num_probes      = params_dict[cls.n_probes_param][0]
        training_factor = params_dict[cls.training_param][0]
        dye_levels      = params_dict[cls.dye_levels_param]

        filtered_dyes = list()
        if cls.filtered_dyes_param in params_dict:
            filtered_dyes = params_dict[cls.filtered_dyes_param]

        ignored_dyes = list()
        if cls.ignored_dyes_param in params_dict:
            ignored_dyes = params_dict[cls.ignored_dyes_param]

        ui_threshold    = params_dict[cls.ui_threshold_param][0]

        if cls.continuous_phase_param in params_dict and \
           params_dict[cls.continuous_phase_param][0]:
            use_pico_thresh = True
        else:
            use_pico_thresh = False

        if cls.ignore_lowest_barcode in params_dict and \
           params_dict[cls.ignore_lowest_barcode][0]:
            ignore_lowest_barcode = True
        else:
            ignore_lowest_barcode = False

        max_uninj_ratio = params_dict[cls.max_ui_ratio_param][0]

        json_response = {IDENTITY: []}

        # Ensure analysis job exists
        try:
            criteria        = {UUID: {"$in": job_uuids}}
            projection      = {ID: 0, RESULT: 1, UUID: 1, CONFIG: 1}
            pa_process_jobs = cls._DB_CONNECTOR.find(PA_PROCESS_COLLECTION,
                                                     criteria, projection)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)

        # Ensure at least one valid analysis job exists
        if len(pa_process_jobs) < 1:
            return make_clean_response(json_response, 404)

        # Process each archive
        status_codes  = []
        for i, pa_uuid in enumerate(job_uuids):
            if len(pa_process_jobs) == 1:
                cur_job_name = job_name
            else:
                cur_job_name = "%s-%d" % (job_name, i)


            status_code = 200

            if cur_job_name in cls._DB_CONNECTOR.distinct(SA_IDENTITY_COLLECTION,
                                                          JOB_NAME):
                status_code = 403
                json_response[IDENTITY].append({ERROR: 'Job exists.'})
            else:
                try:
                    # Create helper functions
                    sai_callable = SaIdentityCallable(pa_uuid,
                                                      num_probes,
                                                      training_factor,
                                                      assay_dye,
                                                      fiducial_dye,
                                                      dye_levels,
                                                      ignored_dyes,
                                                      filtered_dyes,
                                                      ui_threshold,
                                                      max_uninj_ratio,
                                                      cls._DB_CONNECTOR,
                                                      job_name,
                                                      use_pico_thresh,
                                                      ignore_lowest_barcode)
                    response = copy.deepcopy(sai_callable.document)
                    callback = make_process_callback(sai_callable.uuid,
                                                     sai_callable.outfile_path,
                                                     sai_callable.plot_path,
                                                     sai_callable.report_path,
                                                     sai_callable.plate_plot_path,
                                                     sai_callable.temporal_plot_path,
                                                     cls._DB_CONNECTOR)

                    # Add to queue
                    cls._EXECUTION_MANAGER.add_job(sai_callable.uuid,
                                                   sai_callable,
                                                   callback)

                except:
                    APP_LOGGER.exception(traceback.format_exc())
                    response = {JOB_NAME: cur_job_name, ERROR: str(sys.exc_info()[1])}
                    status_code = 500
                finally:
                    if ID in response:
                        del response[ID]
                    json_response[IDENTITY].append(response)

            status_codes.append(status_code)

        # If all jobs submitted successfully, then 200 should be returned.
        # Otherwise, the maximum status code seems good enough.
        return make_clean_response(json_response, max(status_codes))

#===============================================================================
# Callable/Callback Functionality
#===============================================================================
class SaIdentityCallable(object):
    """
    Callable that executes the absorption command.
    """
    def __init__(self, primary_analysis_uuid, num_probes, training_factor, assay_dye,
                 fiducial_dye, dye_levels, ignored_dyes, filtered_dyes,
                 ui_threshold, max_uninj_ratio, db_connector, job_name,
                 use_pico_thresh, ignore_lowest_barcode):
        self.uuid                  = str(uuid4())
        self.primary_analysis_uuid = primary_analysis_uuid
        self.dye_levels            = map(list, dye_levels)
        self.num_probes            = num_probes
        self.training_factor       = training_factor

        results_folder             = get_results_folder()
        self.plot_path             = os.path.join(results_folder, self.uuid + '.png')
        self.plate_plot_path       = os.path.join(results_folder, self.uuid + '_plate.png')
        self.temporal_plot_path    = os.path.join(results_folder, self.uuid + '_temporal.png')
        self.outfile_path          = os.path.join(results_folder, self.uuid)
        self.report_path           = os.path.join(results_folder, self.uuid + '.yaml')
        self.assay_dye             = assay_dye
        self.fiducial_dye          = fiducial_dye
        self.ignored_dyes          = ignored_dyes
        self.filtered_dyes         = filtered_dyes
        self.ui_threshold          = ui_threshold
        self.max_uninj_ratio       = max_uninj_ratio
        self.db_connector          = db_connector
        self.job_name              = job_name
        self.use_pico_thresh       = use_pico_thresh
        self.ignore_lowest_barcode = ignore_lowest_barcode

        self.tmp_path              = os.path.join(TMP_PATH, self.uuid)
        self.tmp_outfile_path      = os.path.join(self.tmp_path, "identity.txt")
        self.tmp_report_path       = os.path.join(self.tmp_path, "report.yaml")
        self.document              = {
                        FIDUCIAL_DYE: fiducial_dye,
                        ASSAY_DYE: assay_dye,
                        NUM_PROBES: num_probes,
                        TRAINING_FACTOR: training_factor,
                        DYE_LEVELS: self.dye_levels,
                        IGNORED_DYES: ignored_dyes,
                        FILTERED_DYES: filtered_dyes,
                        UI_THRESHOLD: ui_threshold,
                        MAX_UNINJECTED_RATIO: max_uninj_ratio,
                        UUID: self.uuid,
                        PA_PROCESS_UUID: primary_analysis_uuid,
                        STATUS: JOB_STATUS.submitted,     # @UndefinedVariable
                        JOB_NAME: self.job_name,
                        JOB_TYPE_NAME: JOB_TYPE.sa_identity, # @UndefinedVariable
                        SUBMIT_DATESTAMP: datetime.today(),
                        CONTINUOUS_PHASE: use_pico_thresh,
                        IGNORE_LOWEST_BARCODE: ignore_lowest_barcode,
                       }
        if job_name in self.db_connector.distinct(SA_IDENTITY_COLLECTION, JOB_NAME):
            raise Exception('Job name %s already exists in identity collection' % job_name)

        self.db_connector.insert(SA_IDENTITY_COLLECTION, [self.document])


    def __call__(self):
        # retrieve primary analysis data
        primary_analysis_doc = self.db_connector.find(
                                PA_PROCESS_COLLECTION,
                                criteria={UUID: self.primary_analysis_uuid},
                                projection={ID: 0, RESULT: 1, UUID: 1, DYES: 1})[0]

        # verify barcode dyes
        primary_analysis_dyes = set(primary_analysis_doc[DYES])
        identity_dyes = set([x[0] for x in self.dye_levels])
        if not identity_dyes.issubset(set(primary_analysis_dyes)):
            raise Exception("Dyes in levels: %s must be a subset of run dyes: %s" %
                            (identity_dyes, primary_analysis_dyes))

        # verify primary analysis file exists
        if not os.path.isfile(primary_analysis_doc[RESULT]):
            raise InvalidFileError(primary_analysis_doc[RESULT])

        # update database to indicate job is running
        update = {"$set": {STATUS: JOB_STATUS.running,
                           START_DATESTAMP: datetime.today()}}
        self.db_connector.update(SA_IDENTITY_COLLECTION, {UUID: self.uuid}, update)

        try:
            safe_make_dirs(self.tmp_path)
            Identity(in_path=primary_analysis_doc[RESULT],
                     num_probes=self.num_probes,
                     factory_type=FACTORY_ORGANIC,
                     plot_base_path=os.path.join(self.tmp_path, 'tmp_plot'),
                     out_file=self.tmp_outfile_path,
                     report_path=self.tmp_report_path,
                     assay_dye=self.assay_dye,
                     picoinjection_dye=self.fiducial_dye,
                     dye_levels=self.dye_levels,
                     show_figure=False,
                     ignored_dyes=self.ignored_dyes,
                     filtered_dyes=self.filtered_dyes,
                     uninjected_threshold=self.ui_threshold,
                     require_perfect_id=False,
                     use_pico_thresh=self.use_pico_thresh,
                     max_uninj_ratio=self.max_uninj_ratio,
                     ignore_lowest_barcode=self.ignore_lowest_barcode).execute()
            if not os.path.isfile(self.tmp_outfile_path):
                raise Exception("Secondary analysis identity job failed: identity output file not generated.")
            else:
                shutil.copy(self.tmp_outfile_path, self.outfile_path)
            tmp_plot_path = os.path.join(self.tmp_path, 'tmp_plot' + ID_PLOT_SUFFIX)
            tmp_plate_plot_path = os.path.join(self.tmp_path, 'tmp_plot' + ID_PLATES_PLOT_SUFFIX)
            tmp_temporal_plot_path = os.path.join(self.tmp_path, 'tmp_plot' + ID_TEMPORAL_PLOT_SUFFIX)
            if os.path.isfile(tmp_plot_path):
                shutil.copy(tmp_plot_path, self.plot_path)
            if os.path.isfile(tmp_plate_plot_path):
                shutil.copy(tmp_plate_plot_path, self.plate_plot_path)
            if os.path.isfile(tmp_temporal_plot_path):
                shutil.copy(tmp_temporal_plot_path, self.temporal_plot_path)
            if os.path.isfile(self.tmp_report_path):
                shutil.copy(self.tmp_report_path, self.report_path)
        finally:
            # Regardless of success or failure, remove the copied archive directory
            shutil.rmtree(self.tmp_path, ignore_errors=True)


def make_process_callback(uuid, outfile_path, plot_path, report_path,
                          plate_plot_path, temporal_plot_path, db_connector):
    """
    Return a closure that is fired when the job finishes. This
    callback updates the DB with completion status, result file location, and
    an error message if applicable.

    @param uuid:         Unique job id in database
    @param outfile_path: Path where the final identity results will live.
    @param plot_path:    Path where the final PNG plot should live.
    @param report_path:    Path where the report should live.
    @param plate_plot_path:    Path where the plate plot should live.
    @param temporal_plot_path:    Path where the temporal plot should live.
    @param db_connector: Object that handles communication with the DB
    """
    query = {UUID: uuid}
    def process_callback(future):
        try:
            _ = future.result()
            report_errors = check_report_for_errors(report_path)
            update_data = { STATUS: JOB_STATUS.succeeded,
                            RESULT: outfile_path,
                            URL: get_results_url(outfile_path),
                            PLOT: plot_path,
                            REPORT: report_path,
                            PLOT_URL: get_results_url(plot_path),
                            REPORT_URL: get_results_url(report_path),
                            PLATE_PLOT_URL: get_results_url(plate_plot_path),
                            TEMPORAL_PLOT_URL: get_results_url(temporal_plot_path),
                            FINISH_DATESTAMP: datetime.today()}
            if report_errors:
                update_data[ERROR] = report_errors

            update = {"$set": update_data}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_IDENTITY_COLLECTION, query, {})) > 0:
                db_connector.update(SA_IDENTITY_COLLECTION, query, update)
            else:
                silently_remove_file(report_path)
                silently_remove_file(outfile_path)
                silently_remove_file(plot_path)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            error_msg = str(sys.exc_info()[1])

            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   RESULT: None,
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            if os.path.isfile(report_path):
                update['$set'][REPORT_URL]
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_IDENTITY_COLLECTION, query, {})) > 0:
                db_connector.update(SA_IDENTITY_COLLECTION, query, update)
            else:
                silently_remove_file(report_path)
                silently_remove_file(outfile_path)
                silently_remove_file(plot_path)

    return process_callback


def check_report_for_errors(report_path):
    """
    Open and retrieve reportable errors from identity if there are any

    @param report_path: String specify report location
    @return:            String describing errors or None
    """
    if os.path.exists(report_path):
        report_errors = list()
        with open(report_path) as fh:
            id_model_errors = yaml.load(fh)[ID_MODEL_METRICS]['PROBLEMS']
            id_collisions = id_model_errors['id_collisions']
            missing = id_model_errors['missing']
            if missing:
                report_errors.append('Missing barcodes: %s' % str(missing))
            if id_collisions:
                report_errors.append('Identity collisions: %s' % str(id_collisions))
        if report_errors:
            return ', '.join(report_errors)


#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = IdentityPostFunction()
    print function
