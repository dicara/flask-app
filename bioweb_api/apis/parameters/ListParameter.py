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
@date:   Feb 10, 2017
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.parameters.AbstractParameter import AbstractParameter
from bioweb_api.apis.ApiConstants import SWAGGER_TYPES

#=============================================================================
# Class
#=============================================================================
class ListParameter(AbstractParameter):
    ''' 
    This parameter parses each element of a list into the specified parameter
    type..
    '''

    #===========================================================================
    # Constructor
    #===========================================================================    
    def __init__(self, name, description, parameter,
                 alias=None, required=False):
         
        if alias is None:
            alias = name
             
        super(ListParameter, self).__init__(name, alias, description,
                                                required=required, 
                                                allow_multiple=True)
        self._parameter   = parameter
 
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.string                         # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        converted_args   = self._parameter._convert_args(raw_args)
        return converted_args
        
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    from ParameterFactory import ParameterFactory
    parameter      = ParameterFactory.lc_string("foo", "bar")
    list_parameter = ListParameter("KeyValueParameter",
                                            "KeyValueParameter description.",
                                            parameter)

    print list_parameter._convert_args(["594:2", "DY633:2", "cY5.5:3"])