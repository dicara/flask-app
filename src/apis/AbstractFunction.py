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
import math    

from abc import ABCMeta
from pprint import pformat
from collections import Counter
from flask import jsonify


from src.apis.parameters.ParameterFactory import ParameterFactory
from src.apis.ApiConstants import FORMATS, MISSING_VALUE

#=============================================================================
# Class
#=============================================================================
class AbstractFunction(object):
    __metaclass__ = ABCMeta
    
    #===========================================================================
    # Constructor
    #===========================================================================    
    '''
    Ensure parameter name/alias pair are unique in the parameters list.
    '''
    def __init__(self):
        dups = [x for x, y in Counter([p.name + p.alias for p in self.parameters()]).items() if y > 1]
        if len(dups) > 0:
            raise Exception("Duplicate parameters not allowed: %s" % ", ".join(dups))
    
    #===========================================================================
    # Static Methods
    #===========================================================================    
    @classmethod
    def type(cls):
        '''
        This is either a Swagger defined Primitive 
        (https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#431-primitives), 
        an array, or Swagger model id. It describes the return value of this API 
        call. Documentation can be found at the following link.
        
        https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#dataTypeType
        '''
        return "void"

    @classmethod
    def models(cls):
        ''' 
        This is a Swagger definition of a function return value. Documentation
        can be found at the following link.
        
        https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#526-models-object
        '''
        return {}
    
    #===========================================================================
    # Abstract Static Methods
    #===========================================================================    
    @staticmethod
    def name():
        '''
        Name of this API function that is included in the URL as the last 
        non-parameter field.
        
        Example API call: http://<hostname>:<port>/api/v1/MeltingTemperatures/IDT?name=foo&sequence=bar
        In this example, name is IDT.
        '''
        raise NotImplementedError("AbstractFunction subclass must implement name method.")
    
    @staticmethod
    def summary():
        ''' 
        For use in the Swagger documentation. 
        
        A short summary of what the operation does. For maximum readability 
        in the swagger-ui, this field SHOULD be less than 120 characters.
        '''
        raise NotImplementedError("AbstractFunction subclass must implement summary method.")

    @staticmethod
    def notes():
        '''
        For use in the Swagger documentation.
         
        A verbose explanation of the operation behavior. 
        '''
        raise NotImplementedError("AbstractFunction subclass must implement notes method.")
    
    #===========================================================================
    # Abstract Class Methods
    #===========================================================================    
    @classmethod
    def parameters(cls):
        ''' 
        List of valid parameters (both path and query) for this function. ORDER
        MATTERS: path parameters are added to the Swagger docs path (and parsed
        from the provided path) in the order in which they appear in this list.
        In other words, if you your desired function path is
        /MeltingTemperatures/IDT/{name}/{sequence} then the name parameter 
        must come before sequence and they both must have 
        param_type == PARAMETER_TYPES.path.
        '''
        raise NotImplementedError("AbstractFunction subclass must implement parameters method.")

    @classmethod
    def get_records(cls, params_dict):
        '''
        Query the database using the provided params_dict to filter results 
        accordingly. Return a tuple of the form (<data>, <column_names>, and 
        <pagination_info>. The column_names may be None, but if not it describes
        the order in which to display the columns when output format is TSV or 
        CSV. The pagination info may also be None, but if not it is also a tuple 
        of page, page_size, and num_pages for use in paginating results. These 
        are used to populate link headers in the returned result to the user. 
        The links are to the first, previous, next, and last page of results to
        simplify paginated results retrieval.
        '''
        raise NotImplementedError("AbstractTableFunction subclass must implement get_records method.")

    #===========================================================================
    # Helper Methods
    #===========================================================================    
    @classmethod
    def getData(cls, query_params, path_fields):
        '''
        Example API call: http://<hostname>:<port>/api/v1/MeltingTemperatures/IDT?name=foo&sequence=bar
        
        In the above example, query_params would be {"name": "foo", 
        "sequence": "bar"} and 
        path_fields would be ["ACC"]. After collecting input parameters,
        call get_records() to query the database and retrieve the filtered
        records. Then return the results in the requested format.
        '''
        (params_dict, _format) = cls._parse_query_params(query_params)
        cls._handle_path_fields(path_fields, params_dict)
        
        (items, column_names, page_info) = cls.get_records(params_dict)

        dict_items = False        
        if len(items) > 0:
            if isinstance(items[0], dict):
                dict_items = True
        
        if _format == FORMATS.json:                         # @UndefinedVariable
            # jsonify allows NaNs which are not valid json, so replace with None
            jsonified_data = jsonify({cls.name(): cls.remove_nans_from_list(items)})
            return jsonified_data, _format, page_info
        elif _format == FORMATS.tsv:                        # @UndefinedVariable
            if dict_items:
                return cls._generate_delimited_output(items, "\t", column_names), _format, page_info
            else:
                tsv = cls.name()
                for item in items:
                    tsv += "\n" + item
                return tsv, _format, page_info
        elif _format == FORMATS.csv:                        # @UndefinedVariable
            if dict_items:
                return cls._generate_delimited_output(items, ",", column_names), _format, page_info
            else:
                csv = cls.name()
                for item in items:
                    csv += "\n" + item
                return csv, _format, page_info
        else:
            raise Exception("Unrecognized output format: %s." % _format)
        
    @classmethod
    def remove_nans_from_list(cls, l):
        ''' Create new list replacing NaN with None. '''
        new_list = list()
        for item in l:
            if isinstance(item, list):
                new_list.append(cls.handle_list(item))
            elif isinstance(item, dict):
                for k,v in item.iteritems():
                    cls.remove_nans_from_dict(item, k, v)
                new_list.append(item)
            elif isinstance(item, float) and math.isnan(item):
                new_list.append(None)
            else:
                new_list.append(item)
        return new_list
    
    @classmethod
    def remove_nans_from_dict(cls, in_dict, in_key, in_value):
        ''' Update in-place replacing NaN with None.'''
        if isinstance(in_value, list):
            in_dict[in_key] = cls.remove_nans_from_list(in_value)
        elif isinstance(in_value, dict):
            for key, value in in_value.iteritems():
                cls.a(in_value, key, value)
        elif isinstance(in_value, float) and math.isnan(in_value):
            in_dict[in_key] = None
        
        
    @classmethod
    def path(cls):
        '''
        Example: CopyNumber/Gistic/FocalAmp/{cohort}/{gene}
        
        The returned path is a combination of the function name (CopyNumber), 
        static path fields (Gistic and FocalAmp which would be provided by the 
        static_path_fields function), and dynamic path fields (cohort and gene). 
        Dynamic path fields are defined by parameters that have param_type == 
        PARAMETER_TYPES.path. They must be included in the parameters list in
        the order in which you want them included in the URL. 
        '''
        path = cls.static_path()
        
        for parameter in cls.__path_parameters():
            path = os.path.join(path, "{%s}" % parameter.alias)
        return path
    
    @classmethod
    def static_path(cls):
        ''' Return the static portion of the path (empty string if none) '''
        path =""
        for static_path_field in cls.static_path_fields():
            path = os.path.join(path, static_path_field)

        path = os.path.join(path, cls.name())
        return path
    
    @classmethod
    def __path_parameters(cls):
        '''
        This returns parameters that have param_type == PARAMETER_TYPES.path 
        indicating that they are parsed from the path rather than being 
        provided by the request object (by calling request.args.getlist(alias)).
        '''
        return filter(lambda p: p.is_path(), cls.parameters())
    
    @staticmethod
    def static_path_fields():
        ''' 
        This allows for greater flexibility in defining an API function's path.
        These fields will be added to the path (separated by os.path.sep) after 
        the function's name and before any dynamic path fields (i.e. parameters 
        that have param_type=path).
        
        Example Path: /MeltingTemperatures/IDT/Foo/Bar/{name}/{sequence} in which 
        MeltingTemperatures is the API name, IDT is the function name, Foo and 
        Bar are the static path fields provided in this function call, and
        {name} and {sequence} are function parameters with param_type=path.
        '''
        return list()
    
    @classmethod
    def _parse_query_params(cls, query_params):
        '''
        Valid query_params are defined by parameters(). However, a user can 
        supply parameters not contained in this list. Therefore, invalid 
        parameters are discarded and a params_dict is populated only with those 
        parameters that are valid. Since format is a special required input 
        parameter for every API function, it is parsed and returned separately.
        
        Note that each parameter parses its own arguments. This allows it to
        set a default when the parameter isn't included in the API call, as well
        as format the input appropriately (string, float, int, date, etc.).  
        '''
        params_dict = dict()
        
        _format = FORMATS.json                               # @UndefinedVariable
        
        parameters = cls.parameters()
        
        for parameter in parameters:
            # Path parameters are parsed in _handle_path_fields()
            if not parameter.is_path():
                # query_params is a default_dict(list), so it returns an empty
                # list if this parameter was not provided - parse_args must
                # be called on every parameter to set its default value if one 
                # exists.
                args = parameter.parse_args(query_params[parameter.alias.lower()])
                if args:
                    if parameter == ParameterFactory.format():
                        _format = args[0]
                    else:
                        params_dict[parameter] = args
                
        return (params_dict, _format)
    
    @classmethod
    def _handle_path_fields(cls, path_fields, params_dict):
        ''' Populate params_dict with path fields. '''
        path_parameters = cls.__path_parameters()
        
        # If there are no path parameters, then there is nothing to do
        if len(path_parameters) < 1:
            return 
        
        # Path parameters must be included in the parameters list in the order 
        # in which they appear in the URL
        for i, path_parameter in enumerate(path_parameters):
            # Multiple comma separated arguments are permitted for a given 
            # path parameter, hence the split
            params_dict[path_parameter] = path_parameter.parse_args(path_fields[i].split(","))
            
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
    
    def __repr__(self):
        return pformat(self.getSwaggerDeclaration("resourcePath"))

    #===========================================================================
    # Swagger Methods
    #===========================================================================    
    @classmethod
    def getSwaggerDeclaration(cls, resourcePath):
        function               = dict()
        function["path"]       = os.path.join(resourcePath, cls.path())
        function["operations"] = list()
        
        operation               = dict()
        operation["method"]     = "GET"
        operation["summary"]    = cls.summary()
        operation["notes"]      = cls.notes()
        operation["type"]       = cls.type()
        operation["nickname"]   = cls.name()
        operation["parameters"] = list()
        operation["responseMessages"] = [{"code": 404, "message": "not found"}]
        for param in cls.parameters():
            operation["parameters"].append(param.getParameterDict())
        function["operations"].append(operation)
        return function