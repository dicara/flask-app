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
import sys

from flask import make_response, jsonify

from src.apis.AbstractDeleteFunction import AbstractDeleteFunction
from src.apis.ApiConstants import ID, UUID, RESULT, ERROR
from src.apis.parameters.ParameterFactory import ParameterFactory
from src import ABSORPTION_COLLECTION

#=============================================================================
# Class
#=============================================================================
class AbsorptionDeleteFunction(AbstractDeleteFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Absorption"
   
    @staticmethod
    def summary():
        return "Delete absorption jobs."
    
    @staticmethod
    def notes():
        return ""
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.lc_string(UUID, "Comma separated UUID(s).", 
                                                 allow_multiple=True,
                                                 enum=cls._DB_CONNECTOR.distinct(ABSORPTION_COLLECTION, UUID)),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        response         = {}
        http_status_code = 200
        uuid_param       = ParameterFactory.lc_string(UUID, "Comma separated UUID(s).", 
                                                      allow_multiple=True,
                                                      enum=cls._DB_CONNECTOR.distinct(ABSORPTION_COLLECTION, UUID))
        absorption_uuids = params_dict[uuid_param]
        criteria         = {UUID: {"$in": absorption_uuids}}
        
        try:
            records = cls._DB_CONNECTOR.find(ABSORPTION_COLLECTION, criteria, {ID:0})
            response["deleted"] = {}
            if len(records) > 0:
                # Record records
                for record in records:
                    response["deleted"][record[UUID]] = record
                
                # Delete records from database
                result = cls._DB_CONNECTOR.remove(ABSORPTION_COLLECTION, criteria)
                
                # Delete files from disk only if removal from DB was successful
                if result and result['n'] == len(response["deleted"]):
                    for _,record in response["deleted"].iteritems():
                        if RESULT in record and os.path.isfile(record[RESULT]):
                            os.remove(record[RESULT])
                else:
                    del response["deleted"]
                    raise Exception("Error deleting records from the database: %s" % result)
            else:
                http_status_code = 404
        except:
            response[ERROR]  = str(sys.exc_info()[1])
            http_status_code = 500
            
        return make_response(jsonify(response), http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = AbsorptionDeleteFunction()
    print function