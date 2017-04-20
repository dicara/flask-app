'''
Copyright 2017 Bio-Rad Laboratories, Inc.

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
@date:   April 20, 2017
'''

#=============================================================================
# Imports
#=============================================================================
import os

import requests

from bioweb_api import HOSTNAME, PORT
from bioweb_api.apis.run_info.RunInfoGetFunction import RUN_REPORT
from bioweb_api.utilities.logging_utilities import APP_LOGGER

#=============================================================================
# Private Static Variables
#=============================================================================
_RUN_INFO_URL               = '/api/v1/RunInfo'
_RUN_INFO_GET_URL           = os.path.join(_RUN_INFO_URL, RUN_REPORT)

#=============================================================================
# Function
#=============================================================================
def update_reports():
    resp = requests.get('http://{0}:{1}{2}?refresh=true'.format(
                                                HOSTNAME,
                                                PORT,
                                                _RUN_INFO_GET_URL))
    APP_LOGGER.info("Updated run reports with status %s" % resp.status_code)
    return resp


if __name__ == '__main__':
    update_reports()
