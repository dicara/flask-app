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

from bioweb_api.tests.test_utils import post_data, get_data, \
    delete_data, read_yaml
from bioweb_api.utilities import io_utilities
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
        
    def test_process(self):
        get_data(self, _ARCHIVES_URL + '?refresh=true&format=json', 200)

        # Test run details
        archive  = '20140715_b8_633pe_6'
        dyes     = ['633', 'pe']
        device   = "beta8"
        job_name = "test_pa_process_job"
        
        # Construct url
        url  = _PROCESS_URL
        url += "?archive=%s" % archive
        url += "&dyes=%s" % ",".join(dyes)
        url += "&device=%s" % device
        url += "&job_name=%s" % job_name
        
        # Submit process job
        response     = post_data(self, url, 200)
        process_uuid = response['uuid']
        
        running = True
        while running:
            time.sleep(10)
            response = get_data(self, _PROCESS_URL, 200)
            for job in response['Process']:
                if process_uuid == job['uuid']:
                    job_details = job
                    running     = job_details['status'] == 'running'
        
        error = ""
        if 'error' in job_details:
            error = job_details['error']
        msg = "Expected pa process job status succeeded, but found %s. " \
              "Error: %s" % (job_details['status'], error)
        self.assertEquals(job_details['status'], "succeeded", msg)
        
        exp_analysis_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), _EXPECTED_ANALYSIS_RESULT)
        msg = "Observed result (%s) doesn't match expected result (%s)." % \
              (job_details['result'], exp_analysis_path)
        self.assertTrue(filecmp.cmp(exp_analysis_path, job_details['result']), msg)

        exp_config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), _EXPECTED_ANALYSIS_RESULT)
        msg = "Observed result (%s) doesn't match expected result (%s)." % \
              (job_details['result'], exp_config_path)
        self.assertTrue(filecmp.cmp(exp_config_path, job_details['result']), msg)

        # Delete absorption job
        delete_data(self, _PROCESS_URL + "?uuid=%s" % process_uuid, 200)
         
        # Ensure job no longer exists in the database
        response = get_data(self, _PROCESS_URL, 200)
        for job in response['Process']:
            msg = "PA process job %s still exists in database." % process_uuid
            self.assertNotEqual(process_uuid, job['uuid'], msg)
