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
from werkzeug.utils import secure_filename

from src.apis.AbstractPostFunction import AbstractPostFunction
from src.apis.ApiConstants import METHODS
from src.apis.parameters.ParameterFactory import ParameterFactory
from src import PROBES_UPLOAD_FOLDER

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
    
    @staticmethod
    def method():
        return METHODS.POST                                 # @UndefinedVariable
    
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
                          "file": probes_file.filename,
                          "error": ""
                        }
        http_status_code = 201
        path = os.path.join(PROBES_UPLOAD_FOLDER, secure_filename(probes_file.filename))
        if os.path.exists(path):
            json_response["error"]  = "File already exists."
            http_status_code        = 403
        else:
            try:
                probes_file.save(os.path.join(PROBES_UPLOAD_FOLDER, path))
                probes_file.close()
            except:
                json_response["error"]  = str(sys.exc_info()[1])
                http_status_code        = 500
        
        return make_response(jsonify(json_response), http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbesPost()
    print function