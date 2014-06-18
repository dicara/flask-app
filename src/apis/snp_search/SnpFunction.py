"""
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

@author: Nathan Brown
@date:   Jun 17, 2014
"""

# =============================================================================
# Imports
#=============================================================================
from src.apis.AbstractGetFunction import AbstractGetFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from src.apis.snp_search.ncbi_utilities import snps_in_interval

#=============================================================================
# Class
#=============================================================================
class SnpFunction(AbstractGetFunction):
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "search"

    @staticmethod
    def summary():
        return "Retrieve SNP within the specifice region from NCBI SNP Database"

    @staticmethod
    def notes():
        return "Retrieve SNP data from the NCBI SNP Database.  Inputs are the " \
               "start and stop position and chromosome"

    @classmethod
    def parameters(cls):
        parameters = [
            ParameterFactory.format(),
            ParameterFactory.chromosome_num(required=True),
            ParameterFactory.chromosome_start(required=True),
            ParameterFactory.chromosome_stop(required=True),
        ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        chromosome_num = params_dict[ParameterFactory.chromosome_num(required=True)][0]
        start_pos = params_dict[ParameterFactory.chromosome_start(required=True)][0]
        stop_pos = params_dict[ParameterFactory.chromosome_stop(required=True)][0]

        data = list()
        ncbi_snps = snps_in_interval(chromosome_num, start_pos, stop_pos)
        for snp in ncbi_snps:
            data.append(snp.to_dict())

        columns = ['rs', 'chromosome', 'loc', 'ref', 'alt']
        return data, columns, None

#
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = SnpFunction()
    print function