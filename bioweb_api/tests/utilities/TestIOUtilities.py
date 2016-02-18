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
@date:   Oct 3, 2014
'''

#=============================================================================
# Imports
#=============================================================================
import unittest

from datetime import datetime
from copy import deepcopy

from bioweb_api.utilities.io_utilities import clean_item, TIME_FORMAT

#=============================================================================
# Setup Logging
#=============================================================================
import tornado.options
tornado.options.parse_command_line()

#=============================================================================
# Class
#=============================================================================
class TestIOUtilities(unittest.TestCase):
    def test_clean_item(self):
        item = {
                "Numbers": [float('NaN'), 1, 2.0],
                "Datetime": datetime.today(),
                "NestedDict": {
                                "a": [1,2,3,float('NaN')],
                                "b": datetime.today(),
                              },
                "NestedList": [
                                float('NaN'),
                                datetime.today(),
                                "a",
                                1,
                                3.0,
                                None,
                               ]
               }  
        exp_clean_item = deepcopy(item)
        exp_clean_item["Numbers"][0] = None
        exp_clean_item["Datetime"]   = exp_clean_item["Datetime"].strftime(TIME_FORMAT)
        exp_clean_item["NestedDict"]["a"][3] = None
        exp_clean_item["NestedDict"]["b"] = exp_clean_item["NestedDict"]["b"].strftime(TIME_FORMAT)
        exp_clean_item["NestedList"][0] = None
        exp_clean_item["NestedList"][1] = exp_clean_item["NestedList"][1].strftime(TIME_FORMAT)
        obs_clean_item = clean_item(item)
        msg = "Expected clean item (%s) doesn't match observed (%s)."  % \
            (exp_clean_item, obs_clean_item)
        self.assertEqual(obs_clean_item, exp_clean_item, msg)
        
#=============================================================================
# Main
#=============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_clean_item']
    unittest.main()