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
@date:   Mar 3, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractApi import AbstractApiV1
from bioweb_api.apis.image.ImagesPostFunction import ImagesPostFunction
from bioweb_api.apis.image.ImagesGetFunction import ImagesGetFunction
from bioweb_api.apis.image.ImagesDeleteFunction import ImagesDeleteFunction

#=============================================================================
# Public Static Variables
#=============================================================================

#=============================================================================
# Private Static Variables
#=============================================================================

#=============================================================================
# Class
#=============================================================================
class ImageAPIV1(AbstractApiV1):
    
    _FUNCTIONS = [
                  ImagesPostFunction(),
                  ImagesGetFunction(),
                  ImagesDeleteFunction(),
                 ]
    
    @staticmethod
    def name():
        return "Image"
   
    @staticmethod
    def description():
        return "Functions for simulating, storing, and retrieving TDI Images."
    
    @staticmethod
    def preferred():
        return True
    
    @staticmethod
    def consumes():
        return ["multipart/form-data"]
    
    @property
    def functions(self):
        return self._FUNCTIONS
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    api = ImageAPIV1()
    print api        