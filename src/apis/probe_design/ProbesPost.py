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
from src import HOSTNAME, PROBES_UPLOAD_FOLDER, PROBES_COLLECTION

#=============================================================================
# Class
#=============================================================================
class ProbesPost(AbstractPostFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Probes"
   
    @staticmethod
    def summary():
        return "Upload probes file."
    
    @staticmethod
    def notes():
        return "In depth description goes here."
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.file("Probes file.")
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        probes_file = params_dict[ParameterFactory.file("Probes file.")][0]
        json_response = {
                          FILENAME: probes_file.filename,
                          ERROR: "",
                        }
        http_status_code = 201
        file_uuid        = str(uuid4())

        path = os.path.join(PROBES_UPLOAD_FOLDER, file_uuid)
        existing_filenames = cls._DB_CONNECTOR.distinct(PROBES_COLLECTION, FILENAME)
        if os.path.exists(path) or probes_file.filename in existing_filenames:
            json_response[ERROR] = "File already exists. Delete the existing file and try again."
            http_status_code     = 403
        else:
            try:
                probes_file.save(path)
                probes_file.close()
                json_response[URL]       = "http://%s/probes/%s" % (HOSTNAME, file_uuid)
                json_response[FILEPATH]  = path
                json_response[UUID]      = file_uuid
                json_response[DATESTAMP] = datetime.today().strftime(TIME_FORMAT)
                json_response[TYPE]      = "probes"
                if "." in probes_file.filename:
                    json_response[FORMAT] = probes_file.filename.split(".")[-1]
                else:
                    json_response[FORMAT] = "Unknown"
                
                cls._DB_CONNECTOR.insert(PROBES_COLLECTION, [json_response])
                del json_response[ID]

            except:
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500
        
        return make_response(jsonify(json_response), http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbesPost()
    print function