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

from uuid import uuid4
from flask import make_response, jsonify
from datetime import datetime

from src.apis.ApiConstants import TIME_FORMAT
from src.apis.AbstractPostFunction import AbstractPostFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from src import HOSTNAME, TARGETS_UPLOAD_FOLDER, TARGETS_COLLECTION

#=============================================================================
# Class
#=============================================================================
class TargetsPost(AbstractPostFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Targets"
   
    @staticmethod
    def summary():
        return "Upload targets FASTA file."
    
    @staticmethod
    def notes():
        return "In depth description goes here."
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.file("Targets FASTA file.")
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        targets_file = params_dict[ParameterFactory.file("Targets FASTA file.")][0]
        json_response = {
                          "filename": targets_file.filename,
                          "error": ""
                        }
        http_status_code = 201
        file_uuid        = str(uuid4())
        path = os.path.join(TARGETS_UPLOAD_FOLDER, file_uuid)
        if os.path.exists(path):
            json_response["error"]  = "File already exists."
            http_status_code        = 403
        else:
            try:
                targets_file.save(path)
                targets_file.close()
                json_response["url"]  = "http://%s/targets/%s" % (HOSTNAME, file_uuid)
                json_response["filepath"] = path
                json_response["uuid"] = file_uuid
                json_response["datestamp"] = datetime.today().strftime(TIME_FORMAT)
                json_response["type"]      = "targets"
                if "." in targets_file.filename:
                    json_response["format"] = targets_file.filename.split(".")[-1]
                else:
                    json_response["format"] = "Unknown"
                    
                cls._DB_CONNECTOR.insert(TARGETS_COLLECTION, [json_response])
                print json_response
                
            except:
                json_response["error"]  = str(sys.exc_info()[1])
                http_status_code        = 500
        
        return make_response(jsonify(json_response), http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = TargetsPost()
    print function