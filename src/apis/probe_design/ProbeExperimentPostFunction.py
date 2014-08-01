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

from src.apis.AbstractPostFunction import AbstractPostFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from src.utilities.io_utilities import get_dialect, silently_remove_file, \
    get_case_insensitive_dictreader
from src import TMP_PATH, PROBE_EXPERIMENTS_COLLECTION
from src.apis.ApiConstants import FILENAME, ERROR, RUN_ID, SAMPLE_ID, DATE, \
    PROBE_EXPERIMENT_HEADERS

#=============================================================================
# Class
#=============================================================================
class ProbeExperimentPostFunction(AbstractPostFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "ProbeExperiment"
   
    @staticmethod
    def summary():
        return "Upload probe design experiment."
    
    def response_messages(self):
        msgs = super(ProbeExperimentPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "Run already exists. Delete the existing " \
                                  "run and retry."},
                     { "code": 415, 
                       "message": "File is not a valid experiment file."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        cls._file_param = ParameterFactory.file("Experiment results file.")
        cls._sid_param  = ParameterFactory.lc_string(SAMPLE_ID, 
                                                     "Genomic DNA Sample ID.")
        cls._rid_param  = ParameterFactory.lc_string(RUN_ID, "Run ID.")
        cls._date_param = ParameterFactory.date()

        parameters = [
                      cls._file_param,
                      cls._sid_param,
                      cls._rid_param,
                      cls._date_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        exp_file  = params_dict[cls._file_param][0]
        sample_id = params_dict[cls._sid_param][0]
        run_id    = params_dict[cls._rid_param][0]
        run_date  = params_dict[cls._date_param][0]
        
        json_response = {
                         FILENAME: exp_file.filename,
                         RUN_ID: run_id,
                         DATE: run_date,
                         SAMPLE_ID: sample_id,
                        }
        http_status_code = 200
        file_uuid        = str(uuid4())

        path = os.path.join(TMP_PATH, file_uuid)
        run_ids = cls._DB_CONNECTOR.distinct(PROBE_EXPERIMENTS_COLLECTION, 
                                             RUN_ID)
        if run_id in run_ids:
            http_status_code     = 403
        else:
            try:
                exp_file.save(path)
                exp_file.close()
                dialect = get_dialect(path)
                if dialect:
                    cls.update_db(dialect, path, sample_id, run_id, run_date)
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
        
        return make_response(jsonify(json_response), http_status_code)
    
    @classmethod
    def update_db(cls, dialect, path, sample_id, run_id, run_date):
        '''
        Read the experiments file and update the DB with its contents.
        '''
        records = list()
        with open(path) as f:
            reader = get_case_insensitive_dictreader(f, dialect, 
                                                     PROBE_EXPERIMENT_HEADERS.keys())
            for row in reader:
                # Add file information and convert fields to their appropriate type
                record = {h: c(row[h]) for h,c in PROBE_EXPERIMENT_HEADERS.items()}
                
                # Add common information
                record[RUN_ID]    = run_id
                record[DATE]      = run_date
                record[SAMPLE_ID] = sample_id
                records.append(record)
                
        cls._DB_CONNECTOR.insert(PROBE_EXPERIMENTS_COLLECTION, records)
        
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbeExperimentPostFunction()
    path = "/home/ddicara/Documents/test"
    print function.validate_experiments_file(path)
#     print function