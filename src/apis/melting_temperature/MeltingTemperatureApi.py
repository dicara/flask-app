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
from src.apis.AbstractApi import AbstractApiV1
from src.apis.melting_temperature.IdtFunction import IdtFunction

#=============================================================================
# Class
#=============================================================================
class MeltingTemperatureApiV1(AbstractApiV1):

    _FUNCTIONS = [
                  IdtFunction(),
                 ]

    @staticmethod
    def name():
        return "MeltingTemperatures"
   
    @staticmethod
    def description():
        return "Functions for computing sequence melting temperatures."
    
    @staticmethod
    def preferred():
        return True
    
    @property
    def functions(self):
        return self._FUNCTIONS
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    api = MeltingTemperatureApiV1()
    print api