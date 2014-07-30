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
@date:   Jul 23, 2014
'''

#=============================================================================
# Imports
#=============================================================================
from src.apis.AbstractApi import AbstractApiV1
from src.apis.primary_analysis.ArchivesGetFunction import ArchivesGetFunction
from src.apis.primary_analysis.DevicesGetFunction import DevicesGetFunction
from src.apis.primary_analysis.DyesGetFunction import DyesGetFunction
from src.apis.primary_analysis.ProcessPostFunction import ProcessPostFunction
from src.apis.primary_analysis.ProcessGetFunction import ProcessGetFunction
from src.apis.primary_analysis.ProcessDeleteFunction import ProcessDeleteFunction

#=============================================================================
# Class
#=============================================================================
class PrimaryAnalysisApiV1(AbstractApiV1):

    _FUNCTIONS = [
                  ArchivesGetFunction(),
                  DevicesGetFunction(),
                  DyesGetFunction(),
                  ProcessPostFunction(),
                  ProcessGetFunction(),
                  ProcessDeleteFunction(),
                 ]

    @staticmethod
    def name():
        return "PrimaryAnalysis"
   
    @staticmethod
    def description():
        return "Functions for running, examining, and deleting primary " \
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
    api = PrimaryAnalysisApiV1()
    print api