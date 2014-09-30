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
from bioweb_api.apis.parameters.AbstractStringParameter import AbstractStringParameter 
from bioweb_api.apis.ApiConstants import PARAMETER_TYPES

#=============================================================================
# Class
#=============================================================================
class LowerCaseStringParameter(AbstractStringParameter):
    ''' 
    This parameter parses a string value provided in the api call and converts
    it into an lower case string for searching the database. If a default value
    and/or enum are provided, they are also converted to lower case.
    '''

    #===========================================================================
    # Constructor
    #===========================================================================    
    ''' '''
    def __init__(self, name, description, alias=None, required=False, 
                 allow_multiple=True, default=None, enum=None, 
                 param_type=PARAMETER_TYPES.query):         # @UndefinedVariable
        
        super(LowerCaseStringParameter, self).__init__(name, alias, description, 
                                                       required, allow_multiple,
                                                       default, enum, 
                                                       param_type)
        
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    def update_case(self, s):
        return s.lower()
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    parameter = LowerCaseStringParameter("StringParameter", 
                                         "StringParameter description.",
                                         alias="StringParameterAlias",
                                         required=True, allow_multiple=False, 
                                         default="this", enum=['This', 'THaT'])
    print parameter
    print parameter._convert_args(['THiS', 'that'])