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
from src.apis.AbstractGetFunction import AbstractGetFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from idt_analyzer.idtClient import IDTClient

#=============================================================================
# Class
#=============================================================================
class IdtFunction(AbstractGetFunction):
    
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
        return "Retrieve sequence melting temperature(s) via IDT (Integrated " \
               "DNA Technologies) SOAP service for sequence analysis. " \
               "Please note, every provided sequence must have an " \
               "accompanying name. Names are assigned to sequences in the " \
               "order in which they are provided, so order matters."
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.format(),
                      ParameterFactory.sequence_names(required=True),
                      ParameterFactory.sequences(required=True),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        sequences      = params_dict[ParameterFactory.sequences(required=True)]
        sequence_names = params_dict[ParameterFactory.sequence_names(required=True)]
        
        # Every sequence must have an accompanying name
        if len(sequences) != len(sequence_names):
            return (None, None, None)
        
        data = list()
        for i, sequence in enumerate(sequences):
            melting_temp = cls._IDT_CLIENT.get_melting_temp(sequence)
            data.append({"Name": sequence_names[i], 
                         "Sequence": sequence,
                         "Tm": melting_temp.tm})
        columns = ["Name", "Sequence", "Tm"]
        return (data, columns, None)
#         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = IdtFunction()
    print function