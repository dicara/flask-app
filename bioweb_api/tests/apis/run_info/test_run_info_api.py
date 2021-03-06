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
from uuid import uuid4

from bioweb_api import app, RUN_REPORT_COLLECTION
from bioweb_api.tests.test_utils import get_data, post_data, delete_data, \
    add_url_argument
from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.run_info.constants import CARTRIDGE_SN, CHIP_SN, \
    DEVICE_NAME, EXP_DEF_NAME, RUN_ID, RUN_DESCRIPTION, USER, IMAGE_STACKS, \
    CARTRIDGE_BC, KIT_BC, MCP_MODE, SAMPLE_NAME, SAMPLE_TYPE, SYRINGE_BC, \
    APP_TYPE, INTERNAL_PART_NUM, LOT_NUM, MANUFACTURE_DATE, MASTER_LOT, \
    CUSTOMER_APP_NAME
from bioweb_api.apis.ApiConstants import UUID, TAGS
from bioweb_api.apis.run_info.RunInfoUtils import read_report_file

#===============================================================================
# Private Static Variables
#===============================================================================
_TEST_DIR                   = os.path.abspath(os.path.dirname(__file__))
_DB_CONNECTOR               = DbConnector.Instance()
_RUN_REPORT_TXTFILE         = 'run_info.txt'
_RUN_REPORT_YAMLFILE        = 'run_info.yaml'
_RUN_REPORT_CLIENTUI        = 'run_info_clientUI.yaml'
_RUN_INFO_URL               = '/api/v1/RunInfo'
_RUN_INFO_GET_URL           = os.path.join(_RUN_INFO_URL, 'run_report')
_RUN_INFO_TAG_URL           = os.path.join(_RUN_INFO_URL, 'tags')
_START_DATE                 = datetime.datetime(2017, 1, 1)
_END_DATE                   = datetime.datetime(2017, 1, 10)

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
        self.assertEqual(report_doc[CARTRIDGE_SN], '36464')
        self.assertEqual(report_doc[DEVICE_NAME], 'pilot6')
        self.assertEqual(report_doc[RUN_DESCRIPTION], 'fragmented gdna')

    def test_read_yaml_clientui(self):
        """
        test reading a yaml file generated from Client UI
        """
        datetime_obj = datetime.datetime.today()
        report_file = os.path.join(_TEST_DIR, _RUN_REPORT_CLIENTUI)
        report_doc = read_report_file(report_file, datetime_obj, 'test')

        self.assertIn(CARTRIDGE_BC, report_doc)
        self.assertIn(KIT_BC, report_doc)
        self.assertIn(SYRINGE_BC, report_doc)
        self.assertIn(MCP_MODE, report_doc)
        self.assertIn(SAMPLE_NAME, report_doc)
        self.assertIn(SAMPLE_TYPE, report_doc)
        self.assertEqual(report_doc[CARTRIDGE_BC][APP_TYPE], '1-xxx')
        self.assertEqual(report_doc[CARTRIDGE_BC][LOT_NUM], '20MAY2016')
        self.assertEqual(report_doc[KIT_BC][CUSTOMER_APP_NAME], 'Beta kit 2016 May')
        self.assertEqual(report_doc[KIT_BC][MANUFACTURE_DATE], '20160609')
        self.assertEqual(report_doc[SYRINGE_BC][INTERNAL_PART_NUM], 'P0000000r0')
        self.assertEqual(report_doc[SYRINGE_BC][MASTER_LOT], 'S0032128')

    def test_get_run_info(self):
        """
        test RunInfoGetFunction
        """
        response = get_data(self, _RUN_INFO_GET_URL + '?refresh=true&format=json', 200)
        len_expected_reports = len(_DB_CONNECTOR.find(RUN_REPORT_COLLECTION, {UUID: {'$exists': True},
                                                                              DEVICE_NAME: {'$ne': ''},
                                                                              EXP_DEF_NAME: {'$ne': None},
                                                                              IMAGE_STACKS: {'$ne': None,
                                                                                             '$not': {'$size': 0}}}))
        len_observed_reports = len(response['run_report'])

        msg = "Numebr of observed run reports (%s) doesn't match expected number (%s)." \
                % (len_observed_reports, len_expected_reports)
        self.assertEqual(len_expected_reports, len_observed_reports, msg)

    def test_update_report_by_dates(self):
        """
        test RunInfoGetFunction with start and end parameters
        """
        # test when both start and end dates are specified
        param_str = '?refresh=true&start={0}&end={1}'.format(
                                            _START_DATE.strftime("%Y_%m_%d"),
                                            _END_DATE.strftime("%Y_%m_%d"))
        response = get_data(self, _RUN_INFO_GET_URL + param_str, 200)
        len_expected_reports = len(_DB_CONNECTOR.find(RUN_REPORT_COLLECTION,
                                            {UUID: {'$exists': True},
                                             DEVICE_NAME: {'$ne': ''},
                                             EXP_DEF_NAME: {'$ne': None},
                                             IMAGE_STACKS: {'$ne': None,
                                                            '$not': {'$size': 0}}}))
        len_observed_reports = len(response['run_report'])
        msg = "Numebr of observed run reports (%s) doesn't match expected number (%s)." \
                % (len_observed_reports, len_expected_reports)
        self.assertEqual(len_expected_reports, len_observed_reports, msg)

        # test when only start date is specified
        param_str = '?refresh=true&start={0}'.format(_START_DATE.strftime("%Y_%m_%d"))
        response = get_data(self, _RUN_INFO_GET_URL + param_str, 200)
        len_expected_reports = len(_DB_CONNECTOR.find(RUN_REPORT_COLLECTION,
                                            {UUID: {'$exists': True},
                                             DEVICE_NAME: {'$ne': ''},
                                             EXP_DEF_NAME: {'$ne': None},
                                             IMAGE_STACKS: {'$ne': None,
                                                            '$not': {'$size': 0}}}))
        len_observed_reports = len(response['run_report'])
        msg = "Numebr of observed run reports (%s) doesn't match expected number (%s)." \
                % (len_observed_reports, len_expected_reports)
        self.assertEqual(len_expected_reports, len_observed_reports, msg)

    def test_tags_api(self):
        """
        test TagsGetFunction, TagsDeleteFunction, and TagsPostFunction.
        """
        report_uuid = str(uuid4())
        _DB_CONNECTOR.insert(RUN_REPORT_COLLECTION,
                             [{UUID: report_uuid, 'name': 'dummy run report'}])

        # test TagsPostFunction, add tags to a run report
        post_url = _RUN_INFO_TAG_URL
        post_url = add_url_argument(post_url, UUID, report_uuid, True)
        post_url = add_url_argument(post_url, TAGS, ','.join(["BRAF e15", "FFPE"]))

        response = post_data(self, post_url, 200)

        # test TagsGetFunction, get tags from all run reports
        response = get_data(self, _RUN_INFO_TAG_URL, 200)
        self.assertIn("braf e15", response[TAGS])

        # test TagsDeleteFunction, delete a tag from a run report
        delete_url = _RUN_INFO_TAG_URL
        delete_url = add_url_argument(delete_url, UUID, report_uuid, True)
        delete_url = add_url_argument(delete_url, TAGS, "ffpe")

        delete_data(self, delete_url, 200)
        response = get_data(self, _RUN_INFO_TAG_URL, 200)
        self.assertIn("braf e15", response[TAGS])
        self.assertNotIn("ffpe", response[TAGS])

        _DB_CONNECTOR.remove(RUN_REPORT_COLLECTION, {UUID: report_uuid})


if __name__ == '__main__':
    unittest.main()
