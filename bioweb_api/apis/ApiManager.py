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
from collections import defaultdict

from bioweb_api.apis.snp_search.SnpSearchApi import SnpSearchApiV1
from bioweb_api.apis.melting_temperature.MeltingTemperatureApi import MeltingTemperatureApiV1
from bioweb_api.apis.probe_design.ProbeDesignApi import ProbeDesignApiV1
from bioweb_api.apis.primary_analysis.PrimaryAnalysisApi import PrimaryAnalysisApiV1
from bioweb_api.apis.secondary_analysis.SecondaryAnalysisApi import SecondaryAnalysisAPIV1
from bioweb_api.apis.ApiConstants import API, API_DOCS, SWAGGER_VERSION

#=============================================================================
# Public Global Variables
#=============================================================================
API_BASE_ROUTE       = "/%s" % API
API_DOCS_BASE_ROUTE  = "/%s" % API_DOCS

#=============================================================================
# Private Global Variables
#=============================================================================
_APIS = [
         SnpSearchApiV1(),
         MeltingTemperatureApiV1(),
         ProbeDesignApiV1(),
         PrimaryAnalysisApiV1(),
         SecondaryAnalysisAPIV1(),
        ]

_APIS_DICT = defaultdict(dict)
for api in _APIS:
    name = api.name()
    _APIS_DICT[name][api.version()] = api

#=============================================================================
# Class
#=============================================================================
class ApiManager(object):

    @staticmethod
    def get_apis():
        return _APIS
    
    @staticmethod
    def get_api(name, version):
        version = version.lower()
        if name in _APIS_DICT and version in _APIS_DICT[name]:
            return _APIS_DICT[name][version]
        return None
    
    @classmethod
    def get_api_function(cls, name, version, path, method):
        api = cls.get_api(name, version)
        if api:
            return api.get_function(path, method)
        return None
    
    @classmethod
    def getSwaggerResourceListing(cls):
        '''
        The Swagger RESTful API Documentation provides a schema for its 
        resource listing here:
         
        https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#51-resource-listing
        '''
        swagger_resource_listing = dict()
        swagger_resource_listing["apiVersion"] = "1.0.0"
        swagger_resource_listing["swaggerVersion"] = SWAGGER_VERSION
        swagger_resource_listing["apis"] = list()
        for api in cls.get_apis():
            swagger_resource_listing["apis"].append(api.getSwaggerResource())
        return swagger_resource_listing
    
    @classmethod
    def getSwaggerApiDeclaration(cls, name, version):
        '''
        The Swagger RESTful API Documentation provides a schema for its API
        declaration here:
         
        https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#52-api-declaration
        '''
        api = cls.get_api(name, version)
        if api:
            return api.getSwaggerApiDeclaration()
