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
from flask import make_response, jsonify

from src.apis.AbstractPostFunction import AbstractPostFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from src.apis.melting_temperature.idtClient import IDTClient
from src import PROBES_COLLECTION, TARGETS_COLLECTION
from src.apis.ApiConstants import UUID, FILEPATH

#=============================================================================
# Class
#=============================================================================
class ValidationPostFunction(AbstractPostFunction):
    
    _IDT_CLIENT = IDTClient()
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Validity"
   
    @staticmethod
    def summary():
        return "Check the validity of a set of probes."
    
    @staticmethod
    def notes():
        return "Probes and targets files must be uploaded using their upload " \
            "APIs prior to calling this function. Use the provided uuids " \
            "returned by the upload APIs to select the targets and probes " \
            "for which you are performing this validation."
    
    def response_messages(self):
        msgs = super(ValidationPostFunction, self).response_messages()
#         msgs.extend([
#                      { "code": 403, 
#                        "message": "File already exists. Delete the existing file and retry."},
#                      { "code": 415, 
#                        "message": "File is not a valid FASTA file."},
#                     ])
        return msgs
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.format(),
                      ParameterFactory.file_uuid("probes", PROBES_COLLECTION),
                      ParameterFactory.file_uuid("targets", TARGETS_COLLECTION),
                      ParameterFactory.boolean("absorb", "Check for absorbed probes."),
                      ParameterFactory.integer("num", "Minimum number of probes for a target.",
                                               default=3, minimum=1),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        probes_file_uuid  = params_dict[ParameterFactory.file_uuid("probes", PROBES_COLLECTION)][0]
        targets_file_uuid = params_dict[ParameterFactory.file_uuid("targets", TARGETS_COLLECTION)][0]
        absorb            = params_dict[ParameterFactory.boolean("absorb", "Check for absorbed probes.")][0]
        num               = params_dict[ParameterFactory.integer("num", "Minimum number of probes for a target.",
                                               default=3, minimum=1)][0]
        json_repsonse = {
                         "probes": probes_file_uuid,
                         "targets": targets_file_uuid,
                         "absorb": absorb,
                         "num": num,
                         }

        print "Probes: %s" % probes_file_uuid
        path = cls._DB_CONNECTOR.find_one(PROBES_COLLECTION, UUID, probes_file_uuid)
        print "Probes record: %s" % path
        print "Targets: %s" % targets_file_uuid
        print "absorb: %s" % absorb
        print "num: %s" % num
        
        return make_response(jsonify(json_repsonse), 500)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ValidationPostFunction()
    print function