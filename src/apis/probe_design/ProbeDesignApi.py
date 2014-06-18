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
@date:   Jun 1, 2014
'''

#=============================================================================
# Imports
#=============================================================================
from src.apis.AbstractApi import AbstractApiV1
from src.apis.probe_design.ValidationFunction import ValidationFunction
from src.apis.probe_design.TargetsPostFunction import TargetsPostFunction
from src.apis.probe_design.TargetsGetFunction import TargetsGetFunction
from src.apis.probe_design.TargetsDeleteFunction import TargetsDeleteFunction
from src.apis.probe_design.ProbesPostFunction import ProbesPostFunction
from src.apis.probe_design.ProbesGetFunction import ProbesGetFunction
from src.apis.probe_design.ProbesDeleteFunction import ProbesDeleteFunction

#=============================================================================
# Class
#=============================================================================
class ProbeDesignApiV1(AbstractApiV1):

    _FUNCTIONS = [
                  ValidationFunction(),
                  TargetsPostFunction(),
                  TargetsGetFunction(),
                  TargetsDeleteFunction(),
                  ProbesPostFunction(),
                  ProbesGetFunction(),
                  ProbesDeleteFunction,
                 ]

    @staticmethod
    def name():
        return "ProbeDesign"
   
    @staticmethod
    def description():
        return "Functions for designing probes."
    
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
    api = ProbeDesignApiV1()
    print api