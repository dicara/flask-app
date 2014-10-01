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
import yaml
import json
import filecmp
import time

from uuid import uuid4
from StringIO import StringIO
from primary_analysis.dye_datastore import Datastore

from bioweb_api.tests.test_utils import upload_file, post_data, get_data, \
    delete_data, read_yaml, write_yaml
from bioweb_api.utilities import io_utilities
from bioweb_api import app, HOME_DIR, TARGETS_UPLOAD_PATH, PROBES_UPLOAD_PATH, \
    RESULTS_PATH, REFS_PATH, PLATES_UPLOAD_PATH
from bioweb_api.apis.ApiConstants import ARCHIVE

#===============================================================================
# Global Private Variables
#===============================================================================
_PRIMARY_ANALYSIS_URL = "/api/v1/PrimaryAnalysis"
_ARCHIVES_URL         = os.path.join(_PRIMARY_ANALYSIS_URL, 'Archives')
_DEVICES_URL          = os.path.join(_PRIMARY_ANALYSIS_URL, 'Devices')
_DYES_URL             = os.path.join(_PRIMARY_ANALYSIS_URL, 'Dyes')
_PROCESS_URL          = os.path.join(_PRIMARY_ANALYSIS_URL, 'Process')

io_utilities.safe_make_dirs(HOME_DIR)
io_utilities.safe_make_dirs(TARGETS_UPLOAD_PATH)
io_utilities.safe_make_dirs(PROBES_UPLOAD_PATH)
io_utilities.safe_make_dirs(PLATES_UPLOAD_PATH)
io_utilities.safe_make_dirs(RESULTS_PATH)
io_utilities.safe_make_dirs(REFS_PATH)

#===============================================================================
# Test
#===============================================================================
class TestPrimaryAnalysisAPI(unittest.TestCase):
    
    def setUp(self):
        self._client = app.test_client(self)
        
    def test_dyes(self):
        response = get_data(self, _DYES_URL + '?refresh=true&format=json', 200)
        dyes     = read_yaml('dyes.yaml')
        observed_dyes = ", ".join(map(lambda x: x['dye'], response['Dyes']))
        expected_dyes = ", ".join(map(lambda x: x['dye'], dyes['Dyes']))
        msg = "Observed dyes (%s) don't match expected (%s)." % \
              (observed_dyes, expected_dyes)
        self.assertEqual(response, dyes, msg)
    
    def test_devices(self):
        response = get_data(self, _DEVICES_URL + '?refresh=true&format=json', 200)
        devices  = read_yaml('devices.yaml')
        observed_devices = ", ".join(map(lambda x: x['device'], response['Devices']))
        expected_devices = ", ".join(map(lambda x: x['device'], devices['Devices']))
        msg = "Observed devices (%s) don't match expected (%s)." % \
              (observed_devices, expected_devices)
        self.assertEqual(response, devices, msg)
        
    def test_archives(self):
        get_data(self, _ARCHIVES_URL, 200)
        
    def test_process(self):
        archive = '2014-09-11_3pm_Beta7'
        dyes = ['pe-cy7', 'percp', 'percp-cy7']
        url = _PROCESS_URL
        url += "?archive=%s" % archive
        url += "&dyes=%s" % "%2C".join(dyes)
        url = _PROCESS_URL + '?archive=2014-09-11_3pm_Beta7&dyes=pe-cy7%2Cpercp%2Cpercp-cy7&device=beta7&job_name=asdfsd'

        pass
    
       
