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
import os

from bioweb_api.apis.AbstractDeleteFunction import AbstractDeleteFunction
from bioweb_api.apis.ApiConstants import ID, UUID, FILEPATH
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import TARGETS_COLLECTION

#=============================================================================
# Class
#=============================================================================
class TargetsDeleteFunction(AbstractDeleteFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Targets"
   
    @staticmethod
    def summary():
        return "Delete targets FASTA files."
    
    @staticmethod
    def notes():
        return ""
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.uuid(),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        response         = {}
        http_status_code = 200
        targets_uuids    = params_dict[ParameterFactory.uuid()]
        criteria         = {UUID: {"$in": targets_uuids}}
        
        records = cls._DB_CONNECTOR.find(TARGETS_COLLECTION, criteria, {ID:0})
        response["deleted"] = {}
        if len(records) > 0:
            # Record records
            for record in records:
                response["deleted"][record[UUID]] = record
            
            # Delete records from database
            result = cls._DB_CONNECTOR.remove(TARGETS_COLLECTION, criteria)
            
            # Delete files from disk only if removal from DB was successful
            if result and result['n'] == len(response["deleted"]):
                for _,record in response["deleted"].iteritems():
                    os.remove(record[FILEPATH])
            else:
                del response["deleted"]
                raise Exception("Error deleting records from the database: %s" % result)
        else:
            http_status_code = 404
            
        return(response, http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = TargetsDeleteFunction()
    print function