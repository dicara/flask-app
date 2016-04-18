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
from collections import defaultdict

from bioweb_api.apis.full_analysis.FullAnalysisPostFunction import FULL_ANALYSIS
from bioweb_api.apis.AbstractDeleteJobFunction import AbstractDeleteJobFunction
from bioweb_api import FA_PROCESS_COLLECTION
from bioweb_api.apis.ApiConstants import UUID, PA_PROCESS_UUID, SA_IDENTITY_UUID, \
    SA_ASSAY_CALLER_UUID, SA_GENOTYPER_UUID
from bioweb_api.apis.primary_analysis.ProcessDeleteFunction import ProcessDeleteFunction
from bioweb_api.apis.secondary_analysis.IdentityDeleteFunction import IdentityDeleteFunction
from bioweb_api.apis.secondary_analysis.AssayCallerDeleteFunction import AssayCallerDeleteFunction
from bioweb_api.apis.secondary_analysis.GenotyperDeleteFunction import GenotyperDeleteFunction

#=============================================================================
# Class
#=============================================================================
class FullAnalysisDeleteFunction(AbstractDeleteJobFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return FULL_ANALYSIS

    @staticmethod
    def summary():
        return "Delete full analysis jobs."

    @classmethod
    def get_collection(cls):
        return FA_PROCESS_COLLECTION

    @classmethod
    def process_request(cls, params_dict, del_file_keys=()):
        fa_uuid = params_dict.values()[0][0]
        fa_document = cls._DB_CONNECTOR.find_one(FA_PROCESS_COLLECTION, UUID, fa_uuid)

        if PA_PROCESS_UUID in fa_document:
            query_params = defaultdict(list)
            query_params[UUID].append(fa_document[PA_PROCESS_UUID])
            pa_params_dict, _ = ProcessDeleteFunction._parse_query_params(query_params)
            ProcessDeleteFunction.process_request(pa_params_dict)

        if SA_IDENTITY_UUID in fa_document:
            query_params = defaultdict(list)
            query_params[UUID].append(fa_document[SA_IDENTITY_UUID])
            pa_params_dict, _ = IdentityDeleteFunction._parse_query_params(query_params)
            IdentityDeleteFunction.process_request(pa_params_dict)

        if SA_ASSAY_CALLER_UUID in fa_document:
            query_params = defaultdict(list)
            query_params[UUID].append(fa_document[SA_ASSAY_CALLER_UUID])
            pa_params_dict, _ = AssayCallerDeleteFunction._parse_query_params(query_params)
            AssayCallerDeleteFunction.process_request(pa_params_dict)

        if SA_GENOTYPER_UUID in fa_document:
            query_params = defaultdict(list)
            query_params[UUID].append(fa_document[SA_GENOTYPER_UUID])
            pa_params_dict, _ = GenotyperDeleteFunction._parse_query_params(query_params)
            GenotyperDeleteFunction.process_request(pa_params_dict)

        return super(FullAnalysisDeleteFunction, cls).process_request(params_dict, del_file_keys=del_file_keys)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = FullAnalysisDeleteFunction()
    print function