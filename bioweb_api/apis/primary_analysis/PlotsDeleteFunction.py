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
@date:   Jan 28, 2015
'''

#=============================================================================
# Imports
#=============================================================================

from bioweb_api.apis.AbstractDeleteJobFunction import AbstractDeleteJobFunction
from bioweb_api.apis.ApiConstants import PLOT
from bioweb_api import PA_PLOTS_COLLECTION

#=============================================================================
# Class
#=============================================================================
class PlotsDeleteFunction(AbstractDeleteJobFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Plots"
   
    @staticmethod
    def summary():
        return "Delete primary analysis plots jobs."
    
    @classmethod
    def get_collection(cls):
        return PA_PLOTS_COLLECTION
    
    @classmethod
    def process_request(cls, params_dict, del_file_keys=(PLOT,)):
        return super(PlotsDeleteFunction, cls).process_request(params_dict, del_file_keys=del_file_keys)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = PlotsDeleteFunction()
    print function