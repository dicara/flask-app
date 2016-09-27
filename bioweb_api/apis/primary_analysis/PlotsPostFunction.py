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
@date:   Jan 27, 2015
'''

#=============================================================================
# Imports
#=============================================================================
import os
import sys
import traceback
import yaml

from uuid import uuid4
from datetime import datetime

from bioweb_api.utilities.io_utilities import silently_remove_file, make_clean_response, \
    get_results_folder, get_results_url
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import UUID, RESULT, ERROR, ID, PLOT, \
    PLOT_URL, SUBMIT_DATESTAMP, FINISH_DATESTAMP, PA_PROCESS_UUID, \
    START_DATESTAMP, CONFIG, JOB_STATUS, JOB_TYPE_NAME, STATUS, JOB_TYPE
from bioweb_api import PA_PROCESS_COLLECTION, PA_PLOTS_COLLECTION

from primary_analysis.plotting.analysis_plot_generator import AnalysisPlotGenerator

#=============================================================================
# Private Static Variables
#=============================================================================
_PLOTS = "Plots"

#=============================================================================
# Class
#=============================================================================
class PlotsPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return "Plots"

    @staticmethod
    def summary():
        return "Run the equivalent of pa plots."

    @staticmethod
    def notes():
        return ""

    def response_messages(self):
        msgs = super(PlotsPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403,
                       "message": "Plot for this analysis job already exists. " \
                                  "Delete the existing plot and retry."},
                     { "code": 404,
                       "message": "Submission unsuccessful. Analysis job not "\
                                  "found."},
                    ])
        return msgs

    @classmethod
    def parameters(cls):
        cls.job_uuid       = ParameterFactory.job_uuid(PA_PROCESS_COLLECTION)

        parameters = [
                      cls.job_uuid,
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        job_uuids     = params_dict[cls.job_uuid]
        json_response = {_PLOTS: []}

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
        for pa_process_job in pa_process_jobs:
            response = {
                        UUID: str(uuid4()),
                        PA_PROCESS_UUID: pa_process_job[UUID],
                        STATUS: JOB_STATUS.submitted,     # @UndefinedVariable
                        JOB_TYPE_NAME: JOB_TYPE.pa_plots, # @UndefinedVariable
                        SUBMIT_DATESTAMP: datetime.today(),
                       }
            status_code = 200
            try:
                results_folder = get_results_folder()
                outfile_path = os.path.join(results_folder,
                                            pa_process_job[UUID] + ".png")

                if pa_process_job[UUID] in cls._DB_CONNECTOR.distinct(PA_PLOTS_COLLECTION,
                                                                      PA_PROCESS_UUID):
                    status_code = 403
                else:
                    with open(pa_process_job[CONFIG]) as fd:
                        config = yaml.load(fd)

                    # Create helper functions
                    abs_callable = PaProcessCallable(config,
                                                     pa_process_job[RESULT],
                                                     outfile_path,
                                                     response[UUID],
                                                     cls._DB_CONNECTOR)
                    callback = make_process_callback(response[UUID],
                                                     outfile_path,
                                                     cls._DB_CONNECTOR)

                    # Add to queue and update DB
                    cls._DB_CONNECTOR.insert(PA_PLOTS_COLLECTION, [response])
                    cls._EXECUTION_MANAGER.add_job(response[UUID],
                                                   abs_callable, callback)
            except:
                APP_LOGGER.exception(traceback.format_exc())
                response[ERROR]  = str(sys.exc_info()[1])
                status_code = 500
            finally:
                if ID in response:
                    del response[ID]

            json_response[_PLOTS].append(response)
            status_codes.append(status_code)

        # If all jobs submitted successfully, then 200 should be returned.
        # Otherwise, the maximum status code seems good enough.
        return make_clean_response(json_response, max(status_codes))

#===============================================================================
# Callable/Callback Functionality
#===============================================================================
class PaProcessCallable(object):
    """
    Callable that executes the absorption command.
    """
    def __init__(self, config, analysis_path, outfile_path, uuid,
                 db_connector):
        self.config        = config
        self.analysis_path = analysis_path
        self.outfile_path  = outfile_path
        self.db_connector  = db_connector
        self.query         = {UUID: uuid}

    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}
        self.db_connector.update(PA_PLOTS_COLLECTION, self.query, update)

        plot_generator = AnalysisPlotGenerator(self.config)
        barcodes_list, barcodes_names = plot_generator.read_barcodes_from_analyses_files([self.analysis_path])
        plot_generator.generate_plots(barcodes_list, barcodes_names,
                                      show_plot=False,
                                      out_path=self.outfile_path,
                                      show_legend=False)

def make_process_callback(uuid, outfile_path, db_connector):
    """
    Return a closure that is fired when the job finishes. This
    callback updates the DB with completion status, result file location, and
    an error message if applicable.

    @param uuid: Unique job id in database
    @param outfile_path - Path where the final png plot should live.
    @param db_connector: Object that handles communication with the DB
    """
    query = {UUID: uuid}
    def process_callback(future):
        try:
            _ = future.result()
            update = { "$set": {
                                 STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                 PLOT: outfile_path,
                                 FINISH_DATESTAMP: datetime.today(),
                                 PLOT_URL: get_results_url(
                                        os.path.basename(outfile_path),
                                        os.path.basename(os.path.dirname(outfile_path))),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(PA_PLOTS_COLLECTION, query, {})) > 0:
                db_connector.update(PA_PLOTS_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            error_msg = str(sys.exc_info()[1])
            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   PLOT: None,
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(PA_PLOTS_COLLECTION, query, {})) > 0:
                db_connector.update(PA_PLOTS_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)

    return process_callback

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = PlotsPostFunction()
    print function
