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
@date:   Feb 3, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractApi import AbstractApiV1
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import IdentityPostFunction
from bioweb_api.apis.secondary_analysis.IdentityGetFunction import IdentityGetFunction
from bioweb_api.apis.secondary_analysis.IdentityDeleteFunction import IdentityDeleteFunction
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import AssayCallerPostFunction
from bioweb_api.apis.secondary_analysis.AssayCallerGetFunction import AssayCallerGetFunction
from bioweb_api.apis.secondary_analysis.AssayCallerDeleteFunction import AssayCallerDeleteFunction
from bioweb_api.apis.secondary_analysis.AssayCallerSubmodelGetFunction import AssayCallerSubmodelGetFunction
from bioweb_api.apis.secondary_analysis.GenotyperPostFunction import GenotyperPostFunction
from bioweb_api.apis.secondary_analysis.GenotyperGetFunction import GenotyperGetFunction
from bioweb_api.apis.secondary_analysis.GenotyperDeleteFunction import GenotyperDeleteFunction
from bioweb_api.apis.secondary_analysis.ExploratoryGetFunction import ExploratoryGetFunction
from bioweb_api.apis.secondary_analysis.ExploratoryPostFunction import ExploratoryPostFunction

#=============================================================================
# Class
#=============================================================================
class SecondaryAnalysisAPIV1(AbstractApiV1):

    _FUNCTIONS = [
                  IdentityPostFunction(),
                  IdentityGetFunction(),
                  IdentityDeleteFunction(),
                  AssayCallerPostFunction(),
                  AssayCallerGetFunction(),
                  AssayCallerDeleteFunction(),
                  AssayCallerSubmodelGetFunction(),
                  GenotyperPostFunction(),
                  GenotyperGetFunction(),
                  GenotyperDeleteFunction(),
                  ExploratoryGetFunction(),
                  ExploratoryPostFunction(),
                 ]

    @staticmethod
    def name():
        return "SecondaryAnalysis"

    @staticmethod
    def description():
        return "Functions for running, examining, and deleting secondary " \
               "analysis jobs."

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
    api = SecondaryAnalysisAPIV1()
    print api