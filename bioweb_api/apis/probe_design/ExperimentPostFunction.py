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
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.io_utilities import silently_remove_file
from bioweb_api import HOSTNAME, PORT, PLATES_UPLOAD_PATH, PLATES_COLLECTION
from bioweb_api.apis.ApiConstants import FILENAME, FILEPATH, ID, URL, DATESTAMP, \
    TYPE, ERROR, UUID

#=============================================================================
# Class
#=============================================================================
class ExperimentPostFunction(AbstractPostFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Experiment"
   
    @staticmethod
    def summary():
        return "Upload experiment."
    
    @staticmethod
    def notes():
        return "."
    
    def response_messages(self):
        msgs = super(ExperimentPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "File already exists. Delete the existing file and retry."},
                     { "code": 415, 
                       "message": "File is not a valid experiment file."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.file("Raw plate reader data file."),
                      ParameterFactory.cs_string("probe_sequence", "Probe sequence."),
                      ParameterFactory.cs_string("probe_tm", "Probe melting temperature."),
                      ParameterFactory.cs_string("probe_length", "Probe melting temperature."),
                      ParameterFactory.cs_string("target_sequence", "Target sequence."),
                      ParameterFactory.cs_string("variant_location", "Variant location."),
                      ParameterFactory.cs_string("variant_allele", "Variant allele."),
                      ParameterFactory.cs_string("reference_allele", "Reference allele."),
                      ParameterFactory.cs_string("incubation_temp", "Incubation temperature (degrees celsius)."),
                      ParameterFactory.cs_string("incubation_time", "Incubation time (minutes)."),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        plate_file       = params_dict[ParameterFactory.file("Raw plate reader data file.")][0]
        probe_sequence   = params_dict[ParameterFactory.cs_string("probe_sequence", "Probe sequence.")][0]
        probe_tm         = params_dict[ParameterFactory.float("probe_tm", "Probe melting temperature (degrees celsius).")][0]
        probe_length     = params_dict[ParameterFactory.integer("probe_length", "Probe length.")][0]
        target_sequence  = params_dict[ParameterFactory.cs_string("target_sequence", "Target sequence.")][0]
        variant_location = params_dict[ParameterFactory.cs_string("variant_location", "Variant location.")][0]
        variant_allele   = params_dict[ParameterFactory.cs_string("variant_allele", "Variant allele.")][0]
        reference_allele = params_dict[ParameterFactory.cs_string("reference_allele", "Reference allele.")][0]
        incubation_temp  = params_dict[ParameterFactory.float("incubation_temp", "Incubation temperature (degrees celsius).")][0]
        incubation_time  = params_dict[ParameterFactory.float("incubation_time", "Incubation time (minutes).")][0]
        
        json_response     = {
                             FILENAME: plate_file.filename,
                             "probe_sequence": probe_sequence,
                             "probe_tm": probe_tm,
                             "probe_length": probe_length,
                             "target_sequence": target_sequence,
                             "variant_location": variant_location,
                             "variant_allele": variant_allele,
                             "reference_allele": reference_allele,
                             "incubation_temp": incubation_temp,
                             "incubation_time": incubation_time,
                           }
        http_status_code = 200
        file_uuid        = str(uuid4())

        path = os.path.join(PLATES_UPLOAD_PATH, file_uuid)
        existing_filenames = cls._DB_CONNECTOR.distinct(PLATES_COLLECTION, FILENAME)
        if os.path.exists(path) or plate_file.filename in existing_filenames:
            http_status_code     = 403
        else:
            try:
                plate_file.save(path)
                plate_file.close()
                json_response[URL]       = "http://%s/uploads/%s/plates/%s" % (HOSTNAME, PORT, file_uuid)
                json_response[FILEPATH]  = path
                json_response[UUID]      = file_uuid
                json_response[DATESTAMP] = datetime.today()
                json_response[TYPE]      = "plate"
                
                cls._DB_CONNECTOR.insert(PLATES_COLLECTION, [json_response])
                del json_response[ID]

            except:
                json_response[ERROR] = str(sys.exc_info()[1])
                http_status_code     = 500
            finally:
                silently_remove_file(path)
                
        return make_clean_response(json_response, http_status_code)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ExperimentPostFunction()
    print function