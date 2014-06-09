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
from src.apis.melting_temperature.idtClient import IDTClient

#=============================================================================
# Class
#=============================================================================
class ValidationFunction(AbstractFunction):
    
    _IDT_CLIENT = IDTClient()
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Validity"
   
    @staticmethod
    def summary():
        return "Check the validity of a set of probes."
    
    @staticmethod
    def notes():
        return "In depth description goes here."
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.format(),
                      ParameterFactory.file("targets", "Targets FASTA file."),
                      ParameterFactory.probes(required=True),
                      ParameterFactory.boolean("absorb", "Check for absorbed probes."),
                      ParameterFactory.integer("num", "Minimum number of probes for a target.",
                                               default=3, minimum=1),
                     ]
        return parameters
    
    @classmethod
    def get_records(cls, params_dict):
        print "file: %s" % params_dict[ParameterFactory.file("targets", "Targets FASTA file.")][0]
#         sequences      = params_dict[ParameterFactory.sequences(required=True)]
#         sequence_names = params_dict[ParameterFactory.sequence_names(required=True)]
#         
#         # Every sequence must have an accompanying name
#         if len(sequences) != len(sequence_names):
#             return (None, None, None)
#         
#         data = list()
#         for i, sequence in enumerate(sequences):
#             melting_temp = cls._IDT_CLIENT.get_melting_temp(sequence)
#             data.append({"Name": sequence_names[i], 
#                          "Sequence": sequence,
#                          "Tm": melting_temp.tm})
#         columns = ["Name", "Sequence", "Tm"]
#         return (data, columns, None)
        return (None, None, None)

         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ValidationFunction()
    print function