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
from src.apis.ApiConstants import SWAGGER_TYPES, PARAMETER_TYPES

#=============================================================================
# Private Global Variables
#=============================================================================

#=============================================================================
# Class
#=============================================================================
class FileParameter(AbstractParameter):
    '''
    This parameter parses a file parameter.
    '''

    #===========================================================================
    # Constructors
    #===========================================================================    
    ''' '''
    def __init__(self, name, description, required=True):
        super(FileParameter, self).__init__(name, name, description,
                                            param_type=PARAMETER_TYPES.form,# @UndefinedVariable
                                            required=required)
        
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.File                           # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        return raw_args
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    pass