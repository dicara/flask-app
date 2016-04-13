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

@author: Nathan Brown
@date:   March 28, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractApi import AbstractApiV1
from bioweb_api.apis.full_analysis.FullAnalysisPostFunction import FullAnalysisPostFunction
from bioweb_api.apis.full_analysis.FullAnalysisGetFunction import FullAnalysisGetFunction
from bioweb_api.apis.full_analysis.FullAnalysisDeleteFunction import FullAnalysisDeleteFunction


#=============================================================================
# Class
#=============================================================================
class FullAnalysisApiV1(AbstractApiV1):

    _FUNCTIONS = [
                  FullAnalysisPostFunction(),
                  FullAnalysisGetFunction(),
                  FullAnalysisDeleteFunction(),
                 ]

    @staticmethod
    def name():
        return "FullAnalysis"
   
    @staticmethod
    def description():
        return "Functions for running a full analysis of an image stack"
    
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
    api = FullAnalysisApiV1()
    print api