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

from src.apis.AbstractDeleteJobFunction import AbstractDeleteJobFunction
from src import PA_PROCESS_COLLECTION

#=============================================================================
# Class
#=============================================================================
class ProcessDeleteFunction(AbstractDeleteJobFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Process"
   
    @staticmethod
    def summary():
        return "Delete primary analysis process jobs."
    
    @classmethod
    def get_collection(cls):
        return PA_PROCESS_COLLECTION

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProcessDeleteFunction()
    print function