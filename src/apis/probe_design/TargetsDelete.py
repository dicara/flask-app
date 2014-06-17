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

from src.apis.AbstractDeleteFunction import AbstractDeleteFunction
from src.apis.ApiConstants import UUID, FILEPATH
from src.apis.parameters.ParameterFactory import ParameterFactory
from src import TARGETS_COLLECTION

#=============================================================================
# Class
#=============================================================================
class TargetsDelete(AbstractDeleteFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Targets"
   
    @staticmethod
    def summary():
        return "Delete targets FASTA files."
    
    @staticmethod
    def notes():
        return ""
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.uuid(),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        targets_uuids = params_dict[ParameterFactory.uuid()]
        print targets_uuids
        criteria = dict()
        criteria[UUID] = {"$in": targets_uuids}
        print criteria
        records = cls._DB_CONNECTOR.find(TARGETS_COLLECTION, criteria)
        cls._DB_CONNECTOR.remove(TARGETS_COLLECTION, criteria)
        for record in records:
            print record
            os.remove(record[FILEPATH])
        return (None, None, None)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = TargetsDelete()
    print function