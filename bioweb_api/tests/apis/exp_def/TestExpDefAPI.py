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
@date:   August 23, 2016
'''

#=============================================================================
# Imports
#=============================================================================
import os
import unittest

from bioweb_api import app, EXP_DEF_COLLECTION, HOSTNAME, PORT
from bioweb_api.DbConnector import DbConnector
from bioweb_api.tests.test_utils import post_data, get_data, \
    add_url_argument
# from bioweb_api.apis.ApiConstants import *

from bioweb_api.apis.exp_def.ExpDefGetFunction import ExpDefGetFunction
from bioweb_api.apis.exp_def.ExpDefPostFunction import ExpDefPostFunction

#=============================================================================
# Setup Logging
#=============================================================================
import tornado.options
tornado.options.parse_command_line()

#===============================================================================
# Private Static Variables
#===============================================================================
_EXP_DEF_URL              = "/api/v1/ExpDef"
_TEST_DIR                 = os.path.abspath(os.path.dirname(__file__))
_DB_CONNECTOR             = DbConnector.Instance()

#=============================================================================
# TestCase
#=============================================================================
class TestExpDefAPI(unittest.TestCase):
    def setUp(self):
        self._client = app.test_client(self)

    def test_post_exp_defs(self):
        """
        test ExpDefPostFunction
        """
        response = post_data(self, _EXP_DEF_URL + '/refresh', 200)

        msg = "Failed to update EXP_DEF_COLLECTION."
        self.assertIn("Number of Inserts/Updates", response, msg)

    def test_get_exp_defs(self):
        """
        test ExpDefGetFunction
        """
        response = get_data(self, _EXP_DEF_URL + '/ExpDef', 200)
        len_expected_defs = len(_DB_CONNECTOR.find(EXP_DEF_COLLECTION, {}))
        len_observed_defs = len(response['ExpDef'])

        msg = "Numebr of observed definitions (%s) doesn't match expected number (%s)." \
                % (len_observed_defs, len_expected_defs)
        self.assertEqual(len_expected_defs, len_observed_defs, msg)


if __name__ == '__main__':
    unittest.main()
