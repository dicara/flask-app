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
from src.apis.AbstractDeleteFunction import AbstractDeleteFunction
from src.apis.ApiConstants import ID, PROBE_ID
from src.apis.parameters.ParameterFactory import ParameterFactory
from src import PROBE_METADATA_COLLECTION

#=============================================================================
# Class
#=============================================================================
class ProbeExperimentMetadataDeleteFunction(AbstractDeleteFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "ProbeExperimentMetadata"
   
    @staticmethod
    def summary():
        return "Delete probe design experiment metadata."
    
    @staticmethod
    def notes():
        return ""
    
    @classmethod
    def parameters(cls):
        pid_enum = cls._DB_CONNECTOR.distinct(PROBE_METADATA_COLLECTION,
                                              PROBE_ID)
        cls._pid_param  = ParameterFactory.lc_string(PROBE_ID, "Probe ID(s).", 
                                                     required=True, 
                                                     allow_multiple=True,
                                                     enum=pid_enum)
        parameters = [
                      cls._pid_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        response         = {}
        http_status_code = 200
        probe_ids        = params_dict[cls._pid_param]
        criteria         = {PROBE_ID: {"$in": probe_ids}}
        
        records = cls._DB_CONNECTOR.find(PROBE_METADATA_COLLECTION, 
                                         criteria, {ID:0})
        response["deleted"] = {}
        num_expected_deletions = 0
        if len(records) > 0:
            # Record records
            for record in records:
                response["deleted"][record[PROBE_ID]] = record
                num_expected_deletions += 1
            
            # Delete records from database
            result = cls._DB_CONNECTOR.remove(PROBE_METADATA_COLLECTION, 
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
    function = ProbeExperimentMetadataDeleteFunction()
    print function