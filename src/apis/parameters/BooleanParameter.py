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
from src.apis.parameters.AbstractParameter import AbstractParameter 
from src.apis.ApiConstants import SWAGGER_TYPES

#=============================================================================
# Private Global Variables
#=============================================================================
_VALID_TRUES = ["true", "t", "1" ]

#=============================================================================
# Class
#=============================================================================
class BooleanParameter(AbstractParameter):
    '''
    This parameter parses a boolean parameter provided in the api call and 
    translates it into a boolean object for searching the database. Valid true
    inputs are %s (case insensitive), anything else will be translated into 
    false.
    ''' % _VALID_TRUES  

    #===========================================================================
    # Constructors
    #===========================================================================    
    ''' '''
    def __init__(self, name, description, required=False, default=True):
        super(BooleanParameter, self).__init__(name, name, description, 
                                              required=required, 
                                              allow_multiple=False)
        
        self._default = default
        
        if not isinstance(self.default, bool):
            raise Exception("Default value must be a boolean but found: %s" % type(self.default))
        
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.boolean                        # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        return map(self.__convert_boolean, raw_args)
        
    #===========================================================================
    # Public Instance Methods
    #===========================================================================    
    @staticmethod
    def __convert_boolean(value):
        if isinstance(value, bool):
            return value
        return value.lower() in _VALID_TRUES
        
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    parameter = BooleanParameter("BooleanParameter", "BooleanParameter description.",
                                required=True, default=False)
    print parameter
#     print parameter._convert_args(['ThiS', 'that'])
    print parameter._convert_args(["t", "true"])