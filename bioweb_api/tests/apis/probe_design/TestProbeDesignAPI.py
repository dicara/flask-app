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
@date:  Jun 23, 2014
'''

#===============================================================================
# Imports
#===============================================================================
import unittest
import os
import json
import filecmp
import time

from uuid import uuid4
from StringIO import StringIO

from bioweb_api.utilities import io_utilities
from bioweb_api import app, HOME_DIR, TARGETS_UPLOAD_PATH, PROBES_UPLOAD_PATH, \
    RESULTS_PATH, REFS_PATH, PLATES_UPLOAD_PATH

#===============================================================================
# Global Private Variables
#===============================================================================
_TARGETS_FILENAME         = "targets.fasta"
_PROBES_FILENAME          = "probes.fasta"
_INVALID_FASTA_FILENAME   = "invalid.fasta"
_EXPECTED_RESULT_FILENAME = "expected_results.txt"
_PROBE_DESIGN_URL         = "/api/v1/ProbeDesign"
_PROBES_URL               = os.path.join(_PROBE_DESIGN_URL, 'Probes')
_TARGETS_URL              = os.path.join(_PROBE_DESIGN_URL, 'Targets')
_ABSORPTION_URL           = os.path.join(_PROBE_DESIGN_URL, 'Absorption')

io_utilities.safe_make_dirs(HOME_DIR)
io_utilities.safe_make_dirs(TARGETS_UPLOAD_PATH)
io_utilities.safe_make_dirs(PROBES_UPLOAD_PATH)
io_utilities.safe_make_dirs(PLATES_UPLOAD_PATH)
io_utilities.safe_make_dirs(RESULTS_PATH)
io_utilities.safe_make_dirs(REFS_PATH)

#===============================================================================
# Test
#===============================================================================
class Test(unittest.TestCase):
    
    def setUp(self):
        self._client = app.test_client(self)

    def test_probes(self):
        self.file_upload_get_delete(_PROBES_URL, _PROBES_FILENAME)
        
    def test_targets(self):
        self.file_upload_get_delete(_TARGETS_URL, _TARGETS_FILENAME)
        
    def test_absorption(self):
        # Upload targets and probes files
        response     = self.upload_file(_PROBES_URL, _PROBES_FILENAME, 200)
        probes_uuid  = response['uuid']
        response     = self.upload_file(_TARGETS_URL, _TARGETS_FILENAME, 200)
        targets_uuid = response['uuid']
        
        # Post absorption job
        url = _ABSORPTION_URL + "?probes=%s&targets=%s&job_name=test_job" % \
             (probes_uuid, targets_uuid)
        response = self.post(url, 200)
        abs_job_uuid = response['uuid']
        
        running     = True
        job_details = None
        while running:
            time.sleep(10)
            response = self.get_data(_ABSORPTION_URL, 200)
            for job in response['Absorption']:
                if abs_job_uuid == job['uuid']:
                    job_details = job
                    running     = job_details['status'] == 'running'
                    
        # Clean up by removing targets and probes files
        self.delete_data(_PROBES_URL + "?uuid=%s" % probes_uuid, 200)
        self.delete_data(_TARGETS_URL + "?uuid=%s" % targets_uuid, 200)

        msg = "Expected absorption job status succeeded, but found: %s" % \
              job_details['status']
        self.assertEquals(job_details['status'], "succeeded", msg)
        
        exp_result_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), _EXPECTED_RESULT_FILENAME)
        msg = "Observed result (%s) doesn't match expected result (%s)." % \
              (job_details['result'], exp_result_path)
        self.assertTrue(filecmp.cmp(exp_result_path, job_details['result']), msg)

        # Delete absorption job
        self.delete_data(_ABSORPTION_URL + "?uuid=%s" % abs_job_uuid, 200)
        
        # Ensure job no longer exists in the database
        response = self.get_data(_ABSORPTION_URL, 200)
        for job in response['Absorption']:
            msg = "Absorption job %s still exists in database." % abs_job_uuid
            self.assertNotEqual(abs_job_uuid, job['uuid'], msg)

        
    #===========================================================================
    # Helper methods
    #===========================================================================
    def file_upload_get_delete(self, url, filename):
        response_key = url.split("/")[-1]
        
        # Test successful file upload
        response   = self.upload_file(url, filename, 200)
        uuid       = response['uuid']
        
        # Test error code 403: File already exists.
        self.upload_file(url, filename, 403)
        
        # Test error code 415: File is not a valid FASTA file.
        self.upload_file(url, _INVALID_FASTA_FILENAME, 415)
        
        # Test successful retrieval of uploaded file
        response       = self.get_data(url, 200) 
        retrieved_uuid = response[response_key][0]['uuid']
        msg = "Expected uuid (%s) doesn't match observed uuid (%s) for %s" % \
              (uuid, retrieved_uuid, url)
        self.assertEqual(uuid, retrieved_uuid, msg)
        
        # Test successful deletion of uploaded file
        self.delete_data(url + "?uuid=%s" % uuid, 200)
        
        # Test unsuccessful deletion of non-existent file
        self.delete_data(url + "?uuid=%s" % str(uuid4()), 404)
    
    def upload_file(self, url, filename, exp_resp_code):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
        with open(path) as f:
            response = self._client.post(
                                   url, 
                                   data={'file': (StringIO(f.read()), filename)}
                                  )
        self.assert_response_code(exp_resp_code, response, url)
        return json.loads(response.data)
    
    def post(self, url, exp_resp_code):
        response = self._client.post(url)
        self.assert_response_code(exp_resp_code, response, url)
        return json.loads(response.data)
    
    def get_data(self, url, exp_resp_code):
        response = self._client.get(url)
        self.assert_response_code(exp_resp_code, response, url)
        return json.loads(response.data)
    
    def delete_data(self, url, exp_resp_code):
        response = self._client.delete(url)
        self.assert_response_code(exp_resp_code, response, url)
        return json.loads(response.data)
        
    def assert_response_code(self, exp_resp_code, response, url):
        msg = "Expected response code (%s) doesn't match observed (%s) for " \
              "%s." % (exp_resp_code, response.status_code, url)
        self.assertEqual(response.status_code, exp_resp_code, msg)

#===============================================================================
# Main
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()