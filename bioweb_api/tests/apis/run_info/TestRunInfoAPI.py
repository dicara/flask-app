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

@author: Yuewei Sheng
@date:   Apr 19, 2016
'''

#=============================================================================
# Imports
#=============================================================================
import datetime
import os
import unittest

from bioweb_api import app, RUN_REPORT_COLLECTION
from bioweb_api.utilities import io_utilities
from bioweb_api.tests.test_utils import get_data
from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.run_info.constants import CARTRIDGE_SN, CHIP_SN, CHIP_REVISION, \
    DATETIME, DEVICE_NAME, EXIT_NOTES, EXP_DEF_NAME, REAGENT_INFO, RUN_ID, \
    RUN_DESCRIPTION, RUN_REPORT_PATH, USER, RUN_REPORT_TXTFILE, IMAGE_STACKS
from bioweb_api.apis.ApiConstants import UUID
from bioweb_api.apis.run_info.RunInfoUtils import read_report_file, \
        get_run_reports, update_run_reports

#===============================================================================
# Private Static Variables
#===============================================================================
_TEST_DIR                   = os.path.abspath(os.path.dirname(__file__))
_DB_CONNECTOR               = DbConnector.Instance()
_RUN_REPORT_TXTFILE         = 'run_info.txt'
_RUN_REPORT_YAMLFILE        = 'run_info.yaml'
_RUN_INFO_URL               = '/api/v1/RunInfo'
_RUN_INFO_GET_URL           = os.path.join(_RUN_INFO_URL, 'run_report')

#=============================================================================
# TestCase
#=============================================================================
class TestRunReportAPI(unittest.TestCase):
    def setUp(self):
        self._client = app.test_client(self)

    def test_read_txt(self):
        """
        test read_report_file, read a run_info.txt file and return a dictionary
        """
        datetime_obj = datetime.datetime.today()
        report_file = os.path.join(_TEST_DIR, _RUN_REPORT_TXTFILE)
        report_doc = read_report_file(report_file, datetime_obj, 'test')

        self.assertIn(CARTRIDGE_SN, report_doc)
        self.assertIn(RUN_DESCRIPTION, report_doc)
        self.assertIn(DEVICE_NAME, report_doc)
        self.assertEqual(report_doc[RUN_ID], 'id1459882049')
        self.assertEqual(report_doc[USER], ['thung', 'erahut'])
        self.assertEqual(report_doc[EXP_DEF_NAME], 'ABL_24_V1')

    def test_read_yaml(self):
        """
        test read_report_file, read a run_info.yaml file and return a dictionary
        """
        datetime_obj = datetime.datetime.today()
        report_file = os.path.join(_TEST_DIR, _RUN_REPORT_YAMLFILE)
        report_doc = read_report_file(report_file, datetime_obj, 'test')

        self.assertIn(CARTRIDGE_SN, report_doc)
        self.assertIn(CHIP_SN, report_doc)
        self.assertIn(DEVICE_NAME, report_doc)
        self.assertIn(EXP_DEF_NAME, report_doc)
        self.assertEqual(report_doc[CARTRIDGE_SN], 'S0029859')
        self.assertEqual(report_doc[REAGENT_INFO], 'abl24')
        self.assertEqual(report_doc[RUN_DESCRIPTION], 'software')

    def test_get_run_info(self):
        """
        test RunInfoGetFunction
        """
        response = get_data(self, _RUN_INFO_GET_URL + '?refresh=true&format=json', 200)
        len_expected_reports = len(_DB_CONNECTOR.find(RUN_REPORT_COLLECTION, {UUID: {'$exists': True},
                                                                              DEVICE_NAME: {'$ne': ''},
                                                                              EXP_DEF_NAME: {'$ne': None}}))
        len_observed_reports = len(response['run_report'])

        msg = "Numebr of observed run reports (%s) doesn't match expected number (%s)." \
                % (len_expected_reports, len_observed_reports)
        self.assertEqual(len_expected_reports, len_observed_reports, msg)

if __name__ == '__main__':
    unittest.main()
