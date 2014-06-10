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

from abc import ABCMeta, abstractproperty
from pprint import pformat

from src.apis.ApiConstants import API_BASE_URL, SWAGGER_VERSION

#=============================================================================
# Class
#=============================================================================
class AbstractApiV1(object):
    __metaclass__ = ABCMeta
    
    #===========================================================================
    # Abstract Properties
    #===========================================================================    
    @abstractproperty
    def functions(self):
        '''
        List of functions available on this API. 
        '''
        raise NotImplementedError("AbstractAPI subclass must implement functions method.")

    #===========================================================================
    # Abstract Static Methods
    #===========================================================================    
    @staticmethod
    def name():
        '''
        Name of this API function that is included in the URL immediately 
        following the base URL and version.
        
        Example API call: http://<hostname>:<port>/api/v1/MeltingTemperatures/IDT?sequences=ACTGAAATTGGGCCCCCC,ACTGGGAAA
        In this example, name is MeltingTemperatures.
        '''

        raise NotImplementedError("AbstractAPI subclass must implement name method.")
    
    @staticmethod
    def description():
        ''' 
        A short description of the API that is displayed in the Swagger resource
        listing and in the Swagger UI next to the API name.
        '''
        raise NotImplementedError("AbstractAPI subclass must implement description method.")
    
    @staticmethod
    def preferred():
        ''' 
        When multiple API versions are available, preferred should be set to 
        True on the latest version indicating that it's the latest and greatest.
        '''
        raise NotImplementedError("AbstractAPI subclass must implement preferred method.")

    #===========================================================================
    # API Methods
    #===========================================================================    
    @staticmethod
    def version():
        ''' 
        Version of this API that is included in the URL immediately
        following the base URL.
        '''
        return "v1"
    
    @staticmethod
    def produces():
        return [
                "application/json",
                "text/tab-separated-values",
                "text/plain"
               ]
        
    @staticmethod
    def consumes():
        return None
        
    def url(self):
        ''' 
        Base URL to this API. Functions themselves will extend this URL with 
        their name and static path fields.
        '''
        return "/".join([API_BASE_URL, self.version(), self.name()])
    
    def get_function(self, path, method):
        ''' 
        Retrieve the appropriate function. Path is everything after the url()
        and before the query parameters (but including path parameters).
        
        For example API call: 
        Example API call: http://<hostname>:<port>/api/v1/MeltingTemperatures/IDT?sequences=ACTGAAATTGGGCCCCCC,ACTGGGAAA
        the path would be IDT.
        '''
        functions = filter(lambda f: self.__compare_path_signatures(f, path), self.functions)
        functions = filter(lambda f: method == f.method(), functions)
        if len(functions) > 1:
            raise Exception("Found >1 matching %s functions: %s." % (method, ",".join([f.name() for f in functions])))
        elif functions:
            return functions[0]
        else:
            return None
        
    #===========================================================================
    # Private Methods
    #===========================================================================    
    def __compare_path_signatures(self, function, path):
        ''' 
        Return true if the function path signature matches the provided 
        path_fields signature. For example, if the function path signature is
        MeltingTemperatures/IDT/{name}/{sequence}, then ensure path_fields is of
        the form [MeltingTemperatures, IDT, {name}, {sequence}] where {name}
        and {sequence} could actually be any string (i.e. this doesn't ensure 
        that dynamic fields are valid).
        '''
        if not path.startswith(function.static_path()):
            return False
        
        # Ensure provided number of path fields matches expected.
        if len(function.path().split(os.path.sep)) != len(path.split(os.path.sep)):
            return False
        
        return True

    def __repr__(self):
        ''' 
        Mainly for testing, this displays the Swagger declaration in properly 
        formatted JSON when you print an instance of this class.
        '''
        return pformat(self.getSwaggerApiDeclaration())

    #===========================================================================
    # Swagger Methods
    #===========================================================================    
    def getSwaggerResource(self):
        '''
        The Swagger RESTful API Documentation provides a schema for its 
        resource listing here:
         
        https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#51-resource-listing
        '''
        swagger_resource = dict()
        swagger_resource["path"] = "/%s/%s" % (self.version(), self.name())
        swagger_resource["description"] = self.description()
        return swagger_resource

    def getSwaggerApiDeclaration(self):
        '''
        The Swagger RESTful API Documentation provides a schema for its API
        declaration here:
         
        https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#52-api-declaration
        '''
        basePath     = os.path.join(API_BASE_URL, self.version())
        resourcePath = "/%s" % self.name()
        
        swagger_api_declaration = dict()
        swagger_api_declaration["apiVersion"]     = self.version()
        swagger_api_declaration["swaggerVersion"] = SWAGGER_VERSION
        swagger_api_declaration["basePath"]       = basePath
        swagger_api_declaration["resourcePath"]   = resourcePath
        swagger_api_declaration["produces"]       = self.produces()
        if self.consumes():
            swagger_api_declaration["consumes"]   = self.consumes()
        swagger_api_declaration["apis"]           = list()
        
        models = dict()
        for function in self.functions:
            swagger_api_declaration["apis"].append(function.getSwaggerDeclaration(resourcePath))
            cur_models = function.models()
            for cur_model in cur_models:
                for k,v in cur_model.model.iteritems():
                    if k in models:
                        if v != models[k]:
                            raise Exception("Duplicate models (%s) discovered that are not equal." % k)
                    else:
                        models[k] = v
        swagger_api_declaration["models"] = models
        
        return swagger_api_declaration
