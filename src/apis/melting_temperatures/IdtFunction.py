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
from src.apis.AbstractFunction import AbstractFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from src.apis.melting_temperatures.idtClient import IDTClient

#=============================================================================
# Class
#=============================================================================
class IdtFunction(AbstractFunction):
    
    _IDT_CLIENT = IDTClient()
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "IDT"
   
    @staticmethod
    def summary():
        return "Retrieve melting temperature(s) via IDT."
    
    @staticmethod
    def notes():
        return "Retrieve oligonucleotide sequence melting temperature(s) via "\
               "IDT (Integrated DNA Technologies) SOAP service for " \
               "primer analysis."
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.format(),
                      ParameterFactory.sequence(required=True),
                     ]
        return parameters
    
    @classmethod
    def get_records(cls, params_dict):
        sequences = params_dict[ParameterFactory.sequence(required=True)]
        data = list()
        for sequence in sequences:
            melting_temp = cls._IDT_CLIENT.get_melting_temp(sequence)
            data.append({"sequence": sequence, "melting_temp": melting_temp})
        return (data, None, None)
#         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = IdtFunction()
    print function