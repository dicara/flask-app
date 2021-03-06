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
from collections import OrderedDict

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import PROBE_EXPERIMENTS_COLLECTION
from bioweb_api.apis.ApiConstants import ID, RUN_ID, DATE, SAMPLE_ID, \
    PROBE_EXPERIMENT_HEADERS, PROBE_ID

#=============================================================================
# Class
#=============================================================================
class ProbeExperimentGetFunction(AbstractGetFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "ProbeExperiment"
   
    @staticmethod
    def summary():
        return "Retrieve probe design experiments."
    
    @classmethod
    def parameters(cls):
        sid_enum  = cls._DB_CONNECTOR.distinct(PROBE_EXPERIMENTS_COLLECTION,
                                               SAMPLE_ID)
        rid_enum  = cls._DB_CONNECTOR.distinct(PROBE_EXPERIMENTS_COLLECTION,
                                               RUN_ID)
        pid_enum  = cls._DB_CONNECTOR.distinct(PROBE_EXPERIMENTS_COLLECTION,
                                               PROBE_ID)
        date_enum = cls._DB_CONNECTOR.distinct(PROBE_EXPERIMENTS_COLLECTION,
                                               DATE)
        date_enum = map(lambda x: x.strftime("%Y_%m_%d"), date_enum)

        parameters = [
                      ParameterFactory.format(),
                      ParameterFactory.lc_string(SAMPLE_ID, 
                                                 "Genomic DNA Sample ID(s).",
                                                 required=False,
                                                 allow_multiple=True,
                                                 enum=sid_enum),
                      ParameterFactory.lc_string(RUN_ID, "Run ID(s).",
                                                 required=False,
                                                 allow_multiple=True,
                                                 enum=rid_enum),
                      ParameterFactory.lc_string(PROBE_ID, "Probe ID(s).",
                                                 required=False,
                                                 allow_multiple=True,
                                                 enum=pid_enum),
                      ParameterFactory.date(required=False, enum=date_enum)
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        columns            = OrderedDict()
        columns[ID]        = 0
        columns[RUN_ID]    = 1
        columns[DATE]      = 1
        columns[SAMPLE_ID] = 1
        for header in PROBE_EXPERIMENT_HEADERS:
            columns[header] = 1

        column_names = columns.keys()  
        column_names.remove(ID)         
        
        data = cls._DB_CONNECTOR.find_from_params(PROBE_EXPERIMENTS_COLLECTION, 
                                                  params_dict, columns)
        
        return (data, column_names, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbeExperimentGetFunction()
    print function