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
class CaseSensitiveStringParameter(AbstractStringParameter):
    ''' 
    This parameter parses a string value provided in the api call and converts
    it into the appropriate case sensitive string for searching the database. 
    A required enum of valid case sensitive strings is used to perform this 
    mapping. Please note, similar strings of mixed case (e.g. ["foo", "FOO"])
    are prohibited in the enum, because the mapping is of lower case string to 
    case-sensitive string which would result in duplicate keys.
    '''

    #===========================================================================
    # Constructor
    #===========================================================================    
    ''' '''
    def __init__(self, name, description, enum=None, alias=None, required=False, 
                 allow_multiple=True, default=None, 
                 param_type=PARAMETER_TYPES.query):         # @UndefinedVariable
        
        self._mapping = None
        
        # Super constructor calls update_case, so the map must be populated
        # prior to calling super
        if enum:
            if len(enum) > len(set([x.lower() for x in enum])):
                raise Exception("Enum cannot contain duplicate entries: %s" % enum)
            self._mapping = {v.lower(): v for v in enum}

        super(CaseSensitiveStringParameter, self).__init__(name, alias, 
                                                           description, 
                                                           required, 
                                                           allow_multiple,
                                                           default, 
                                                           enum, 
                                                           param_type)
        
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    def update_case(self, s):
        ''' 
        If a fixed set of case sensitive strings was provided, then abide by it.
        '''
        if self._mapping:
            if isinstance(s, list):
                new_s = list()
                for item in s:
                    new_s.append(self._map_case(item))
                return new_s
            else:
                return self._map_case(s)
        return s
    
    def _map_case(self, s):
        if s.lower() not in self._mapping:
                raise Exception("Unrecognized input argument: %s" % s)
        return self._mapping[s.lower()]
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    parameter = CaseSensitiveStringParameter("StringParameter", 
                                             "StringParameter description.",
                                             ['This', 'THaT'],
                                             alias="StringParameterAlias",
                                             required=True, allow_multiple=False, 
                                             default="that")
    print parameter
    print parameter._convert_args(['THiS', 'that'])