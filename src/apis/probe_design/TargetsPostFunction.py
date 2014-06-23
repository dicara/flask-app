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

from src.apis.ApiConstants import TIME_FORMAT, FORMAT, FILENAME, FILEPATH, ID, \
    URL, DATESTAMP, TYPE, ERROR, UUID
from src.apis.AbstractPostFunction import AbstractPostFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from src import HOSTNAME, TARGETS_UPLOAD_FOLDER, TARGETS_COLLECTION
from src.utilities.bio_utilities import validate_fasta

#=============================================================================
# Class
#=============================================================================
class TargetsPostFunction(AbstractPostFunction):
    
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
        return "The returned uuid identifies the uploaded file and must " \
            "be used to select this file as input to APIs that consume " \
            "targets files."
   
    def response_messages(self):
        msgs = super(TargetsPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "File already exists. Delete the existing file and retry."},
                     { "code": 415, 
                       "message": "File is not a valid FASTA file."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.file("Targets FASTA file.")
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        targets_file     = params_dict[ParameterFactory.file("Targets FASTA file.")][0]
        json_response    = {FILENAME: targets_file.filename}
        http_status_code = 200
        file_uuid        = str(uuid4())
        
        path = os.path.join(TARGETS_UPLOAD_FOLDER, file_uuid)
        existing_filenames = cls._DB_CONNECTOR.distinct(TARGETS_COLLECTION, FILENAME)
        if os.path.exists(path) or targets_file.filename in existing_filenames:
            http_status_code     = 403
        elif validate_fasta(targets_file) == False:
            http_status_code     = 415
        else:
            try:
                targets_file.save(path)
                targets_file.close()
                json_response[URL]       = "http://%s/targets/%s" % (HOSTNAME, file_uuid)
                json_response[FILEPATH]  = path
                json_response[UUID]      = file_uuid
                json_response[DATESTAMP] = datetime.today()
                json_response[TYPE]      = "targets"
                if "." in targets_file.filename:
                    json_response[FORMAT] = targets_file.filename.split(".")[-1]
                else:
                    json_response[FORMAT] = "Unknown"
                    
                cls._DB_CONNECTOR.insert(TARGETS_COLLECTION, [json_response])
                del json_response[ID]
            except:
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500
        
        return make_response(jsonify(json_response), http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = TargetsPostFunction()
    print function