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

from datetime import datetime
from uuid import uuid4

from bioweb_api.tests.test_utils import post_data, get_data, \
    delete_data, read_yaml
from bioweb_api.utilities import io_utilities
from bioweb_api.apis.ApiConstants import UUID, FIDUCIAL_DYE, ASSAY_DYE,\
    NUM_PROBES, TRAINING_FACTOR, THRESHOLD, OUTLIERS
from bioweb_api import app, HOME_DIR, TARGETS_UPLOAD_PATH, PROBES_UPLOAD_PATH, \
    RESULTS_PATH, REFS_PATH, PLATES_UPLOAD_PATH, TMP_PATH, PA_PROCESS_COLLECTION
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import IDENTITY
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import ASSAY_CALLER

from bioweb_api.apis.ApiConstants import JOB_NAME, JOB_TYPE_NAME, JOB_TYPE, \
    UUID, ARCHIVE, COV_TYPE, \
    DEVICE, DYES, STATUS, SUBMIT_DATESTAMP, START_DATESTAMP, FINISH_DATESTAMP, \
    URL, CONFIG_URL, RESULT, CONFIG, KDE_PLOT, SCATTER_PLOT

from bioweb_api.DbConnector import DbConnector
from secondary_analysis.constants import COVARIANCE_TYPES

from pprint import pformat

#=============================================================================
# Private Static Variables
#=============================================================================
_TEST_DIR                 = os.path.abspath(os.path.dirname(__file__))
_DB_CONNECTOR             = DbConnector.Instance()
_EXPECTED_ANALYSIS_RESULT = "expected_analysis.txt"
_EXPECTED_CONFIG_RESULT   = "expected.cfg"
_SECONDARY_ANALYSIS_URL   = "/api/v1/SecondaryAnalysis"
_IDENTITY_URL             = os.path.join(_SECONDARY_ANALYSIS_URL, IDENTITY)
_ASSAY_CALLER_URL         = os.path.join(_SECONDARY_ANALYSIS_URL, ASSAY_CALLER)
_RESULT                   = "result"
_CONFIG                   = "config"
_STATUS                   = "status"
_PROCESS                  = "Process"
_DYES                     = ['633', 'pe']
_DEVICE                   = "beta8"
_JOB_NAME                 = "test_pa_process_job"


_IDENTITY_JOB_NAME     = "test_identity"
_ASSAY_CALLER_JOB_NAME = "test_assay_caller"
_FIDUCIAL_DYE          = "joe"
_ASSAY_DYE             = "fam"
_NUM_PROBES            = 1000
_TRAINING_FACTOR       = 10
_THRESHOLD             = 0.0
_OUTLIERS              = False
_COV_TYPE              = COVARIANCE_TYPES[-1]
# _DYE_LEVELS        = ""





io_utilities.safe_make_dirs(HOME_DIR)
io_utilities.safe_make_dirs(TMP_PATH)

#=============================================================================
# Private Static Variables
#=============================================================================

#=============================================================================
# Class
#=============================================================================
class Test(unittest.TestCase):

    def setUp(self):
        self._client          = app.test_client(self)
        self._pa_process_uuid = "402895fd-6a44-411c-817b-cba84c2abb8c"
        self._record = {
                        JOB_NAME : "test_binary",
                        JOB_TYPE_NAME : JOB_TYPE.pa_process,# @UndefinedVariable
                        UUID : self._pa_process_uuid,
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
                        URL : "http://bioweb/results/8020/" + self._pa_process_uuid,
                        CONFIG_URL : "http://bioweb/results/8020/" + self._pa_process_uuid + ".cfg",
                        RESULT : os.path.join(_TEST_DIR, self._pa_process_uuid),
                        CONFIG : os.path.join(_TEST_DIR, self._pa_process_uuid + ".cfg"),
                       }
        _DB_CONNECTOR.insert(PA_PROCESS_COLLECTION, [self._record])
        
    def tearDown(self):
        _DB_CONNECTOR.remove(PA_PROCESS_COLLECTION, 
                             {UUID: {"$in": [self._pa_process_uuid]}})
        
    def test_pa_result_exists(self):
        """
        This tests taht setUp properly inserts the primary analysis result in
        the database and that the result files exist.
        """
        response = _DB_CONNECTOR.find_one(PA_PROCESS_COLLECTION, UUID,
                                          self._pa_process_uuid)
        
        msg = "No entries in the DB with UUID = %s" % self._pa_process_uuid
        self.assertTrue(response, msg)
        
        msg = "Result file cannot be found: %s" % response[RESULT]
        self.assertTrue(os.path.isfile(response[RESULT]), msg)

        msg = "Config file cannot be found: %s" % response[CONFIG]
        self.assertTrue(os.path.isfile(response[CONFIG]), msg)
        
    def test_assay_caller(self):
        # Construct url
        url = _ASSAY_CALLER_URL
        url = self.add_url_argument(url, UUID, self._record[UUID], True) 
        url = self.add_url_argument(url, JOB_NAME, _ASSAY_CALLER_JOB_NAME) 
        url = self.add_url_argument(url, FIDUCIAL_DYE, _FIDUCIAL_DYE) 
        url = self.add_url_argument(url, ASSAY_DYE, _ASSAY_DYE) 
        url = self.add_url_argument(url, NUM_PROBES, _NUM_PROBES) 
        url = self.add_url_argument(url, TRAINING_FACTOR, _TRAINING_FACTOR) 
        url = self.add_url_argument(url, THRESHOLD, _THRESHOLD) 
        url = self.add_url_argument(url, OUTLIERS, _OUTLIERS) 
        url = self.add_url_argument(url, COV_TYPE, _COV_TYPE) 
         
        # Submit identity job
        response          = post_data(self, url, 200)
        assay_caller_uuid = response[ASSAY_CALLER][0][UUID]
          
        # Test that submitting two jobs with the same name fails and returns
        # the appropriate error code. 
        post_data(self, url, 403)
  
        running = True
        while running:
            time.sleep(10)
            response = get_data(self, _IDENTITY_URL, 200)
            for job in response[IDENTITY]:
                if assay_caller_uuid == job[UUID]:
                    job_details = job
                    running     = job_details[_STATUS] == 'running'
        print "DONE"

        # Copy result files to cwd for bamboo to ingest as artifacts
        assay_caller_txt_path = None
        if _RESULT in job_details:
            assay_caller_txt_path = job_details[_RESULT]
            if os.path.isfile(assay_caller_txt_path):
                shutil.copy(assay_caller_txt_path, "observed_assay_caller.txt")
               
        kde_plot_path = None  
        if KDE_PLOT in job_details:
            kde_plot_path = job_details[KDE_PLOT]
            if os.path.isfile(kde_plot_path):
                shutil.copy(kde_plot_path, "observed_kde_plot.png")
         
        scatter_plot_path = None  
        if SCATTER_PLOT in job_details:
            scatter_plot_path = job_details[KDE_PLOT]
            if os.path.isfile(scatter_plot_path):
                shutil.copy(scatter_plot_path, "observed_scatter_plot.png")
         
        error = ""
        if 'error' in job_details:
            error = job_details['error']
        msg = "Expected sa assay caller job status succeeded, but found %s. " \
              "Error: %s" % (job_details[_STATUS], error)
        self.assertEquals(job_details[_STATUS], "succeeded", msg)
         
#         exp_assay_caller_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), _EXPECTED_ANALYSIS_RESULT)
#         msg = "Observed result (%s) doesn't match expected result (%s)." % \
#               (assay_caller_txt_path, exp_assay_caller_path)
#         self.assertTrue(filecmp.cmp(exp_assay_caller_path, assay_caller_txt_path), msg)
 
        # Delete sa assay caller job
        delete_url = self.add_url_argument(_ASSAY_CALLER_URL, UUID, 
                                           assay_caller_uuid, True), 
        delete_data(self, delete_url, 200)
          
        # Ensure job no longer exists in the database
        response = get_data(self, _ASSAY_CALLER_URL, 200)
        for job in response[ASSAY_CALLER]:
            msg = "PA process job %s still exists in database." % assay_caller_uuid
            self.assertNotEqual(assay_caller_uuid, job[UUID], msg)



     
    @staticmethod
    def add_url_argument(url, key, value, first_argument=False):
        sep = "&"
        if first_argument:
            sep = "?"
        return url + "%s%s=%s" % (sep, key, value)
         
#     def test_identity(self):
#         # Construct url
#         url = self.construct_process_url()
#         
#         # Submit identity job
#         response      = post_data(self, url, 200)
#         identity_uuid = response[IDENTITY][0][UUID]
#         
#         # Test that submitting two jobs with the same name fails and returns
#         # the appropriate error code. 
#         post_data(self, url, 403)
# 
#         running = True
#         while running:
#             time.sleep(10)
#             response = get_data(self, _IDENTITY_URL, 200)
#             for job in response[IDENTITY]:
#                 if identity_uuid == job[UUID]:
#                     job_details = job
#                     running     = job_details[_STATUS] == 'running'
#         
#     def construct_identity_url(self):
#         url  = _IDENTITY_URL
#         url += "?uuid=%s" % self._record[UUID]
#         url += "&job_name=%s" % _IDENTITY_JOB_NAME
#         url += "&fiducial_dye=%s" % _FIDUCIAL_DYE
#         url += "&assay_dye=%s" % _ASSAY_DYE
#         url += "&num_probes=%s" % _NUM_PROBES
#         url += "&training_factor=%s" % _TRAINING_FACTOR
#         url += "&dye_levels=%s" % _DYE_LEVELS
#         return url
       
#     def test_get_identity(self):
#         response = get_data(self, _IDENTITY_URL + '?format=json', 200)
#         expected_response = {u'Identity': 
#                                 [{ u'job_name': u'test',
#                                    u'job_type': u'sa_identity',
#                                    u'uuid': u'90010cfe-e7f5-463b-bd02-90701de601f0',
#                                    u'pa_process_uuid': u'b7c980d0-6610-4265-b7a6-b64159cfee82',
#                                    u'fiducial_dye': u'joe',
#                                    u'assay_dye': u'fam',
#                                    u'num_probes': 0,
#                                    u'training_factor': 10,
#                                    u'dye_levels': [ [u'594', 2],
#                                                     [u'633', 2],
#                                                     [u'cy5.5', 2],
#                                                     [u'pe-cy7', 2]],
#                                    u'status': u'running',
#                                    u'start_datestamp': u'2015_02_18__11_38_16',
#                                    u'submit_datestamp': u'2015_02_18__11_38_14'}]}
#         msg = "Observed response doesn't match expected response.\n" + \
#             "Observed: %s\nExpected: %s" % (pformat(response), 
#                                             pformat(expected_response))
#         self.assertEquals(response, expected_response, msg)
        
#     def test_get_assay_caller(self):
#         response = get_data(self, _ASSAY_CALLER_URL + '?format=json', 200)
#         print "RESPONSE %s" % pformat(response)


#=============================================================================
# Main
#=============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()