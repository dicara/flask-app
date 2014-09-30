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
from bioweb_api.apis.ApiConstants import SWAGGER_TYPES

#=============================================================================
# Class
#=============================================================================
class SortParameter(AbstractParameter):
    ''' 
    This parameter takes a list of parameters that the user can provide in the
    api call for sorting the returned result. If you want Swagger to display
    the alias in the UI, then keep use_alias set to True. Otherwise, set it to
    False to display the name in the Swagger UI. 
    '''

    #===========================================================================
    # Constructors
    #===========================================================================    
    ''' '''
    def __init__(self, name, description, default, parameters, use_alias=True,
                 required=False):
        super(SortParameter, self).__init__(name, name, description, 
                                              required=required, 
                                              allow_multiple=False)
        
        if not isinstance(default, AbstractParameter):
            raise Exception("Default must be an AbstractParameter but found: %s" % type(default))
        
        if use_alias:
            self._default     = default.alias
        else:
            self._default     = default.name
        self._parameters  = self._ensureNotNone("parameters", parameters)
        
        if not isinstance(self.default, str) and not isinstance(self.default, unicode):
            raise Exception("Expected default to be of type str but found: %s" % type(self.default))
        
        if use_alias:
            self._pmap = {p.alias: p.name for p in self._parameters}
        else:
            self._pmap = {p.name: p.name for p in self._parameters}
        self._enum = self._pmap.keys()
        
        if False in map(lambda x: isinstance(x, str) or isinstance(x,unicode), self.enum):
            raise Exception("All enum values must be strings but found: %s" % self.enum)
        self._ensure_default_in_enum()
        
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.string                         # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        sort_by = raw_args[0].lower()
        
        # Input sort_by should be case-insensitive
        for k in self.enum:
            if sort_by == k.lower():
                return [self._pmap[k]]
        else:
            raise Exception("Provided argument (%s) is not in set of valids: %s" % (sort_by, self.enum))
        
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    parameter = SortParameter("SortParameter", "SortParameter description.",
                                required=True, allow_multiple=True, 
                                default="THIS", enum=['THIS', 'THAT'])
    print parameter
#     print parameter._convert_args(['ThiS', 'that'])
    print parameter._convert_args(['THIS', 'THAT'])