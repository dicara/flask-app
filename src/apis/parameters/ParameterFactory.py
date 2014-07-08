'''
Copyright (c) 2013 The Broad Institute, Inc. 
SOFTWARE COPYRIGHT NOTICE 
This software and its documentation are the copyright of the Broad Institute,
Inc. All rights are reserved.

This software is supplied without any warranty or guaranteed support
whatsoever. The Broad Institute is not responsible for its use, misuse, or
functionality.

@author: Dan DiCara
@date:   Mar 12, 2014
'''

# =============================================================================
# Imports
#=============================================================================
from src.apis.parameters.DateParameter import DateParameter
from src.apis.parameters.BooleanParameter import BooleanParameter
from src.apis.parameters.IntegerParameter import IntegerParameter
from src.apis.parameters.FloatParameter import FloatParameter
from src.apis.parameters.SortParameter import SortParameter
from src.apis.parameters.UnmodifiedStringParameter import UnmodifiedStringParameter
from src.apis.parameters.LowerCaseStringParameter import LowerCaseStringParameter
from src.apis.parameters.UpperCaseStringParameter import UpperCaseStringParameter
from src.apis.parameters.CaseSensitiveStringParameter import CaseSensitiveStringParameter
from src.apis.parameters.FileParameter import FileParameter
from src.apis.ApiConstants import PARAMETER_TYPES, FORMAT, FORMATS, SEQUENCE, \
    SEQUENCE_NAME, PROBE, EQUALITY, FILE, FILENAMES, UUID, CHR_NUM, CHR_START, \
    CHR_STOP, SNP_SEARCH_NAME
from src.DbConnector import DbConnector

#=============================================================================
# Class
#=============================================================================
class ParameterFactory(object):
    
    _DB_CONNECTOR = DbConnector.Instance()
    
    @classmethod
    def format(cls):
        """ Create a parameter instance for defining the return format of the result."""
        return CaseSensitiveStringParameter(FORMAT, "Format of result.",
                                            FORMATS._fields,
                                            default=FORMATS.json,  # @UndefinedVariable
                                            allow_multiple=False)

    @classmethod
    def sequences(cls, required=False, allow_multiple=True,
                  param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        """ Create a parameter instance for specifying sequence(s). """
        return CaseSensitiveStringParameter(SEQUENCE, "Comma separated sequence(s). ",
                                            param_type=param_type, required=required,
                                            allow_multiple=allow_multiple)

    @classmethod
    def sequence_names(cls, required=False, allow_multiple=True,
                       param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        """ Create a parameter instance for specifying sequence name(s). """
        return CaseSensitiveStringParameter(SEQUENCE_NAME, "Comma separated sequence name(s). ",
                                            param_type=param_type, required=required,
                                            allow_multiple=allow_multiple)

    @classmethod
    def snpsearch_name(cls, required=False, allow_multiple=True,
                       param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        """ Create a parameter instance for specifying chromosome number. """
        return CaseSensitiveStringParameter(SNP_SEARCH_NAME, "Comma separated integers specifying snp search name. ",
                                required=required, allow_multiple=allow_multiple,
                                param_type=param_type)

    @classmethod
    def chromosome_num(cls, required=False, allow_multiple=True,
                       param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        """ Create a parameter instance for specifying chromosome number. """
        return CaseSensitiveStringParameter(CHR_NUM, "Comma separated integers specifying chromosome numbers. ",
                                required=required, allow_multiple=allow_multiple,
                                param_type=param_type)

    @classmethod
    def chromosome_start(cls, required=False, allow_multiple=True, param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        """ Create a parameter instance for specifying start position of chromosome. """
        return CaseSensitiveStringParameter(CHR_START, "Comma separated integers specifying chromosome start position. ",
                                required=required, allow_multiple=allow_multiple, param_type=param_type)

    @classmethod
    def chromosome_stop(cls, required=False, allow_multiple=True, param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        """ Create a parameter instance for specifying end position of chromosome. """
        return CaseSensitiveStringParameter(CHR_STOP, "Comma separated integers  specifying chromosome end position. ",
                                required=required, allow_multiple=allow_multiple, param_type=param_type)

    @classmethod
    def probes(cls, required=False, allow_multiple=True,
               param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        """ Create a parameter instance for specifying probe(s). """
        return UpperCaseStringParameter(PROBE, "Comma separated probe(s). ",
                                        param_type=param_type, required=required,
                                        allow_multiple=allow_multiple)

    @classmethod
    def boolean(cls, name, description, default_value=True, required=False):
        """ Create a parameter instance for setting a flag to True or False."""
        return BooleanParameter(name, description, default=default_value, 
                                required=required)

    @classmethod
    def integer(cls, name, description, required=False, default=None,
                minimum=None, maximum=None):
        """ Create a parameter instance for specifying an integer. """
        return IntegerParameter(name, description, required=required,
                                allow_multiple=False, default=default,
                                minimum=minimum, maximum=maximum,
                                equality=EQUALITY.less_than_or_equal_to)  # @UndefinedVariable

    @classmethod
    def file(cls, description):
        """ Create a parameter instance for uploading a file."""
        return FileParameter(FILE, description)

    @classmethod
    def filenames(cls, required=True, allow_multiple=True,
                  param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        """ Create a parameter instance for specifying filename(s). """
        return CaseSensitiveStringParameter(FILENAMES, "Comma separated list of target filename(s) to delete. ",
                               param_type=param_type, required=required,
                               allow_multiple=allow_multiple)
        
    @classmethod
    def uuid(cls, required=True, allow_multiple=True,
             param_type=PARAMETER_TYPES.query): # @UndefinedVariable
        ''' Create a parameter instance for specifying uuid(s). '''
        return LowerCaseStringParameter(UUID, "Comma separated uuid(s). ",
                               param_type=param_type, required=required,
                               allow_multiple=allow_multiple)

    @classmethod
    def file_uuid(cls, alias, collection, required=True, allow_multiple=False):
        if allow_multiple:
            description = "Comma separated UUID(s)."
        else:
            description = "File UUID."
        return LowerCaseStringParameter(UUID, description,
                               alias=alias, required=required, 
                               allow_multiple=allow_multiple, 
                               enum=cls._DB_CONNECTOR.get_distinct(collection, 
                                                                   UUID))    

    @classmethod
    def lc_string(cls, name, description, alias=None, required=True, 
                  allow_multiple=False, enum=None):
        return LowerCaseStringParameter(name, description,
                               alias=alias, required=required, 
                               allow_multiple=allow_multiple, enum=enum)

    @classmethod
    def cs_string(cls, name, description, alias=None, required=True, 
                  allow_multiple=False):
        return CaseSensitiveStringParameter(name, description,
                               alias=alias, required=required, 
                               allow_multiple=allow_multiple)
    @staticmethod
    def float(name, description, alias=None, required=False, 
              allow_multiple=False, default=None, enum=None, minimum=None,
              maximum=None, equality=None):
        return FloatParameter(name, description, alias=alias, required=required,
                              allow_multiple=allow_multiple, default=None, 
                              enum=None, minimum=None, maximum=None, 
                              equality=None)
