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
from abc import ABCMeta, abstractmethod

from src.apis.parameters.AbstractParameter import AbstractParameter 
from src.apis.ApiConstants import SWAGGER_TYPES

#=============================================================================
# Class
#=============================================================================
class AbstractStringParameter(AbstractParameter):
    __metaclass__ = ABCMeta

    ''' 
    This parameter parses a string value provided in the api call and translates
    it into the required case for searching the database via the update_case() 
    function.
    '''

    #===========================================================================
    # Constructor
    #===========================================================================    
    def __init__(self, name, alias, description, required, allow_multiple, 
                 default, enum, param_type):
        
        if alias is None:
            alias = name
            
        super(AbstractStringParameter, self).__init__(name, alias, description, 
                                                       required=required, 
                                                       allow_multiple=allow_multiple,
                                                       param_type=param_type)
        
        self._default = default
        self._enum    = enum
        
        if self.default:
            if not isinstance(self.default, str) and not isinstance(self.default, unicode):
                raise Exception("Expected default to be of type str but found: %s" % type(self.default))
            self._default = self.update_case(self._default)
        
        if self.enum:
            if False in map(lambda x: isinstance(x, str) or isinstance(x,unicode), self.enum):
                raise Exception("All enum values must be strings but found: %s" % self.enum)
            self._enum = map(self.update_case, self.enum)
            self._ensure_default_in_enum()
    
    #===========================================================================
    # Abstract Methods
    #===========================================================================    
    @abstractmethod
    def update_case(self, s):
        ''' 
        Convert input string to the appropriate case for searching the database. 
        This is a workaround for handling case insensitivity, since using case 
        insensitive regular expressions for querying the database was very slow.
        '''
        raise NotImplementedError("AbstractStringParameter subclass must implement update_case function.")

    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.string                         # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        fixed_case_args = map(self.update_case, raw_args)
        if self.enum:
            valid_strings = set(self.enum)
            if not set(fixed_case_args).issubset(valid_strings):
                invalid_args = set(fixed_case_args).difference(valid_strings)
                raise Exception("Provided arguments %s not a subset of valid arguments: %s" % (invalid_args, valid_strings))
        return fixed_case_args