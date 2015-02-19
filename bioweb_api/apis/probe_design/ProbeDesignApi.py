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
from bioweb_api.apis.AbstractApi import AbstractApiV1
# from bioweb_api.apis.probe_design.ValidationPostFunction import ValidationPostFunction
# from bioweb_api.apis.probe_design.ValidationGetFunction import ValidationGetFunction
# from bioweb_api.apis.probe_design.ExperimentPostFunction import ExperimentPostFunction
# from bioweb_api.apis.probe_design.ExperimentGetFunction import ExperimentGetFunction
from bioweb_api.apis.probe_design.ProbeExperimentMetadataPostFunction import ProbeExperimentMetadataPostFunction
from bioweb_api.apis.probe_design.ProbeExperimentMetadataGetFunction import ProbeExperimentMetadataGetFunction
from bioweb_api.apis.probe_design.ProbeExperimentMetadataDeleteFunction import ProbeExperimentMetadataDeleteFunction
from bioweb_api.apis.probe_design.ProbeExperimentPostFunction import ProbeExperimentPostFunction
from bioweb_api.apis.probe_design.ProbeExperimentGetFunction import ProbeExperimentGetFunction
from bioweb_api.apis.probe_design.ProbeExperimentDeleteFunction import ProbeExperimentDeleteFunction
from bioweb_api.apis.probe_design.AbsorptionPostFunction import AbsorptionPostFunction
from bioweb_api.apis.probe_design.AbsorptionGetFunction import AbsorptionGetFunction
from bioweb_api.apis.probe_design.AbsorptionDeleteFunction import AbsorptionDeleteFunction
from bioweb_api.apis.probe_design.TargetsPostFunction import TargetsPostFunction
from bioweb_api.apis.probe_design.TargetsGetFunction import TargetsGetFunction
from bioweb_api.apis.probe_design.TargetsDeleteFunction import TargetsDeleteFunction
from bioweb_api.apis.probe_design.ProbesPostFunction import ProbesPostFunction
from bioweb_api.apis.probe_design.ProbesGetFunction import ProbesGetFunction
from bioweb_api.apis.probe_design.ProbesDeleteFunction import ProbesDeleteFunction
from bioweb_api.apis.probe_design.ApplicationGetFunction import ApplicationGetFunction

#=============================================================================
# Class
#=============================================================================
class ProbeDesignApiV1(AbstractApiV1):

    _FUNCTIONS = [
                  ProbeExperimentMetadataPostFunction(),
                  ProbeExperimentMetadataGetFunction(),
                  ProbeExperimentMetadataDeleteFunction(),
                  ProbeExperimentPostFunction(),
                  ProbeExperimentGetFunction(),
                  ProbeExperimentDeleteFunction(),
#                   ExperimentPostFunction(),
#                   ExperimentGetFunction(),
                  AbsorptionPostFunction(),
                  AbsorptionGetFunction(),
                  AbsorptionDeleteFunction(),
                  TargetsPostFunction(),
                  TargetsGetFunction(),
                  TargetsDeleteFunction(),
                  ProbesPostFunction(),
                  ProbesGetFunction(),
                  ProbesDeleteFunction(),
                  ApplicationGetFunction(),
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