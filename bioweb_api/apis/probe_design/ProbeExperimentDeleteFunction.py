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
from collections import defaultdict

from bioweb_api.apis.AbstractDeleteFunction import AbstractDeleteFunction
from bioweb_api.apis.ApiConstants import ID, RUN_ID
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import PROBE_EXPERIMENTS_COLLECTION

#=============================================================================
# Class
#=============================================================================
class ProbeExperimentDeleteFunction(AbstractDeleteFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "ProbeExperiment"
   
    @staticmethod
    def summary():
        return "Delete probe design experiment run."
    
    @staticmethod
    def notes():
        return ""
    
    @classmethod
    def parameters(cls):
        rid_enum = cls._DB_CONNECTOR.distinct(PROBE_EXPERIMENTS_COLLECTION,
                                              RUN_ID)
        cls._rid_param  = ParameterFactory.lc_string(RUN_ID, "Run ID.", 
                                                     required=True, 
                                                     allow_multiple=True,
                                                     enum=rid_enum)
        parameters = [
                      cls._rid_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        response         = {}
        http_status_code = 200
        run_ids          = params_dict[cls._rid_param]
        criteria         = {RUN_ID: {"$in": run_ids}}
        
        records = cls._DB_CONNECTOR.find(PROBE_EXPERIMENTS_COLLECTION, 
                                         criteria, {ID:0})
        response["deleted"]    = defaultdict(list)
        num_expected_deletions = 0
        if len(records) > 0:
            # Record records
            for record in records:
                response["deleted"][record[RUN_ID]].append(record)
                num_expected_deletions += 1
            
            # Delete records from database
            result = cls._DB_CONNECTOR.remove(PROBE_EXPERIMENTS_COLLECTION, 
                                              criteria)
            
            # Check that all records were deleted successfully.
            if not result or result['n'] != num_expected_deletions:
                del response["deleted"]
                raise Exception("Error deleting records from the " \
                                "database: %s" % result)
        else:
            http_status_code = 404
            
        return response, http_status_code

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbeExperimentDeleteFunction()
    print function