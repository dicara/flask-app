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

@author: Nathan Brown
@date:   Jun 17, 2014
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractApi import AbstractApiV1
from bioweb_api.apis.snp_search.SnpFunction import SnpFunction

#=============================================================================
# Class
#=============================================================================
class SnpSearchApiV1(AbstractApiV1):

    _FUNCTIONS = [SnpFunction()]

    @staticmethod
    def name():
        return "SNPSearch"
   
    @staticmethod
    def description():
        return "Locate SNP within a chromosome"
    
    @staticmethod
    def preferred():
        return True
    
    @property
    def functions(self):
        return self._FUNCTIONS
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    api = SnpSearchApiV1()
    print api