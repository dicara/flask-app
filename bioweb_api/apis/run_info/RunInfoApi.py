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
@date:   Apr 11, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractApi import AbstractApiV1
from bioweb_api.apis.run_info.RunInfoGetFunction import RunInfoGetFunction
from bioweb_api.apis.run_info.RunInfoFullAnalysisPostFunction import RunInfoFullAnalysisPostFunction

#=============================================================================
# Class
#=============================================================================
class RunInfoAPIV1(AbstractApiV1):

    _FUNCTIONS = [
                  RunInfoGetFunction(),
                  RunInfoFullAnalysisPostFunction(),
                 ]

    @staticmethod
    def name():
        return "RunInfo"

    @staticmethod
    def description():
        return "Browse available run reports and run full analysis pipeline."

    @staticmethod
    def preferred():
        return True

    @staticmethod
    def consumes():
        return ["multipart/form-data"]

    @property
    def functions(self):
        return self._FUNCTIONS

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    api = RunInfoAPIV1()
    print api
