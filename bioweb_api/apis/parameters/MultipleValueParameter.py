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
class MultipleValueParameter(AbstractParameter):
    ''' 
    This parameter deals with cases where you want to pass multiple values
    of different data types in a single argument.  The argument must be a
    colon separated list,  The data type for each value is specified in
    the value_dtype variable.
    '''

    #===========================================================================
    # Constructor
    #===========================================================================    
    def __init__(self, name, description, value_dtypes,
                 alias=None, required=False):
        '''
        @param name:            String, parameter name
        @param description:     A string describing the parameter
        @param value_dtypes:    A list of parameter data types for each value
                                of an argument.
        @param alias:           String, alias
        @param required:        Bool specifying if the parameter is required.
        '''
         
        if alias is None:
            alias = name
             
        super(MultipleValueParameter, self).__init__(name, alias, description, 
                                                required=required, 
                                                allow_multiple=True)
        self._value_dtypes = value_dtypes
 
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.string                         # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        # each element is a list that will contain the non-converted values
        data_container = [list() for _ in self._value_dtypes]
        
        for raw_arg in raw_args:
            input_data = raw_arg.split(":")
            # make sure each argument is the correct length
            if len(input_data) != len(self._value_dtypes):
                raise Exception("Expected %d values separated "
                                "by a colon, but found: %s" %
                                (len(self._value_dtypes), raw_arg))
            # add to container
            for container, data in zip(data_container, input_data):
                container.append(data)

        # convert all data to appropriate type
        converted_data = list()
        for dtype, data in zip(self._value_dtypes, data_container):
            converted_data.append(dtype._convert_args(data))

        
        return list(zip(*converted_data))
        
#===============================================================================
# Run Main
#===============================================================================
# if __name__ == "__main__":
#     keys_parameter      = ParameterFactory.dyes()
#     values_parameter    = ParameterFactory.integer("foo", "bar", minimum=1)
#     key_value_parameter = MultipleValueParameter("MultipleValueParameter",
#                                             "MultipleValueParameter description.",
#                                             keys_parameter,
#                                             values_parameter,
#                                             )
#     print key_value_parameter
#     print key_value_parameter._convert_args(["594:0", "633:2", "cy5.5:3"])