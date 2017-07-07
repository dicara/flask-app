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
from abc import ABCMeta
from flask import jsonify, make_response

from bioweb_api.apis.AbstractFunction import AbstractFunction 
from bioweb_api.apis.ApiConstants import FORMATS, MISSING_VALUE, METHODS
from bioweb_api.utilities.io_utilities import make_clean_response

#=============================================================================
# Class
#=============================================================================
class AbstractGetFunction(AbstractFunction):
    __metaclass__ = ABCMeta
 
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def method():
        return METHODS.GET                                  # @UndefinedVariable
    
    @classmethod
    def handle_request(cls, query_params, path_fields):
        '''
        Example API call: http://<hostname>:<port>/api/v1/MeltingTemperatures/<user>/IDT?name=foo&sequence=bar
        
        In the above example, query_params would be {"name": "foo", 
        "sequence": "bar"} and path_fields would be [<user>]. After collecting 
        input parameters, call process_request(). Then return the results in the 
        requested format.
        '''
        (params_dict, _format) = cls._parse_query_params(query_params)
        cls._handle_path_fields(path_fields, params_dict)
        
        (items, column_names, page_info) = cls.process_request(params_dict)

        if items is None:
            return make_response(jsonify({"error": "Operation failed."}), 500)

        dict_items = False        
        if len(items) > 0:
            if isinstance(items[0], dict):
                dict_items = True
        
        if _format == FORMATS.json:                         # @UndefinedVariable
            response = {cls.name(): items}
            return make_clean_response(response, 200), _format, page_info
        elif _format == FORMATS.tsv:                        # @UndefinedVariable
            if dict_items:
                return cls._generate_delimited_output(items, "\t", column_names), _format, page_info
            else:
                tsv = cls.name()
                for item in items:
                    tsv += "\n" + item
                return make_response(tsv, 200), _format, page_info
        elif _format == FORMATS.csv:                        # @UndefinedVariable
            if dict_items:
                return cls._generate_delimited_output(items, ",", column_names), _format, page_info
            else:
                csv = cls.name()
                for item in items:
                    csv += "\n" + item
                return make_response(csv, 200), _format, page_info
        else:
            raise Exception("Unrecognized output format: %s." % _format)
        
    #===========================================================================
    # Helper Methods
    #===========================================================================    
    @classmethod
    def _generate_delimited_output(cls, records, delimiter, column_names=None):
        ''' This method converts records into TSV or CSV output formats. '''
        if column_names is None:
            column_names = cls._get_unique_attributes_sorted(records)
        delimited_output = delimiter.join(column_names)
        for record in records:
            fields = list()
            for column_name in column_names:
                if column_name in record:
                    fields.append(str(record[column_name]))
                else:
                    fields.append(MISSING_VALUE)
            delimited_output += "\n" + delimiter.join(fields)
        return delimited_output
    
    @staticmethod
    def _get_unique_attributes_sorted(records):
        ''' 
        Iterate over provided records to retrieve the set of unique attributes.
        Return a case insensitively sorted list of attributes.
        '''
        attributes = set()
        for record in records:
            attributes.update(record.keys())
        return sorted(list(attributes), key=lambda s: s.lower())