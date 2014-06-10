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
import os

from werkzeug.utils import secure_filename

from src.apis.AbstractPostFunction import AbstractPostFunction
from src.apis.ApiConstants import METHODS
from src.apis.parameters.ParameterFactory import ParameterFactory
from src import UPLOAD_FOLDER

#=============================================================================
# Class
#=============================================================================
class TargetsPost(AbstractPostFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Targets"
   
    @staticmethod
    def summary():
        return "Upload targets FASTA file."
    
    @staticmethod
    def notes():
        return "In depth description goes here."
    
    @staticmethod
    def method():
        return METHODS.POST                                 # @UndefinedVariable
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.file("Targets FASTA file.")
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        targets_file = params_dict[ParameterFactory.file("Targets FASTA file.")][0]
        print "filename: %s" % targets_file.filename
        print "save: %s" % targets_file.save(os.path.join(UPLOAD_FOLDER, secure_filename(targets_file.filename)))
        print "close: %s" % targets_file.close()
        return (None, None, None)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = TargetsPost()
    print function