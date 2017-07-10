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
from bioweb_api.apis.full_analysis.FullAnalysisPostFunction import FULL_ANALYSIS
from bioweb_api.apis.AbstractDeleteJobFunction import AbstractDeleteJobFunction
from bioweb_api import FA_PROCESS_COLLECTION

#=============================================================================
# Class
#=============================================================================
class FullAnalysisDeleteFunction(AbstractDeleteJobFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return FULL_ANALYSIS

    @staticmethod
    def summary():
        return "Delete full analysis jobs."

    @classmethod
    def get_collection(cls):
        return FA_PROCESS_COLLECTION

    @classmethod
    def process_request(cls, params_dict, del_file_keys=()):
        return super(FullAnalysisDeleteFunction, cls).process_request(params_dict, del_file_keys=del_file_keys)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = FullAnalysisDeleteFunction()
    print function
