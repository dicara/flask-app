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
@date:   Feb 17, 2015
'''

#=============================================================================
# Imports
#=============================================================================
import os
import shutil
import time
import unittest
import yaml

from datetime import datetime

from bioweb_api.tests.test_utils import post_data, get_data, \
    delete_data, add_url_argument
from bioweb_api.utilities import io_utilities
from bioweb_api.apis.ApiConstants import UUID, FIDUCIAL_DYE, ASSAY_DYE,\
    NUM_PROBES, TRAINING_FACTOR, DYE_LEVELS, PLOT, \
    JOB_NAME, JOB_TYPE_NAME, JOB_TYPE, ARCHIVE, DEVICE, DYES, \
    STATUS, SUBMIT_DATESTAMP, START_DATESTAMP, FINISH_DATESTAMP, \
    URL, CONFIG_URL, REPORT, RESULT, CONFIG, \
    FILTERED_DYES, IGNORED_DYES, PF_TRAINING_FACTOR, UI_THRESHOLD,\
    CALC_DROP_PROB, PA_PROCESS_UUID, PLOT_URL, REPORT_URL, SA_IDENTITY_UUID, \
    JOE, FAM, JOB_STATUS, KDE_PLOT, KDE_PLOT_URL, SCATTER_PLOT, \
    SCATTER_PLOT_URL, REQUIRED_DROPS, EXP_DEF, PDF, PNG, PNG_SUM, VCF
from bioweb_api import app, HOME_DIR, TMP_PATH, PA_PROCESS_COLLECTION, SA_IDENTITY_COLLECTION,\
    SA_ASSAY_CALLER_COLLECTION
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import IDENTITY
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import ASSAY_CALLER
from bioweb_api.apis.secondary_analysis.GenotyperPostFunction import GENOTYPER
from secondary_analysis.constants import AC_TRAINING_FACTOR

from bioweb_api.DbConnector import DbConnector

#=============================================================================
# Setup Logging
#=============================================================================
import tornado.options
tornado.options.parse_command_line()

#=============================================================================
# Private Static Variables
#=============================================================================
_TEST_DIR                 = os.path.abspath(os.path.dirname(__file__))
_ARCHIVE_DIR              = "/mnt/runs/bamboo_test_data/bioweb-api/secondary_analysis"
_DB_CONNECTOR             = DbConnector.Instance()
_EXPECTED_IDENTITY_REPORT = "expected_report.yaml"
_SECONDARY_ANALYSIS_URL   = "/api/v1/SecondaryAnalysis"
_IDENTITY_URL             = os.path.join(_SECONDARY_ANALYSIS_URL, IDENTITY)
_ASSAY_CALLER_URL         = os.path.join(_SECONDARY_ANALYSIS_URL, ASSAY_CALLER)
_GENOTYPER_URL            = os.path.join(_SECONDARY_ANALYSIS_URL, GENOTYPER)
_JOB_NAME                 = "test_pa_process_job"

_IDENTITY_JOB_NAME     = "test_identity"
_ASSAY_CALLER_JOB_NAME = "test_assay_caller"
_GENOTYPER_JOB_NAME    = "test_genotyper2"
_FIDUCIAL_DYE          = "joe"
_ASSAY_DYE             = "fam"
_AC_NUM_PROBES         = 8
_ID_NUM_PROBES         = 0
_TRAINING_FACTOR       = 10
_DYE_LEVELS            = "594:4,633:3,cy5.5:4,pe:2,pe-cy7:2,IF790:2"
_EXP_DEF_NAME          = "ABL_8elements_V4"
_REQUIRED_DROPS        = 8000

# ABL r2 Lot 0003 reagents Run
_ABL_IDENTITY_JOB_NAME = "test_abl_identity"
_ABL_ID_NUM_PROBES     = 8
_ABL_DYE_LEVELS        = "594:2,633:2,cy5.5:2"
_ABL_FILTERED_DYES     = "pe"
_ABL_EXPECTED_IDENTITY_REPORT = "abl_expected_report.yaml"

io_utilities.safe_make_dirs(HOME_DIR)
io_utilities.safe_make_dirs(TMP_PATH)

#=============================================================================
# Class
#=============================================================================
class TestSecondaryAnalysisAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ########################################################################
        # Primary Analysis Records
        ########################################################################
        cls._pa_uuid   = "4a67e0fa-d513-468b-a8e2-5fc925b6807b"
        cls._pa_record = {
                          JOB_NAME : "golden_run",
                          JOB_TYPE_NAME : JOB_TYPE.pa_process,# @UndefinedVariable
                          UUID : cls._pa_uuid,
                          ARCHIVE : "20141015_b7_312ele_60mw_g2_18000_2",
                          DEVICE : "beta7",
                          DYES : [ 
                                  "594", 
                                  "633", 
                                  "cy5.5", 
                                  "pe", 
                                  "pe-cy7"
                                 ],
                          STATUS : JOB_STATUS.succeeded, # @UndefinedVariable
                          SUBMIT_DATESTAMP : datetime.today(),
                          START_DATESTAMP : datetime.today(),
                          FINISH_DATESTAMP : datetime.today(),
                          URL : "http://bioweb/results/8020/" + cls._pa_uuid,
                          CONFIG_URL : "http://bioweb/results/8020/" + cls._pa_uuid + ".cfg",
                          RESULT : os.path.join(_TEST_DIR, cls._pa_uuid),
                          CONFIG : os.path.join(_TEST_DIR, cls._pa_uuid + ".cfg"),
                         }

        cls._abl_pa_uuid   = "cbb2515d-b11e-4ebd-88a3-8e7ff2ae75b8"
        cls._abl_pa_record = {
                              JOB_NAME : "2016-01-28_05.22pm_beta_15-ddicara",
                              JOB_TYPE_NAME : JOB_TYPE.pa_process,# @UndefinedVariable
                              UUID : cls._abl_pa_uuid,
                              ARCHIVE : "2016-01-28_05.22pm_beta_15",
                              DEVICE : "beta7",
                              DYES : [ 
                                      "594", 
                                      "633", 
                                      "cy5.5", 
                                      "pe",
                                      "joe",
                                      "fam"
                                     ],
                              STATUS : JOB_STATUS.succeeded, # @UndefinedVariable
                              SUBMIT_DATESTAMP : datetime.today(),
                              START_DATESTAMP : datetime.today(),
                              FINISH_DATESTAMP : datetime.today(),
                              URL : "http://bioweb/results/8020/" + cls._abl_pa_uuid,
                              CONFIG_URL : "http://bioweb/results/8020/" + cls._abl_pa_uuid + ".cfg",
                              RESULT : os.path.join(_ARCHIVE_DIR, cls._abl_pa_uuid),
                              CONFIG : os.path.join(_ARCHIVE_DIR, cls._abl_pa_uuid + ".cfg"),
                             }
        _DB_CONNECTOR.insert(PA_PROCESS_COLLECTION, [cls._pa_record,
                                                     cls._abl_pa_record])
        
        ########################################################################
        # Identity Records
        ########################################################################
        cls._identity_uuid = "fb549af2-d807-492c-8b73-4f8c41435917"
        cls._id_record = {
                          FIDUCIAL_DYE: "joe",
                          ASSAY_DYE: "fam",
                          NUM_PROBES: 8,
                          TRAINING_FACTOR: 1000,
                          DYE_LEVELS : [ 
                                  ["594", 2],
                                  ["633", 2], 
                                  ["cy5.5", 2],
                                 ],
                          IGNORED_DYES: [],
                          FILTERED_DYES: ['pe'],
                          PF_TRAINING_FACTOR: 10,
                          UI_THRESHOLD: 4000,
                          UUID : cls._identity_uuid,
                          PA_PROCESS_UUID: cls._abl_pa_uuid,
                          STATUS : JOB_STATUS.succeeded, # @UndefinedVariable
                          JOB_NAME : "2016-01-28_05.22pm_beta_15-ddicara",
                          JOB_TYPE_NAME : JOB_TYPE.sa_identity,# @UndefinedVariable
                          SUBMIT_DATESTAMP : datetime.today(),
                          CALC_DROP_PROB: False,
                          START_DATESTAMP : datetime.today(),
                          FINISH_DATESTAMP : datetime.today(),
                          URL : "http://bioweb/results/8020/" + cls._identity_uuid,
                          RESULT : os.path.join(_ARCHIVE_DIR, cls._identity_uuid),
                          PLOT: os.path.join(_ARCHIVE_DIR, cls._identity_uuid + ".png"),
                          PLOT_URL: "http://bioweb/results/8010/" +  cls._identity_uuid + ".png",
                          REPORT: os.path.join(_ARCHIVE_DIR, cls._identity_uuid + ".yaml"),
                          REPORT_URL: "http://bioweb/results/8010/" + cls._identity_uuid + ".yaml",
                         }
        _DB_CONNECTOR.insert(SA_IDENTITY_COLLECTION, [cls._id_record])
        
        ########################################################################
        # Assay Caller Records
        ########################################################################
        cls._ac_uuid = "13e80cb5-17d7-469f-8714-71520342d3a5"
        cls._ac_record = {
                          JOB_NAME : "2016-01-28_05.22pm_beta_15-ddicara",
                          JOB_TYPE_NAME : JOB_TYPE.sa_assay_calling, # @UndefinedVariable
                          UUID : cls._ac_uuid,
                          SA_IDENTITY_UUID: cls._identity_uuid,
                          FIDUCIAL_DYE: JOE,
                          ASSAY_DYE: FAM,
                          NUM_PROBES: 8,
                          TRAINING_FACTOR: 1000,
                          STATUS : JOB_STATUS.succeeded, # @UndefinedVariable
                          SUBMIT_DATESTAMP : datetime.today(),
                          START_DATESTAMP : datetime.today(),
                          FINISH_DATESTAMP : datetime.today(),
                          RESULT : os.path.join(_ARCHIVE_DIR, cls._ac_uuid),
                          URL : "http://bioweb/results/8020/" + cls._ac_uuid,
                          KDE_PLOT: os.path.join(_ARCHIVE_DIR, cls._ac_uuid + "_kde.png"),
                          KDE_PLOT_URL : "http://bioweb/results/8020/" + cls._ac_uuid + "_kde.png",
                          SCATTER_PLOT: os.path.join(_ARCHIVE_DIR, cls._ac_uuid + "_scatter.png"),
                          SCATTER_PLOT_URL : "http://bioweb/results/8020/" + cls._ac_uuid + "_scatter.png",
                         }
        _DB_CONNECTOR.insert(SA_ASSAY_CALLER_COLLECTION, [cls._ac_record])

    @classmethod
    def tearDownClass(cls):
        _DB_CONNECTOR.remove(PA_PROCESS_COLLECTION, 
                             {UUID: {"$in": [cls._pa_uuid,
                                             cls._abl_pa_uuid]}})
        _DB_CONNECTOR.remove(SA_IDENTITY_COLLECTION, 
                             {UUID: {"$in": [cls._identity_uuid]}})
        _DB_CONNECTOR.remove(SA_ASSAY_CALLER_COLLECTION,
                             {UUID: {"$in": [cls._ac_uuid]}})
        
    def setUp(self):
        self._client = app.test_client(self)
        self._exp_id_report_path = os.path.join(_TEST_DIR, _EXPECTED_IDENTITY_REPORT)

        self.assertTrue(os.path.isfile(self._exp_id_report_path),
                        "Expected identity result file doesn't exist: %s" % \
                        self._exp_id_report_path)
        
        self._exp_abl_id_report_path = os.path.join(_ARCHIVE_DIR, _ABL_EXPECTED_IDENTITY_REPORT)

        self.assertTrue(os.path.isfile(self._exp_abl_id_report_path),
                        "Expected ABL identity result file doesn't exist: %s" % \
                        self._exp_abl_id_report_path)
        
    def test_results_exist(self):
        """
        This tests that setUp properly inserts the primary analysis result in
        the database and that the result files exist.
        """
        response = _DB_CONNECTOR.find_one(PA_PROCESS_COLLECTION, UUID,
                                          self._pa_uuid)

        msg = "No entries in the DB with UUID = %s" % self._pa_uuid
        self.assertTrue(response, msg)

        msg = "Result file cannot be found: %s" % response[RESULT]
        self.assertTrue(os.path.isfile(response[RESULT]), msg)

        msg = "Config file cannot be found: %s" % response[CONFIG]
        self.assertTrue(os.path.isfile(response[CONFIG]), msg)

        response = _DB_CONNECTOR.find_one(PA_PROCESS_COLLECTION, UUID,
                                          self._abl_pa_uuid)

        msg = "No entries in the DB with UUID = %s" % self._abl_pa_uuid
        self.assertTrue(response, msg)

        msg = "Result file cannot be found: %s" % response[RESULT]
        self.assertTrue(os.path.isfile(response[RESULT]), msg)

        msg = "Config file cannot be found: %s" % response[CONFIG]
        self.assertTrue(os.path.isfile(response[CONFIG]), msg)

        response = _DB_CONNECTOR.find_one(SA_IDENTITY_COLLECTION, UUID,
                                          self._identity_uuid)

        msg = "No entries in the DB with UUID = %s" % self._identity_uuid
        self.assertTrue(response, msg)

        msg = "Result file cannot be found: %s" % response[RESULT]
        self.assertTrue(os.path.isfile(response[RESULT]), msg)

        response = _DB_CONNECTOR.find_one(SA_ASSAY_CALLER_COLLECTION, UUID,
                                          self._ac_uuid)

        msg = "No entries in the DB with UUID = %s" % self._ac_uuid
        self.assertTrue(response, msg)

        msg = "Result file cannot be found: %s" % response[RESULT]
        self.assertTrue(os.path.isfile(response[RESULT]), msg)

    def test_identity_on_golden_temple(self):
        """
        Test the POST, GET and DELETE identity APIs.
        """
        # Construct url
        url = _IDENTITY_URL
        url = add_url_argument(url, UUID, self._pa_record[UUID], True) 
        url = add_url_argument(url, JOB_NAME, _IDENTITY_JOB_NAME) 
        url = add_url_argument(url, NUM_PROBES, _ID_NUM_PROBES) 
        url = add_url_argument(url, TRAINING_FACTOR, _TRAINING_FACTOR)
        url = add_url_argument(url, DYE_LEVELS, _DYE_LEVELS)
               
        # Submit identity job
        response      = post_data(self, url, 200)
        identity_uuid = response[IDENTITY][0][UUID]
                   
        # Test that submitting two jobs with the same name fails and returns
        # the appropriate error code. 
        post_data(self, url, 403)
           
        running = True
        while running:
            time.sleep(10)
            response = get_data(self, _IDENTITY_URL, 200)
            for job in response[IDENTITY]:
                if identity_uuid == job[UUID]:
                    job_details = job
                    running     = job_details[STATUS] == 'running'
     
        msg = "%s doesn't exist in job_details." % REPORT
        self.assertTrue(REPORT in job_details, msg)
        obs_id_report_path = job_details[REPORT]
        msg = "Report path doesn't exist: %s" % obs_id_report_path
        self.assertTrue(os.path.isfile(obs_id_report_path), msg)
        shutil.copy(obs_id_report_path, "observed_report.yaml")
     
        msg = "%s doesn't exist in job_details." % PLOT
        self.assertTrue(PLOT in job_details, msg)
        identity_plot_path = job_details[PLOT]
        msg = "Plot path doesn't exist: %s" % identity_plot_path
        self.assertTrue(os.path.isfile(identity_plot_path), msg)
        shutil.copy(identity_plot_path, "identity_plot.png")
     
        msg = "%s doesn't exist in job_details." % RESULT
        self.assertTrue(RESULT in job_details, msg)
        result_path = job_details[RESULT]
        msg = "Result path doesn't exist: %s" % result_path
        self.assertTrue(os.path.isfile(result_path), msg)
        shutil.copy(result_path, "observed_identity.txt")
     
        # check if expected clusters were found
        with open(self._exp_id_report_path) as f_exp, open(obs_id_report_path) as f_obs:
            exp_report = yaml.load(f_exp)
            obs_report = yaml.load(f_obs)
        exp_clusters = exp_report['MODEL_METRICS']['CLUSTERS']
        obs_clusters = obs_report['MODEL_METRICS']['CLUSTERS']
     
        exp_clus_ids = exp_clusters.keys()
        exp_clus_ids.sort()
        obs_clus_ids = obs_clusters.keys()
        obs_clus_ids.sort()
     
        msg = 'Identity result contains barcode IDs that were not expected.'
        self.assertTrue(exp_clus_ids == obs_clus_ids, msg)
         
        # Delete sa assay caller job
        delete_url = add_url_argument(_IDENTITY_URL, UUID, identity_uuid, True)
        delete_data(self, delete_url, 200)
                   
        # Ensure job no longer exists in the database
        response = get_data(self, _IDENTITY_URL, 200)
        for job in response[IDENTITY]:
            msg = "PA process job %s still exists in database." % identity_uuid
            self.assertNotEqual(identity_uuid, job[UUID], msg)
                 
    def test_identity_on_abl(self):
        """
        Test the POST, GET and DELETE identity APIs.
        """
        # Construct url
        url = _IDENTITY_URL
        url = add_url_argument(url, UUID, self._abl_pa_record[UUID], True) 
        url = add_url_argument(url, JOB_NAME, _ABL_IDENTITY_JOB_NAME) 
        url = add_url_argument(url, NUM_PROBES, _ABL_ID_NUM_PROBES) 
        url = add_url_argument(url, DYE_LEVELS, _ABL_DYE_LEVELS)
        url = add_url_argument(url, FILTERED_DYES, _ABL_FILTERED_DYES)
               
        # Submit identity job
        response      = post_data(self, url, 200)
        identity_uuid = response[IDENTITY][0][UUID]
                   
        # Test that submitting two jobs with the same name fails and returns
        # the appropriate error code. 
        post_data(self, url, 403)
           
        running = True
        while running:
            time.sleep(10)
            response = get_data(self, _IDENTITY_URL, 200)
            for job in response[IDENTITY]:
                if identity_uuid == job[UUID]:
                    job_details = job
                    running     = job_details[STATUS] == 'running'
     
        msg = "%s doesn't exist in job_details." % REPORT
        self.assertTrue(REPORT in job_details, msg)
        obs_id_report_path = job_details[REPORT]
             
        msg = "Report path doesn't exist: %s" % obs_id_report_path
        self.assertTrue(os.path.isfile(obs_id_report_path), msg)
     
        shutil.copy(obs_id_report_path, "abl_observed_report.yaml")
     
        msg = "%s doesn't exist in job_details." % PLOT
        self.assertTrue(PLOT in job_details, msg)
        identity_plot_path = job_details[PLOT]
             
        msg = "Plot path doesn't exist: %s" % identity_plot_path
        self.assertTrue(os.path.isfile(identity_plot_path), msg)
     
        shutil.copy(identity_plot_path, "abl_identity_plot.png")
     
        msg = "%s doesn't exist in job_details." % RESULT
        self.assertTrue(RESULT in job_details, msg)
        result_path = job_details[RESULT]
             
        msg = "Result path doesn't exist: %s" % result_path
        self.assertTrue(os.path.isfile(result_path), msg)
     
        shutil.copy(result_path, "abl_observed_identity.txt")
     
        # check if expected clusters were found
        with open(self._exp_abl_id_report_path) as f_exp, open(obs_id_report_path) as f_obs:
            exp_report = yaml.load(f_exp)
            obs_report = yaml.load(f_obs)
        exp_clusters = exp_report['MODEL_METRICS']['CLUSTERS']
        obs_clusters = obs_report['MODEL_METRICS']['CLUSTERS']
     
        exp_clus_ids = exp_clusters.keys()
        exp_clus_ids.sort()
        obs_clus_ids = obs_clusters.keys()
        obs_clus_ids.sort()
     
        msg = 'Identity result contains barcode IDs that were not expected.'
        self.assertTrue(exp_clus_ids == obs_clus_ids, msg)
         
        # Delete sa assay caller job
        delete_url = add_url_argument(_IDENTITY_URL, UUID, identity_uuid, True)
        delete_data(self, delete_url, 200)
                   
        # Ensure job no longer exists in the database
        response = get_data(self, _IDENTITY_URL, 200)
        for job in response[IDENTITY]:
            msg = "PA process job %s still exists in database." % identity_uuid
            self.assertNotEqual(identity_uuid, job[UUID], msg)
                 
    def test_assay_caller(self):
        """
        Test the POST, GET and DELETE assay caller APIs.
        """
        # Construct url
        url = _ASSAY_CALLER_URL
        url = add_url_argument(url, UUID, self._id_record[UUID], True)
        url = add_url_argument(url, JOB_NAME, _ASSAY_CALLER_JOB_NAME)
        url = add_url_argument(url, FIDUCIAL_DYE, _FIDUCIAL_DYE)
        url = add_url_argument(url, ASSAY_DYE, _ASSAY_DYE)
        url = add_url_argument(url, NUM_PROBES, _AC_NUM_PROBES)
        url = add_url_argument(url, TRAINING_FACTOR, AC_TRAINING_FACTOR)
      
        # Submit identity job
        response          = post_data(self, url, 200)
        assay_caller_uuid = response[ASSAY_CALLER][0][UUID]
      
        # Test that submitting two jobs with the same name fails and returns
        # the appropriate error code.
        post_data(self, url, 403)
      
        running = True
        while running:
            time.sleep(10)
            response = get_data(self, _ASSAY_CALLER_URL, 200)
            for job in response[ASSAY_CALLER]:
                if assay_caller_uuid == job[UUID]:
                    job_details = job
                    running     = job_details[STATUS] == 'running'
      
        # Copy result files to cwd for bamboo to ingest as artifacts
        assay_caller_txt_path = None
        if RESULT in job_details:
            assay_caller_txt_path = job_details[RESULT]
            if os.path.isfile(assay_caller_txt_path):
                shutil.copy(assay_caller_txt_path, "observed_assay_caller.txt")
      
        kde_plot_path = None
        if KDE_PLOT in job_details:
            kde_plot_path = job_details[KDE_PLOT]
            if os.path.isfile(kde_plot_path):
                shutil.copy(kde_plot_path, "observed_kde_plot.png")
      
        scatter_plot_path = None
        if SCATTER_PLOT in job_details:
            scatter_plot_path = job_details[SCATTER_PLOT]
            if os.path.isfile(scatter_plot_path):
                shutil.copy(scatter_plot_path, "observed_scatter_plot.png")
      
        error = ""
        if 'error' in job_details:
            error = job_details['error']
        msg = "Expected sa assay caller job status succeeded, but found %s. " \
              "Error: %s" % (job_details[STATUS], error)
        self.assertEquals(job_details[STATUS], "succeeded", msg)
      
        # Delete sa assay caller job
        delete_url = add_url_argument(_ASSAY_CALLER_URL, UUID,
                                      assay_caller_uuid, True)
        delete_data(self, delete_url, 200)
      
        # Ensure job no longer exists in the database
        response = get_data(self, _ASSAY_CALLER_URL, 200)
        for job in response[ASSAY_CALLER]:
            msg = "PA process job %s still exists in database." % assay_caller_uuid
            self.assertNotEqual(assay_caller_uuid, job[UUID], msg)

    def test_genotyper(self):
        """
        Test the POST, GET and DELETE assay caller APIs.
        """
        # Construct url
        url = _GENOTYPER_URL
        url = add_url_argument(url, UUID, self._ac_record[UUID], True)
        url = add_url_argument(url, JOB_NAME, _GENOTYPER_JOB_NAME)
        url = add_url_argument(url, EXP_DEF, _EXP_DEF_NAME)
        url = add_url_argument(url, REQUIRED_DROPS, _REQUIRED_DROPS)
  
        # Submit identity job
        response       = post_data(self, url, 200)
        genotyper_uuid = response[GENOTYPER][0][UUID]
  
        # Test that submitting two jobs with the same name fails and returns
        # the appropriate error code.
        post_data(self, url, 403)
  
        running = True
        while running:
            time.sleep(10)
            response = get_data(self, _GENOTYPER_URL, 200)
            for job in response[GENOTYPER]:
                if genotyper_uuid == job[UUID]:
                    job_details = job
                    running     = job_details[STATUS] == 'running'
  
        # Copy result files to cwd for bamboo to ingest as artifacts
        self.ensure_and_copy_genotyper_result(job_details, RESULT, ".%s" % VCF)
        self.ensure_and_copy_genotyper_result(job_details, PDF)
        self.ensure_and_copy_genotyper_result(job_details, PNG)
        self.ensure_and_copy_genotyper_result(job_details, PNG_SUM, "_sum.png")

        error = ""
        if 'error' in job_details:
            error = job_details['error']
        msg = "Expected sa assay caller job status succeeded, but found %s. " \
              "Error: %s" % (job_details[STATUS], error)
        self.assertEquals(job_details[STATUS], "succeeded", msg)
  
        # Delete sa assay caller job
        delete_url = add_url_argument(_GENOTYPER_URL, UUID,
                                      genotyper_uuid, True)
        delete_data(self, delete_url, 200)
        
        self.ensure_genotyper_result_deleted(job_details, RESULT)
        self.ensure_genotyper_result_deleted(job_details, PDF)
        self.ensure_genotyper_result_deleted(job_details, PNG)
        self.ensure_genotyper_result_deleted(job_details, PNG_SUM)
        
        # Ensure job no longer exists in the database
        response = get_data(self, _GENOTYPER_URL, 200)
        for job in response[GENOTYPER]:
            msg = "Genotyper job %s still exists in database." % genotyper_uuid
            self.assertNotEqual(genotyper_uuid, job[UUID], msg)

    def ensure_and_copy_genotyper_result(self, job_details, key, file_ext=None):
        self.assertTrue(key in job_details, "%s not in job_details." % key)
        msg = "Result file doesn't exist: %s" % job_details[key]
        self.assertTrue(os.path.isfile(job_details[key]), msg)
        if file_ext is None:
            shutil.copy(job_details[key], "observed_genotyper.%s" % key)
        else:
            shutil.copy(job_details[key], "observed_genotyper%s" % file_ext)

    def ensure_genotyper_result_deleted(self, job_details, key):
        msg = "Result file not deleted: %s" % job_details[key]
        self.assertFalse(os.path.isfile(job_details[key]), msg)

#=============================================================================
# Main
#=============================================================================
if __name__ == "__main__":
    unittest.main()