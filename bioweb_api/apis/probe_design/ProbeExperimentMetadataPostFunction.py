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

from bioweb_api.utilities.io_utilities import make_clean_response
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.io_utilities import get_dialect, silently_remove_file, \
    get_case_insensitive_dictreader
from bioweb_api import TMP_PATH, PROBE_METADATA_COLLECTION
from bioweb_api.apis.ApiConstants import FILENAME, ERROR, PROBE_METADATA_HEADERS, \
    PROBE_ID

#=============================================================================
# Class
#=============================================================================
class ProbeExperimentMetadataPostFunction(AbstractPostFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "ProbeExperimentMetadata"
   
    @staticmethod
    def summary():
        return "Upload probe design experiment metadata."
    
    def response_messages(self):
        msgs = super(ProbeExperimentMetadataPostFunction, 
                     self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "Probe(s) already exists. Delete the " \
                                  "existing probe(s) and retry."},
                     { "code": 415, 
                       "message": "File is not a valid experiment metadata " \
                                  "file."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        cls._file_param = ParameterFactory.file("Probe metadata file.")
        parameters = [
                      cls._file_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        metadata_file    = params_dict[cls._file_param][0]
        json_response    = { FILENAME: metadata_file.filename }
        http_status_code = 200
        file_uuid        = str(uuid4())
        path             = os.path.join(TMP_PATH, file_uuid)
        
        try:
            metadata_file.save(path)
            metadata_file.close()
            dialect = get_dialect(path)
            if dialect:
                probe_ids = cls._DB_CONNECTOR.distinct(PROBE_METADATA_COLLECTION, 
                                                       PROBE_ID)
                ids_are_unique = cls.update_db(dialect, path, probe_ids)
                if not ids_are_unique:
                    http_status_code = 403
            else:
                http_status_code = 415
                json_response[ERROR] = "Invalid file format - file must " \
                    "be either tab or comma delimited."
        except IOError:
            http_status_code     = 415
            json_response[ERROR] = str(sys.exc_info()[1])
        except:
            http_status_code     = 500
            json_response[ERROR] = str(sys.exc_info()[1])
        finally:
            silently_remove_file(path)
        
        return make_clean_response(json_response, http_status_code)
    
    @classmethod
    def update_db(cls, dialect, path, probe_ids):
        '''
        Read the metadata file and update the DB with its contents. If a 
        probe_id is encountered in the file that already exists in the DB, then
        immediately quit and return False (adding nothing to the DB). 
        
        @return True if update is successful, False if probe_id in file is one
                that already exists in the DB.
        '''
        records = list()
        with open(path) as f:
            reader = get_case_insensitive_dictreader(f, dialect, 
                                                     PROBE_METADATA_HEADERS)
            
            for row in reader:
                # Ensure probe_id is unique.
                if row[PROBE_ID] in probe_ids:
                    return False
                records.append({h: row[h] for h in PROBE_METADATA_HEADERS})
                
        cls._DB_CONNECTOR.insert(PROBE_METADATA_COLLECTION, records)
        
        return True
        
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbeExperimentMetadataPostFunction()
    print function