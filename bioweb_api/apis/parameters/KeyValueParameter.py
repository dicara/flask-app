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
@date:   Feb 4, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.parameters.AbstractParameter import AbstractParameter
from bioweb_api.apis.ApiConstants import SWAGGER_TYPES

#=============================================================================
# Class
#=============================================================================
class KeyValueParameter(AbstractParameter):
    ''' 
    This parameter parses a string value provided in the api call and translates
    it into a dictionary.
    '''

    #===========================================================================
    # Constructor
    #===========================================================================    
    def __init__(self, name, description, keys_parameter, values_parameter, 
                 alias=None, required=False):
         
        if alias is None:
            alias = name
             
        super(KeyValueParameter, self).__init__(name, alias, description, 
                                                required=required, 
                                                allow_multiple=True)
        self._keys_parameter   = keys_parameter
        self._values_parameter = values_parameter
 
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.string                         # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        num_args = len(raw_args)
        keys     = list()
        values   = list()
        
        for raw_arg in raw_args:
            fields = raw_arg.split(":")
            if len(fields) != 2:
                raise Exception("Expected two components of argument ",
                                "separated by a colon, but found %s", raw_arg)
            keys.append(fields[0])
            values.append(fields[1])
            
        converted_keys   = self._keys_parameter._convert_args(keys)
        converted_values = self._values_parameter._convert_args(values)
        
        if num_args != len(converted_keys):
            raise Exception("Invalid arguments found: original (%s) converted (%s)",
                            keys, converted_keys)
        if num_args != len(converted_values):
            raise Exception("Invalid arguments found: original (%s) converted (%s)",
                            values, converted_values)
        
        return [(converted_keys[i], converted_values[i]) 
                for i in range(num_args)]
        
#===============================================================================
# Run Main
#===============================================================================
# if __name__ == "__main__":
#     keys_parameter      = ParameterFactory.dyes()
#     values_parameter    = ParameterFactory.integer("foo", "bar", minimum=1)
#     key_value_parameter = KeyValueParameter("KeyValueParameter",
#                                             "KeyValueParameter description.",
#                                             keys_parameter,
#                                             values_parameter,
#                                             )
#     print key_value_parameter
#     print key_value_parameter._convert_args(["594:0", "633:2", "cy5.5:3"])