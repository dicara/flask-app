'''
Copyright 2016 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Nathan Brown
@date:   March 28, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from collections import OrderedDict

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import FA_PROCESS_COLLECTION, PA_PROCESS_COLLECTION, \
    SA_IDENTITY_COLLECTION, SA_ASSAY_CALLER_COLLECTION, SA_GENOTYPER_COLLECTION
from bioweb_api.apis.ApiConstants import UUID, STATUS, ID, JOB_NAME, JOB_TYPE_NAME, \
    SUBMIT_DATESTAMP, START_DATESTAMP, FINISH_DATESTAMP, ERROR, PA_PROCESS_UUID, \
    SA_IDENTITY_UUID, SA_ASSAY_CALLER_UUID, SA_GENOTYPER_UUID

#=============================================================================
# Class
#=============================================================================
class FullAnalysisGetFunction(AbstractGetFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return 'Process'
   
    @staticmethod
    def summary():
        return "Retrieve list of full analysis jobs."
    
    @staticmethod
    def notes():
        return ""
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.format(),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        columns                   = OrderedDict()
        columns[ID]               = 0
        columns[JOB_NAME]         = 1
        columns[JOB_TYPE_NAME]    = 1
        columns[UUID]             = 1
        columns[STATUS]           = 1
        columns[SUBMIT_DATESTAMP] = 1
        columns[START_DATESTAMP]  = 1
        columns[FINISH_DATESTAMP] = 1
        columns[ERROR]            = 1
        columns[PA_PROCESS_UUID]  = 1
        columns[SA_IDENTITY_UUID] = 1
        columns[SA_ASSAY_CALLER_UUID] = 1
        columns[SA_GENOTYPER_UUID] = 1
        
        column_names = columns.keys()  
        column_names.remove(ID)         
        
        fa_documents = cls._DB_CONNECTOR.find(FA_PROCESS_COLLECTION, {}, columns)
        for fa_document in fa_documents:
            if PA_PROCESS_UUID in fa_document:
                pa_document = cls._DB_CONNECTOR.find_one(PA_PROCESS_COLLECTION, UUID, fa_document[PA_PROCESS_UUID])
                if pa_document:
                    if ID in pa_document:
                        del pa_document[ID]
                    fa_document['pa_document'] = pa_document
            if SA_IDENTITY_UUID in fa_document:
                id_document = cls._DB_CONNECTOR.find_one(SA_IDENTITY_COLLECTION, UUID, fa_document[SA_IDENTITY_UUID])
                if id_document:
                    if ID in id_document:
                        del id_document[ID]
                    fa_document['id_document'] = id_document
            if SA_ASSAY_CALLER_UUID in fa_document:
                ac_document = cls._DB_CONNECTOR.find_one(SA_ASSAY_CALLER_COLLECTION, UUID, fa_document[SA_ASSAY_CALLER_UUID])
                if ac_document:
                    if ID in ac_document:
                        del ac_document[ID]
                    fa_document['ac_document'] = ac_document
            if SA_GENOTYPER_UUID in fa_document:
                gt_document = cls._DB_CONNECTOR.find_one(SA_GENOTYPER_COLLECTION, UUID, fa_document[SA_GENOTYPER_UUID])
                if gt_document:
                    if ID in gt_document:
                        del gt_document[ID]
                    fa_document['gt_document'] = gt_document
         
        return (fa_documents, column_names, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = FullAnalysisGetFunction()
    print function