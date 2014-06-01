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
from src.apis.ApiConstants import SWAGGER_TYPES, SWAGGER_FORMATS, EQUALITY

#=============================================================================
# Class
#=============================================================================
class IntegerParameter(AbstractParameter):
    ''' 
    This parameter parses an integer value provided in the api call and 
    translates it into a int object for searching the database.
    '''

    #===========================================================================
    # Constructors
    #===========================================================================    
    ''' '''
    def __init__(self, name, description, required=False, allow_multiple=True,
                 default=None, enum=None, minimum=None, maximum=None, equality=None,
                 format=SWAGGER_FORMATS.int32):             # @UndefinedVariable
        super(IntegerParameter, self).__init__(name, name, description, 
                                               required=required, 
                                               allow_multiple=allow_multiple)
        
        self._format  = format
        
        if self.format not in [SWAGGER_FORMATS.int32, SWAGGER_FORMATS.int64]: # @UndefinedVariable
            raise Exception("Invalid format for IntegerParameter: %s" % self.format)
        
        if default:
            self._default = self.__convert(default)
        
        if enum:
            self._enum = map(self.__convert, enum)
            self._ensure_default_in_enum()
            
        if minimum:
            self._minimum = self.__convert(minimum)

        if maximum:
            self._maximum = self.__convert(maximum)
            
        if equality and equality not in EQUALITY._fields:
            raise Exception("Equality (%s) must be one of %s." % (equality, EQUALITY._fields))
        
        self._equality = equality

        
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.integer                        # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        args = map(self.__convert, raw_args)
        if self.minimum:
            args = filter(lambda x: x>= self.minimum, args)
        if self.maximum:
            args = filter(lambda x: x<= self.maximum, args)
        return args
        
    #===========================================================================
    # Public Instance Methods
    #===========================================================================    
    def __convert(self, value):
        if self.format == SWAGGER_FORMATS.int32:            # @UndefinedVariable
            return self.__convert_int(value)
        elif self.format == SWAGGER_FORMATS.int64:          # @UndefinedVariable
            self.__convert_long(value)
        else:
            raise Exception("Invalid format for IntegerParameter: %s" % self.format)
    
    @staticmethod
    def __convert_int(value):
        if isinstance(value, int):
            return value
        return int(value)
        
    @staticmethod
    def __convert_long(value):
        if isinstance(value, long):
            return value
        return long(value)

        
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    parameter = IntegerParameter("IntegerParameter", "IntegerParameter description.",
                                required=True, default=False)
    print parameter
#     print parameter._convert_args(['ThiS', 'that'])
    print parameter._convert_args(["t", "true"])