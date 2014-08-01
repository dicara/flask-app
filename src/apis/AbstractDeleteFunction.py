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
import sys
import traceback

from abc import ABCMeta
from flask import make_response, jsonify

from src.apis.AbstractFunction import AbstractFunction 
from src.apis.ApiConstants import METHODS, ERROR
from src.utilities.logging_utilities import APP_LOGGER

#=============================================================================
# Class
#=============================================================================
class AbstractDeleteFunction(AbstractFunction):
    __metaclass__ = ABCMeta
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def method():
        return METHODS.DELETE                               # @UndefinedVariable
    
    def response_messages(self):
        return [
                { "code": 200, 
                  "message": "Record(s) deleted successfully."},
                { "code": 404, 
                  "message": "Deletion unsuccessful: no records found matching criteria."},
                { "code": 500, 
                  "message": "Operation failed."},
               ]
    
    @classmethod
    def handle_request(cls, query_params, path_fields):
        '''
        Example API call: http://<hostname>:<port>/api/v1/MeltingTemperatures/<user>/IDT?name=foo&sequence=bar
        
        In the above example, query_params would be {"name": "foo", 
        "sequence": "bar"} and path_fields would be [<user>]. After collecting 
        input parameters, call process_request(). Then return the results in the 
        requested format.
        '''
        (params_dict, _) = cls._parse_query_params(query_params)
        cls._handle_path_fields(path_fields, params_dict)
        
        response         = {}
        http_status_code = None
        try:
            response, http_status_code = cls.process_request(params_dict)
        except:
            APP_LOGGER.error("Failed to delete records: %s" % 
                             traceback.format_exc())
            http_status_code = 500
            response[ERROR]  = str(sys.exc_info()[1])
        
        return (make_response(jsonify(response), http_status_code), None, None)