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
import copy
import logging
import os
import shutil
import sys

from datetime import datetime
from uuid import uuid4

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import SA_GENOTYPER_COLLECTION, SA_ASSAY_CALLER_COLLECTION, \
    SA_IDENTITY_COLLECTION, TMP_PATH
from bioweb_api.apis.ApiConstants import JOB_NAME, UUID, ERROR, ID, \
    RESULT, EXP_DEF_NAME, SA_ASSAY_CALLER_UUID, SUBMIT_DATESTAMP,\
    SA_IDENTITY_UUID, IGNORED_DYES, FILTERED_DYES, REQUIRED_DROPS, \
    JOB_NAME_DESC, START_DATESTAMP, FINISH_DATESTAMP, URL, JOB_STATUS, \
    STATUS, JOB_TYPE, JOB_TYPE_NAME, VCF, PDF, PDF_URL, PNG, PNG_URL, PNG_SUM, \
    PNG_SUM_URL, REQ_DROPS_DESCRIPTION, VARIANT_MASK, KDE_PNG, KDE_PNG_SUM, \
    KDE_PNG_SUM_URL, KDE_PNG_URL
from bioweb_api.utilities.io_utilities import make_clean_response, \
    silently_remove_file, safe_make_dirs, get_results_folder, get_results_url
from bioweb_api.utilities.logging_utilities import APP_LOGGER

from expdb import HotspotExperiment
from primary_analysis.experiment.experiment_definitions import ExperimentDefinitions
from primary_analysis.command import InvalidFileError
from secondary_analysis.genotyping.genotype_analysis import GenotypeProcessor
from secondary_analysis.assay_calling.assay_caller_plotting import generate_plots

#=============================================================================
# Public Static Variables
#=============================================================================
GENOTYPER = "Genotyper"

#=============================================================================
# Private Static Variables
#=============================================================================
log = logging.getLogger(__name__)


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
                                                       REQ_DROPS_DESCRIPTION,
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
        status_codes = list()
        for i, assay_caller_uuid in enumerate(job_uuids):
            if len(job_uuids) == 1:
                cur_job_name = job_name
            else:
                cur_job_name = "%s-%d" % (job_name, i)
            status_code = 200

            if cur_job_name in cls._DB_CONNECTOR.distinct(SA_GENOTYPER_COLLECTION,
                                                          JOB_NAME):
                status_code = 403
                json_response[GENOTYPER].append({ERROR: 'Job exists.'})
            else:
                try:
                    # Create helper functions
                    genotyper_callable = SaGenotyperCallable(assay_caller_uuid,
                                                             exp_def_name,
                                                             required_drops,
                                                             cls._DB_CONNECTOR,
                                                             cur_job_name)
                    response = copy.deepcopy(genotyper_callable.document)
                    callback = make_process_callback(genotyper_callable.uuid,
                                                     exp_def_name,
                                                     genotyper_callable.ac_result_path,
                                                     genotyper_callable.ignored_dyes,
                                                     genotyper_callable.outfile_path,
                                                     cls._DB_CONNECTOR,
                                                     cur_job_name)

                    # Add to queue
                    cls._EXECUTION_MANAGER.add_job(response[UUID],
                                                   genotyper_callable,
                                                   callback)

                except:
                    APP_LOGGER.exception("Error processing Genotyper post request.")
                    response = {JOB_NAME: cur_job_name, ERROR: str(sys.exc_info()[1])}
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
    def __init__(self, assay_caller_uuid, exp_def_name,
                 required_drops, db_connector, job_name, mask_code=None,
                 combine_alleles=False):

        assay_caller_doc = db_connector.find_one(SA_ASSAY_CALLER_COLLECTION, UUID, assay_caller_uuid)
        identity_doc = db_connector.find_one(SA_IDENTITY_COLLECTION, UUID, assay_caller_doc[SA_IDENTITY_UUID])

        if not os.path.isfile(assay_caller_doc[RESULT]):
            raise InvalidFileError(assay_caller_doc[RESULT])

        self.uuid = str(uuid4())
        self.exp_def_name = exp_def_name
        self.assay_caller_uuid = assay_caller_uuid
        self.ac_result_path   = assay_caller_doc[RESULT]

        results_folder        = get_results_folder()
        self.outfile_path     = os.path.join(results_folder, self.uuid + '.%s' % VCF)
        self.required_drops   = required_drops
        self.ignored_dyes     = identity_doc[IGNORED_DYES] + identity_doc[FILTERED_DYES]
        self.db_connector     = db_connector
        self.mask_code        = mask_code
        self.combine_alleles  = combine_alleles
        self.tmp_path         = os.path.join(TMP_PATH, self.uuid)
        self.tmp_outfile_path = os.path.join(self.tmp_path, self.uuid + ".%s" % VCF)
        self.document = {
                        EXP_DEF_NAME: exp_def_name,
                        REQUIRED_DROPS: required_drops,
                        UUID: self.uuid,
                        SA_ASSAY_CALLER_UUID: assay_caller_uuid,
                        STATUS: JOB_STATUS.submitted,     # @UndefinedVariable
                        JOB_NAME: job_name,
                        JOB_TYPE_NAME: JOB_TYPE.sa_genotyping, # @UndefinedVariable
                        SUBMIT_DATESTAMP: datetime.today(),
                        VARIANT_MASK: self.mask_code,
                       }

        if job_name in self.db_connector.distinct(SA_GENOTYPER_COLLECTION, JOB_NAME):
            raise Exception('Job name %s already exists in genotyper collection' % job_name)

        self.db_connector.insert(SA_GENOTYPER_COLLECTION, [self.document])

    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}
        query = {UUID: self.uuid}
        self.db_connector.update(SA_GENOTYPER_COLLECTION, query, update)
        try:
            safe_make_dirs(self.tmp_path)

            exp_def_fetcher = ExperimentDefinitions()
            exp_def_uuid = exp_def_fetcher.get_experiment_uuid(self.exp_def_name)
            exp_def = exp_def_fetcher.get_experiment_defintion(exp_def_uuid)
            experiment = HotspotExperiment.from_dict(exp_def)
            GenotypeProcessor(experiment, None, self.tmp_outfile_path,
                              required_drops=self.required_drops,
                              in_file=self.ac_result_path,
                              ignored_dyes=self.ignored_dyes,
                              mask_code=self.mask_code,
                              combine_alleles=self.combine_alleles)

            if not os.path.isfile(self.tmp_outfile_path):
                raise Exception("Secondary analysis genotyper job " +
                                "failed: VCF file not generated.")
            else:
                shutil.copy(self.tmp_outfile_path, self.outfile_path)

            if not os.path.isfile(self.tmp_outfile_path[:-3] + PDF):
                raise Exception("Secondary analysis genotyper job " +
                                "failed: PDF file not generated.")
            else:
                shutil.copy(self.tmp_outfile_path[:-3] + PDF, self.outfile_path[:-3] + PDF)
        finally:
            # Regardless of success or failure, remove the copied archive directory
            shutil.rmtree(self.tmp_path, ignore_errors=True)

def make_process_callback(uuid, exp_def_name, ac_result_path, ignored_dyes,
                          outfile_path, db_connector, cur_job_name):
    """
    Return a closure that is fired when the job finishes. This
    callback updates the DB with completion status, result file location, and
    an error message if applicable.

    @param uuid:         Unique job id in database
    @param exp_def_name: Experiment definition name
    @param ac_result_path: Path to assay caller result
    @param ignored_dyes: List of dyes to ignore
    @param outfile_path: Path where the final identity results will live
    @param db_connector: Object that handles communication with the DB
    @param cur_job_name: Current job name from which to get the title for
        plotting purposes (e.g. 2016-08-16_1400.59-pilot2_2MVHbM)
    """
    query = {UUID: uuid}
    def process_callback(future):
        try:
            _ = future.result()

            dirname    = os.path.dirname(outfile_path)
            vcf_fn     = os.path.basename(outfile_path)
            basename   = os.path.splitext(vcf_fn)[0]
            pdf_fn     = '%s.%s' % (basename, PDF)
            scatter_png_fn     = '%s_scatter.%s' % (basename, PNG)
            scatter_ind_pdf_fn = '%s_scatter_ind.%s' % (basename, PDF)
            kde_png_fn         = '%s_kde.%s' % (basename, PNG)
            kde_ind_pdf_fn     = '%s_kde_ind.%s' % (basename, PDF)

            generate_plots(exp_def_name, ac_result_path,
                           os.path.splitext(outfile_path)[0],
                           ignored_dyes=ignored_dyes,
                           data_set_name=cur_job_name)

            update = { "$set": {
                                 STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                 RESULT: outfile_path,
                                 URL: get_results_url(vcf_fn),
                                 PDF: os.path.join(dirname, pdf_fn),
                                 PDF_URL: get_results_url(pdf_fn),
                                 PNG: os.path.join(dirname, scatter_ind_pdf_fn),
                                 PNG_URL: get_results_url(scatter_ind_pdf_fn),
                                 PNG_SUM: os.path.join(dirname, scatter_png_fn),
                                 PNG_SUM_URL: get_results_url(scatter_png_fn),
                                 KDE_PNG: os.path.join(dirname, kde_ind_pdf_fn),
                                 KDE_PNG_URL: get_results_url(kde_ind_pdf_fn),
                                 KDE_PNG_SUM: os.path.join(dirname, kde_png_fn),
                                 KDE_PNG_SUM_URL: get_results_url(kde_png_fn),
                                 FINISH_DATESTAMP: datetime.today(),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_GENOTYPER_COLLECTION, query, {})) > 0:
                db_connector.update(SA_GENOTYPER_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(os.path.join(dirname, pdf_fn))
                silently_remove_file(os.path.join(dirname, scatter_png_fn))
                silently_remove_file(os.path.join(dirname, scatter_ind_pdf_fn))
                silently_remove_file(os.path.join(dirname, kde_png_fn))
                silently_remove_file(os.path.join(dirname, kde_ind_pdf_fn))
        except:
            APP_LOGGER.exception("Error in Genotyper post request process callback.")
            error_msg = str(sys.exc_info()[1])
            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   RESULT: None,
                                   PDF: None,
                                   PNG: None,
                                   PNG_SUM: None,
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(SA_GENOTYPER_COLLECTION, query, {})) > 0:
                db_connector.update(SA_GENOTYPER_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(os.path.join(dirname, pdf_fn))
                silently_remove_file(os.path.join(dirname, scatter_png_fn))
                silently_remove_file(os.path.join(dirname, scatter_ind_pdf_fn))
                silently_remove_file(os.path.join(dirname, kde_png_fn))
                silently_remove_file(os.path.join(dirname, kde_ind_pdf_fn))

    return process_callback

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = GenotyperPostFunction()
    print function
