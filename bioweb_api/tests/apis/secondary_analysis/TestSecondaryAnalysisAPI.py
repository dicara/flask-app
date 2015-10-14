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
import filecmp
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
    NUM_PROBES, TRAINING_FACTOR, THRESHOLD, OUTLIERS, DYE_LEVELS, PLOT, \
    JOB_NAME, JOB_TYPE_NAME, JOB_TYPE, ARCHIVE, COV_TYPE, DEVICE, DYES, \
    STATUS, SUBMIT_DATESTAMP, START_DATESTAMP, FINISH_DATESTAMP, \
    URL, CONFIG_URL, REPORT, RESULT, CONFIG, KDE_PLOT, SCATTER_PLOT
from bioweb_api import app, HOME_DIR, TMP_PATH, PA_PROCESS_COLLECTION
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import IDENTITY
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import ASSAY_CALLER

from bioweb_api.DbConnector import DbConnector
from secondary_analysis.constants import COVARIANCE_TYPES

#=============================================================================
# Private Static Variables
#=============================================================================
_TEST_DIR                 = os.path.abspath(os.path.dirname(__file__))
_DB_CONNECTOR             = DbConnector.Instance()
_EXPECTED_IDENTITY_RESULT = "expected_identity.txt"
_EXPECTED_IDENTITY_REPORT = "expected_report.yaml"
_SECONDARY_ANALYSIS_URL   = "/api/v1/SecondaryAnalysis"
_IDENTITY_URL             = os.path.join(_SECONDARY_ANALYSIS_URL, IDENTITY)
_ASSAY_CALLER_URL         = os.path.join(_SECONDARY_ANALYSIS_URL, ASSAY_CALLER)
_JOB_NAME                 = "test_pa_process_job"

_IDENTITY_JOB_NAME     = "test_identity"
_ASSAY_CALLER_JOB_NAME = "test_assay_caller"
_FIDUCIAL_DYE          = "joe"
_ASSAY_DYE             = "fam"
_AC_NUM_PROBES         = 1000
_ID_NUM_PROBES         = 0
_TRAINING_FACTOR       = 10
_THRESHOLD             = 2500.0
_OUTLIERS              = False
_COV_TYPE              = COVARIANCE_TYPES[-1]
_DYE_LEVELS            = "594:4,633:3,cy5.5:4,pe:2,pe-cy7:2,IF790:2"

io_utilities.safe_make_dirs(HOME_DIR)
io_utilities.safe_make_dirs(TMP_PATH)

#=============================================================================
# Private Static Variables
#=============================================================================

#=============================================================================
# Class
#=============================================================================
class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._pa_process_ac_uuid = "402895fd-6a44-411c-817b-cba84c2abb8c"
        cls._ac_record = {
                          JOB_NAME : "test_binary",
                          JOB_TYPE_NAME : JOB_TYPE.pa_process,# @UndefinedVariable
                          UUID : cls._pa_process_ac_uuid,
                          ARCHIVE : "2014-12-07beta9/20141207ablcontlowT61_2_25",
                          DEVICE : "beta7",
                          DYES : [ 
                                  "594", 
                                  "633", 
                                  "cy5.5", 
                                  "fam", 
                                  "joe", 
                                  "pe-cy7"
                                 ],
                          STATUS : "succeeded",
                          SUBMIT_DATESTAMP : datetime.today(),
                          START_DATESTAMP : datetime.today(),
                          FINISH_DATESTAMP : datetime.today(),
                          URL : "http://bioweb/results/8020/" + cls._pa_process_ac_uuid,
                          CONFIG_URL : "http://bioweb/results/8020/" + cls._pa_process_ac_uuid + ".cfg",
                          RESULT : os.path.join(_TEST_DIR, cls._pa_process_ac_uuid),
                          CONFIG : os.path.join(_TEST_DIR, cls._pa_process_ac_uuid + ".cfg"),
                         }
        cls._pa_process_id_uuid = "4a67e0fa-d513-468b-a8e2-5fc925b6807b"
        cls._id_record = {
                          JOB_NAME : "golden_run",
                          JOB_TYPE_NAME : JOB_TYPE.pa_process,# @UndefinedVariable
                          UUID : cls._pa_process_id_uuid,
                          ARCHIVE : "20141015_b7_312ele_60mw_g2_18000_2",
                          DEVICE : "beta7",
                          DYES : [ 
                                  "594", 
                                  "633", 
                                  "cy5.5", 
                                  "pe", 
                                  "pe-cy7"
                                 ],
                          STATUS : "succeeded",
                          SUBMIT_DATESTAMP : datetime.today(),
                          START_DATESTAMP : datetime.today(),
                          FINISH_DATESTAMP : datetime.today(),
                          URL : "http://bioweb/results/8020/" + cls._pa_process_id_uuid,
                          CONFIG_URL : "http://bioweb/results/8020/" + cls._pa_process_id_uuid + ".cfg",
                          RESULT : os.path.join(_TEST_DIR, cls._pa_process_id_uuid),
                          CONFIG : os.path.join(_TEST_DIR, cls._pa_process_id_uuid + ".cfg"),
                         }
        _DB_CONNECTOR.insert(PA_PROCESS_COLLECTION, [cls._ac_record, 
                                                     cls._id_record])
        
    @classmethod
    def tearDownClass(cls):
        _DB_CONNECTOR.remove(PA_PROCESS_COLLECTION, 
                             {UUID: {"$in": [cls._pa_process_ac_uuid, 
                                             cls._pa_process_id_uuid]}})
        
    def setUp(self):
        self._client = app.test_client(self)
        self._exp_id_report_path = os.path.join(_TEST_DIR, _EXPECTED_IDENTITY_REPORT)

        self.assertTrue(os.path.isfile(self._exp_id_report_path),
                        "Expected identity result file doesn't exist: %s" % \
                        self._exp_id_report_path)
        
    def test_pa_results_exist(self):
        """
        This tests that setUp properly inserts the primary analysis result in
        the database and that the result files exist.
        """
        response = _DB_CONNECTOR.find_one(PA_PROCESS_COLLECTION, UUID,
                                          self._pa_process_ac_uuid)

        msg = "No entries in the DB with UUID = %s" % self._pa_process_ac_uuid
        self.assertTrue(response, msg)

        msg = "Result file cannot be found: %s" % response[RESULT]
        self.assertTrue(os.path.isfile(response[RESULT]), msg)

        msg = "Config file cannot be found: %s" % response[CONFIG]
        self.assertTrue(os.path.isfile(response[CONFIG]), msg)

        response = _DB_CONNECTOR.find_one(PA_PROCESS_COLLECTION, UUID,
                                          self._pa_process_id_uuid)

        msg = "No entries in the DB with UUID = %s" % self._pa_process_id_uuid
        self.assertTrue(response, msg)

        msg = "Result file cannot be found: %s" % response[RESULT]
        self.assertTrue(os.path.isfile(response[RESULT]), msg)

        msg = "Config file cannot be found: %s" % response[CONFIG]
        self.assertTrue(os.path.isfile(response[CONFIG]), msg)

    def test_assay_caller(self):
        """
        Test the POST, GET and DELETE assay caller APIs.
        """
        # Construct url
        url = _ASSAY_CALLER_URL
        url = add_url_argument(url, UUID, self._ac_record[UUID], True)
        url = add_url_argument(url, JOB_NAME, _ASSAY_CALLER_JOB_NAME)
        url = add_url_argument(url, FIDUCIAL_DYE, _FIDUCIAL_DYE)
        url = add_url_argument(url, ASSAY_DYE, _ASSAY_DYE)
        url = add_url_argument(url, NUM_PROBES, _AC_NUM_PROBES)
        url = add_url_argument(url, TRAINING_FACTOR, _TRAINING_FACTOR)
        url = add_url_argument(url, THRESHOLD, _THRESHOLD)
        url = add_url_argument(url, OUTLIERS, _OUTLIERS)
        url = add_url_argument(url, COV_TYPE, _COV_TYPE)

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
            
    def test_identity(self):
        """
        Test the POST, GET and DELETE identity APIs.
        """
        # Construct url
        url = _IDENTITY_URL
        url = add_url_argument(url, UUID, self._id_record[UUID], True) 
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

        # Copy result files to cwd for bamboo to ingest as artifacts
        obs_id_report_path = None
        if REPORT in job_details:
            obs_id_report_path = job_details[REPORT]
            if os.path.isfile(obs_id_report_path):
                shutil.copy(obs_id_report_path, "observed_report.yaml")

        identity_plot_path = None
        if PLOT in job_details:
            identity_plot_path = job_details[PLOT]
            if os.path.isfile(identity_plot_path):
                shutil.copy(identity_plot_path, "identity_plot.png")

        # check if expected clusters were found
        with open(self._exp_id_report_path) as f_exp, open(obs_id_report_path) as f_obs:
            exp_report = yaml.load(f_exp)
            obs_report = yaml.load(f_obs)
        exp_clusters = exp_report['IDENTITY MODEL METRICS']['CLUSTERS']
        obs_clusters = obs_report['IDENTITY MODEL METRICS']['CLUSTERS']

        exp_clus_ids = [clus.keys()[0] for clus in exp_clusters]
        obs_clus_ids = [clus.keys()[0] for clus in obs_clusters]

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

#=============================================================================
# Main
#=============================================================================
if __name__ == "__main__":
    unittest.main()