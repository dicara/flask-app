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
@date:   August 22, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractApi import AbstractApiV1
from bioweb_api.apis.exp_def.ExpDefGetFunction import ExpDefGetFunction
from bioweb_api.apis.exp_def.ExpDefPostFunction import ExpDefPostFunction

#=============================================================================
# Class
#=============================================================================
class ExpDefApiV1(AbstractApiV1):

    _FUNCTIONS = [
                  ExpDefGetFunction(),
                  ExpDefPostFunction(),
                 ]

    @staticmethod
    def name():
        return "ExpDef"

    @staticmethod
    def description():
        return "API for Experiment Definitions."

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
    api = ExpDefApiV1()
    print api
