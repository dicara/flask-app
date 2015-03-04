'''
Copyright 2015 Bio-Rad Laboratories, Inc.

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
@date:   Mar 4, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from collections import OrderedDict

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api import IMAGES_COLLECTION
from bioweb_api.apis.ApiConstants import FILENAME, ID, \
    RESULT, EXP_DEF_NAME, EXP_DEF_UUID, NUM_IMAGES,\
    DATESTAMP, UUID, NAME, DESCRIPTION, URL
from bioweb_api.apis.image.ImagesPostFunction import IMAGES

#=============================================================================
# Class
#=============================================================================
class ImagesGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return IMAGES
   
    @staticmethod
    def summary():
        return "Retrieve list of image stacks."
    
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
        columns               = OrderedDict()
        columns[ID]           = 0
        columns[FILENAME]     = 1
        columns[UUID]         = 1
        columns[DATESTAMP]    = 1
        columns[RESULT]       = 1
        columns[URL]          = 1
        columns[NAME]         = 1
        columns[DESCRIPTION]  = 1
        columns[EXP_DEF_NAME] = 1
        columns[EXP_DEF_UUID] = 1
        columns[NUM_IMAGES]   = 1
        
        column_names = columns.keys()  
        column_names.remove(ID)         
        
        data = cls._DB_CONNECTOR.find(IMAGES_COLLECTION, {}, columns)
         
        return (data, column_names, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ImagesGetFunction()
    print function