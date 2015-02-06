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
from datetime import datetime

from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.apis.ApiConstants import FORMAT, FILENAME, FILEPATH, ID, URL, \
    DATESTAMP, TYPE, ERROR, UUID
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import HOSTNAME, PORT, PROBES_UPLOAD_PATH, PROBES_COLLECTION
from bioweb_api.utilities.bio_utilities import validate_fasta

#=============================================================================
# Class
#=============================================================================
class ProbesPostFunction(AbstractPostFunction):
    
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
        return "The returned uuid identifies the uploaded file and must " \
            "be used to select this file as input to APIs that consume " \
            "probes files."
    
    def response_messages(self):
        msgs = super(ProbesPostFunction, self).response_messages()
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
                      ParameterFactory.file("Probes file.")
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        probes_file      = params_dict[ParameterFactory.file("Probes file.")][0]
        json_response    = {FILENAME: probes_file.filename}
        http_status_code = 200
        file_uuid        = str(uuid4())

        path = os.path.join(PROBES_UPLOAD_PATH, file_uuid)
        existing_filenames = cls._DB_CONNECTOR.distinct(PROBES_COLLECTION, FILENAME)
        if os.path.exists(path) or probes_file.filename in existing_filenames:
            http_status_code     = 403
        elif validate_fasta(probes_file) == False:
            http_status_code     = 415
        else:
            try:
                probes_file.save(path)
                probes_file.close()
                json_response[URL]       = "http://%s/uploads/%s/probes/%s" % (HOSTNAME, PORT, file_uuid)
                json_response[FILEPATH]  = path
                json_response[UUID]      = file_uuid
                json_response[DATESTAMP] = datetime.today()
                json_response[TYPE]      = "probes"
                if "." in probes_file.filename:
                    json_response[FORMAT] = probes_file.filename.split(".")[-1]
                else:
                    json_response[FORMAT] = "Unknown"
                
                cls._DB_CONNECTOR.insert(PROBES_COLLECTION, [json_response])
            except:
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500
            finally:
                if ID in json_response:
                    del json_response[ID]
        
        return make_clean_response(json_response, http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbesPostFunction()
    print function