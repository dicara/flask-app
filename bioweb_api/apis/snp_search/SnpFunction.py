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
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from ncbi_utilities.ncbi_util import snps_in_interval_multiple

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
            ParameterFactory.snpsearch_name(required=True),
            ParameterFactory.chromosome_num(required=True),
            ParameterFactory.chromosome_start(required=True),
            ParameterFactory.chromosome_stop(required=True),
        ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        snp_search_name = params_dict[ParameterFactory.snpsearch_name(required=True)]
        chromosome_num = params_dict[ParameterFactory.chromosome_num(required=True)]
        start_pos = params_dict[ParameterFactory.chromosome_start(required=True)]
        stop_pos = params_dict[ParameterFactory.chromosome_stop(required=True)]

        data = list()
        ncbi_snps = snps_in_interval_multiple(snp_search_name, chromosome_num, start_pos, stop_pos)
        for snp in ncbi_snps:
            data.append(snp)

        columns = ['search_name', 'rs', 'chromosome', 'loc', 'ref', 'alt', 'validated']
        return data, columns, None

#
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = SnpFunction()
    print function