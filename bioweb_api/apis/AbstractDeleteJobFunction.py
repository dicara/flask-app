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

from abc import ABCMeta

from bioweb_api.apis.AbstractDeleteFunction import AbstractDeleteFunction
from bioweb_api.apis.ApiConstants import ID, UUID, RESULT
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.logging_utilities import APP_LOGGER

#=============================================================================
# Class
#=============================================================================
class AbstractDeleteJobFunction(AbstractDeleteFunction):
    __metaclass__ = ABCMeta
    
    #===========================================================================
    # Abstract Class Methods
    #===========================================================================    
    @staticmethod
    def notes():
        return ""

    @classmethod
    def get_collection(cls):
        '''
        Retrieve the name of the collection
        '''
        raise NotImplementedError("AbstractDeleteJobFunction subclass must " \
                                  "implement get_collection method.")


    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.job_uuid(cls.get_collection()),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        response         = {}
        http_status_code = 200
        
        uuids     = params_dict[ParameterFactory.job_uuid(cls.get_collection())]
        criteria  = {UUID: {"$in": uuids}}
        
        APP_LOGGER.info("Deleting the following jobs: %s" % ",".join(uuids))
        records = cls._DB_CONNECTOR.find(cls.get_collection(), criteria, 
                                         {ID:0})
        response["deleted"] = {}
        if len(records) > 0:
            # Record records
            for record in records:
                response["deleted"][record[UUID]] = record
            
            # Delete records from database
            result = cls._DB_CONNECTOR.remove(cls.get_collection(), 
                                              criteria)
            
            # Delete files from disk only if removal from DB was successful
            if result and result['n'] == len(response["deleted"]):
                for _,record in response["deleted"].iteritems():
                    if RESULT in record and os.path.isfile(record[RESULT]):
                        os.remove(record[RESULT])
            else:
                del response["deleted"]
                raise Exception("Error deleting records from the " \
                                "database: %s" % result)
            APP_LOGGER.info("Successfully deleted the following jobs: %s" \
                            % ",".join(uuids))
        else:
            http_status_code = 404
            
        return response, http_status_code

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = AbstractDeleteJobFunction()
    print function