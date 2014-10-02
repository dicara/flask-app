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

from uuid import uuid4

from bioweb_api.tests.test_utils import upload_file, post_data, get_data, \
    delete_data
from bioweb_api.utilities import io_utilities
from bioweb_api.apis.ApiConstants import UUID
from bioweb_api import app, HOME_DIR, TARGETS_UPLOAD_PATH, PROBES_UPLOAD_PATH, \
    RESULTS_PATH, REFS_PATH, PLATES_UPLOAD_PATH

#===============================================================================
# Global Private Variables
#===============================================================================
_TEST_DIR                 = os.path.abspath(os.path.dirname(__file__))
_TARGETS_FILENAME         = "targets.fasta"
_PROBES_FILENAME          = "probes.fasta"
_INVALID_FASTA_FILENAME   = "invalid.fasta"
_EXPECTED_RESULT_FILENAME = "expected_results.txt"
_PROBE_DESIGN_URL         = "/api/v1/ProbeDesign"
_ABSORPTION               = "Absorption"
_STATUS                   = "status"
_RESULT                   = "result"
_PROBES_URL               = os.path.join(_PROBE_DESIGN_URL, 'Probes')
_TARGETS_URL              = os.path.join(_PROBE_DESIGN_URL, 'Targets')
_ABSORPTION_URL           = os.path.join(_PROBE_DESIGN_URL, _ABSORPTION)

io_utilities.safe_make_dirs(HOME_DIR)
io_utilities.safe_make_dirs(TARGETS_UPLOAD_PATH)
io_utilities.safe_make_dirs(PROBES_UPLOAD_PATH)
io_utilities.safe_make_dirs(PLATES_UPLOAD_PATH)
io_utilities.safe_make_dirs(RESULTS_PATH)
io_utilities.safe_make_dirs(REFS_PATH)

#===============================================================================
# Test
#===============================================================================
class TestProbeDesignAPI(unittest.TestCase):
    
    def setUp(self):
        self._client = app.test_client(self)

    def test_probes(self):
        self.exercise_file_upload_api(_PROBES_URL, _PROBES_FILENAME)
        
    def test_targets(self):
        self.exercise_file_upload_api(_TARGETS_URL, _TARGETS_FILENAME)
        
    def test_absorption(self):
        # Upload targets and probes files
        response     = upload_file(self, _TEST_DIR, _PROBES_URL, 
                                   _PROBES_FILENAME, 200)
        probes_uuid  = response[UUID]
        response     = upload_file(self, _TEST_DIR, _TARGETS_URL, 
                                   _TARGETS_FILENAME, 200)
        targets_uuid = response[UUID]
        
        # Post absorption job
        url = _ABSORPTION_URL + "?probes=%s&targets=%s&job_name=test_job" % \
             (probes_uuid, targets_uuid)
        response = post_data(self, url, 200)
        abs_job_uuid = response[UUID]
        
        running     = True
        job_details = None
        while running:
            time.sleep(10)
            response = get_data(self, _ABSORPTION_URL, 200)
            for job in response[_ABSORPTION]:
                if abs_job_uuid == job[UUID]:
                    job_details = job
                    running     = job_details[_STATUS] == 'running'
                    
        # Copy result file to cwd for bamboo to ingest as an artifact
        if _RESULT in job_details:
            absorption_path = job_details[_RESULT]
            if os.path.isfile(absorption_path):
                shutil.copy(absorption_path, "observed_absorption.txt")
            
        # Clean up by removing targets and probes files
        delete_data(self, _PROBES_URL + "?uuid=%s" % probes_uuid, 200)
        delete_data(self, _TARGETS_URL + "?uuid=%s" % targets_uuid, 200)

        msg = "Expected absorption job status succeeded, but found: %s" % \
              job_details[_STATUS]
        self.assertEquals(job_details[_STATUS], "succeeded", msg)
        
        exp_result_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), _EXPECTED_RESULT_FILENAME)
        msg = "Observed result (%s) doesn't match expected result (%s)." % \
              (job_details[_RESULT], exp_result_path)
        self.assertTrue(filecmp.cmp(exp_result_path, job_details[_RESULT]), msg)

        # Delete absorption job
        delete_data(self, _ABSORPTION_URL + "?uuid=%s" % abs_job_uuid, 200)
        
        # Ensure job no longer exists in the database
        response = get_data(self, _ABSORPTION_URL, 200)
        for job in response[_ABSORPTION]:
            msg = "Absorption job %s still exists in database." % abs_job_uuid
            self.assertNotEqual(abs_job_uuid, job[UUID], msg)

        
    #===========================================================================
    # Helper methods
    #===========================================================================
    def exercise_file_upload_api(self, url, filename):
        response_key = url.split("/")[-1]
        
        # Test successful file upload
        response   = upload_file(self, _TEST_DIR, url, filename, 200)
        uuid       = response[UUID]
        
        # Test error code 403: File already exists.
        upload_file(self, _TEST_DIR, url, filename, 403)
        
        # Test error code 415: File is not a valid FASTA file.
        upload_file(self, _TEST_DIR, url, _INVALID_FASTA_FILENAME, 415)
        
        # Test successful retrieval of uploaded file
        response       = get_data(self, url, 200) 
        retrieved_uuid = response[response_key][0][UUID]
        msg = "Expected uuid (%s) doesn't match observed uuid (%s) for %s" % \
              (uuid, retrieved_uuid, url)
        self.assertEqual(uuid, retrieved_uuid, msg)
        
        # Test successful deletion of uploaded file
        delete_data(self, url + "?uuid=%s" % uuid, 200)
        
        # Test unsuccessful deletion of non-existent file
        delete_data(self, url + "?uuid=%s" % str(uuid4()), 404)
    
#===============================================================================
# Main
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()