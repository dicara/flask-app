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
from bioweb_api.apis.parameters.AbstractParameter import AbstractParameter 
from bioweb_api.apis.ApiConstants import SWAGGER_TYPES, EQUALITY

#=============================================================================
# Class
#=============================================================================
class FloatParameter(AbstractParameter):
    ''' 
    This parameter parses a float value provided in the api call and translates
    it into a float object for searching the database.
    '''

    #===========================================================================
    # Constructors
    #===========================================================================    
    ''' '''
    def __init__(self, name, description, alias=None, required=False, 
                 allow_multiple=True, default=None, enum=None, minimum=None, 
                 maximum=None,equality=None):
        
        if alias is None:
            alias = name
        
        super(FloatParameter, self).__init__(name, alias, description, 
                                             required=required, 
                                             allow_multiple=allow_multiple)
        
        if default is not None:
            self._default = self.__convert_float(default)
        
        if minimum:
            self._minimum = self.__convert_float(minimum)

        if maximum:
            self._maximum = self.__convert_float(maximum)
            
        if enum:
            self._enum = self._convert_args(enum)
            self._ensure_default_in_enum()
            
        if equality and equality not in EQUALITY._fields:
            raise Exception("Equality (%s) must be one of %s." % (equality, EQUALITY._fields))
        
        self._equality = equality
        
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.number                         # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        args = map(self.__convert_float, raw_args)
        if self.minimum:
            args = filter(lambda x: x>= self.minimum, args)
        if self.maximum:
            args = filter(lambda x: x<= self.maximum, args)
        return args
        
    #===========================================================================
    # Public Instance Methods
    #===========================================================================    
    @staticmethod
    def __convert_float(value):
        if isinstance(value, float):
            return value
        return float(value)
        
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    parameter = FloatParameter("FloatParameter", "FloatParameter description.",
                                required=True, default=False)
    print parameter
#     print parameter._convert_args(['ThiS', 'that'])
    print parameter._convert_args(["t", "true"])