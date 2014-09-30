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

from bioweb_api.apis.AbstractDeleteJobFunction import AbstractDeleteJobFunction
from bioweb_api import ABSORPTION_COLLECTION

#=============================================================================
# Class
#=============================================================================
class AbsorptionDeleteFunction(AbstractDeleteJobFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Absorption"
   
    @staticmethod
    def summary():
        return "Delete absorption jobs."

    @classmethod
    def get_collection(cls):
        return ABSORPTION_COLLECTION

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = AbsorptionDeleteFunction()
    print function