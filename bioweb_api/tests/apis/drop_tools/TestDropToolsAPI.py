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
@date:   Mar 4, 2015
'''

#=============================================================================
# Imports
#=============================================================================
import os
import unittest

from bioweb_api import app
from bioweb_api.apis.drop_tools.DropSizePostFunction import DROP_SIZE
from bioweb_api.tests.test_utils import get_data, delete_data, \
    add_url_argument, upload_file, post_data
from bioweb_api.apis.ApiConstants import DROP_AVE_DIAMETER, DROP_STD_DIAMETER, DYE_METRICS


#=============================================================================
# Private Static Variables
#=============================================================================
_DROP_SIZE_URL     = os.path.join("/api/v1/DropTools", DROP_SIZE)

#=============================================================================
# Class
#=============================================================================
class TestDropToolsApi(unittest.TestCase):

    def setUp(self):
        self._client = app.test_client(self)

    def test_valid_params(self):
        # Try a simple post request
        drop_size_url = _DROP_SIZE_URL
        drop_size_url = add_url_argument(drop_size_url, DROP_AVE_DIAMETER, 28, True)
        drop_size_url = add_url_argument(drop_size_url, DROP_STD_DIAMETER, 0.5)
        drop_size_url = add_url_argument(drop_size_url, DYE_METRICS, "594:4:0:20000,633:3:0:30000")
        post_data(self, drop_size_url, 200)

    def test_invalid_dye_metrics(self):
        # Try post request with improperly formatted dye metrics
        drop_size_url = _DROP_SIZE_URL
        drop_size_url = add_url_argument(drop_size_url, DROP_AVE_DIAMETER, 28, True)
        drop_size_url = add_url_argument(drop_size_url, DROP_STD_DIAMETER, 0.5)
        drop_size_url = add_url_argument(drop_size_url, DYE_METRICS, "594:4:20000,633:3:0:30000")
        post_data(self, drop_size_url, 500)



#=============================================================================
# Main
#=============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()