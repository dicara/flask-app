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
@date:  Sep 30, 2014
'''

#===============================================================================
# Imports
#===============================================================================
import unittest
import os
import filecmp
import time
import shutil

from bioweb_api.tests.test_utils import post_data, get_data, \
    delete_data, read_yaml
from bioweb_api.utilities import io_utilities
from bioweb_api.apis.ApiConstants import UUID
from bioweb_api import app, HOME_DIR, TARGETS_UPLOAD_PATH, PROBES_UPLOAD_PATH, \
    RESULTS_PATH, REFS_PATH, PLATES_UPLOAD_PATH, TMP_PATH

#===============================================================================
# Global Private Variables
#===============================================================================
_TEST_DIR                 = os.path.abspath(os.path.dirname(__file__))
_EXPECTED_ANALYSIS_RESULT = "expected_analysis.txt"
_EXPECTED_CONFIG_RESULT   = "expected.cfg"
_PRIMARY_ANALYSIS_URL     = "/api/v1/PrimaryAnalysis"
_ARCHIVES_URL             = os.path.join(_PRIMARY_ANALYSIS_URL, 'Archives')
_DEVICES_URL              = os.path.join(_PRIMARY_ANALYSIS_URL, 'Devices')
_DYES_URL                 = os.path.join(_PRIMARY_ANALYSIS_URL, 'Dyes')
_PROCESS_URL              = os.path.join(_PRIMARY_ANALYSIS_URL, 'Process')
_RESULT                   = "result"
_CONFIG                   = "config"
_STATUS                   = "status"
_PROCESS                  = "Process"
_DYES                     = ['633', 'pe']
_DEVICE                   = "beta8"
_JOB_NAME                 = "test_pa_process_job"

io_utilities.safe_make_dirs(HOME_DIR)
io_utilities.safe_make_dirs(TARGETS_UPLOAD_PATH)
io_utilities.safe_make_dirs(PROBES_UPLOAD_PATH)
io_utilities.safe_make_dirs(PLATES_UPLOAD_PATH)
io_utilities.safe_make_dirs(RESULTS_PATH)
io_utilities.safe_make_dirs(REFS_PATH)
io_utilities.safe_make_dirs(TMP_PATH)

#===============================================================================
# Test
#===============================================================================
class TestPrimaryAnalysisAPI(unittest.TestCase):
    
    def setUp(self):
        self._client = app.test_client(self)
        
    def test_dyes(self):
        response = get_data(self, _DYES_URL + '?refresh=true&format=json', 200)
        dyes     = read_yaml(os.path.join(_TEST_DIR, 'dyes.yaml'))
        observed_dyes = ", ".join(map(lambda x: x['dye'], response['Dyes']))
        expected_dyes = ", ".join(map(lambda x: x['dye'], dyes['Dyes']))
        msg = "Observed dyes (%s) don't match expected (%s)." % \
              (observed_dyes, expected_dyes)
        self.assertEqual(response, dyes, msg)
    
    def test_devices(self):
        response = get_data(self, _DEVICES_URL + '?refresh=true&format=json', 200)
        devices  = read_yaml(os.path.join(_TEST_DIR, 'devices.yaml'))
        observed_devices = ", ".join(map(lambda x: x['device'], response['Devices']))
        expected_devices = ", ".join(map(lambda x: x['device'], devices['Devices']))
        msg = "Observed devices (%s) don't match expected (%s)." % \
              (observed_devices, expected_devices)
        self.assertEqual(response, devices, msg)
        
    def test_archives(self):
        get_data(self, _ARCHIVES_URL + '?refresh=true&format=json', 200)
        
    def test_process_no_archive(self):
        archive = "nonexistent_archive"
        url = self.construct_process_url(archive)
        post_data(self, url, 500)
        
    def test_process_no_images_in_archive(self):
        archive = "tmp"
        url = self.construct_process_url(archive)
        post_data(self, url, 404)
        
    def test_process(self):
        get_data(self, _ARCHIVES_URL + '?refresh=true&format=json', 200)
 
        # Test run details
        archive  = '20140715_b8_633pe_6'
         
        # Construct url
        url = self.construct_process_url(archive)
         
        # Submit process job
        response     = post_data(self, url, 200)
        process_uuid = response[_PROCESS][0][UUID]
        
        # Test that submitting two jobs with the same name fails and returns
        # the appropriate error code. 
        post_data(self, url, 403)

        running = True
        while running:
            time.sleep(10)
            response = get_data(self, _PROCESS_URL, 200)
            for job in response[_PROCESS]:
                if process_uuid == job[UUID]:
                    job_details = job
                    running     = job_details[_STATUS] == 'running'
         
        # Copy result files to cwd for bamboo to ingest as artifacts
        analysis_txt_path = None
        if _RESULT in job_details:
            analysis_txt_path = job_details[_RESULT]
            if os.path.isfile(analysis_txt_path):
                shutil.copy(analysis_txt_path, "observed_analysis.txt")
               
        config_path = None  
        if _CONFIG in job_details:
            config_path = job_details[_CONFIG]
            if os.path.isfile(config_path):
                shutil.copy(config_path, "observed.cfg")
         
        error = ""
        if 'error' in job_details:
            error = job_details['error']
        msg = "Expected pa process job status succeeded, but found %s. " \
              "Error: %s" % (job_details[_STATUS], error)
        self.assertEquals(job_details[_STATUS], "succeeded", msg)
         
        exp_analysis_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), _EXPECTED_ANALYSIS_RESULT)
        msg = "Observed result (%s) doesn't match expected result (%s)." % \
              (analysis_txt_path, exp_analysis_path)
        self.assertTrue(filecmp.cmp(exp_analysis_path, analysis_txt_path), msg)
 
        exp_config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), _EXPECTED_CONFIG_RESULT)
        msg = "Observed result (%s) doesn't match expected result (%s)." % \
              (config_path, exp_config_path)
        self.assertTrue(filecmp.cmp(exp_config_path, config_path), msg)
 
        # Delete absorption job
        delete_data(self, _PROCESS_URL + "?uuid=%s" % process_uuid, 200)
          
        # Ensure job no longer exists in the database
        response = get_data(self, _PROCESS_URL, 200)
        for job in response['Process']:
            msg = "PA process job %s still exists in database." % process_uuid
            self.assertNotEqual(process_uuid, job[UUID], msg)
             
    @staticmethod
    def construct_process_url(archive):
        url  = _PROCESS_URL
        url += "?archive=%s" % archive
        url += "&dyes=%s" % ",".join(_DYES)
        url += "&device=%s" % _DEVICE
        url += "&job_name=%s" % _JOB_NAME
        return url