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
    CHR_STOP, SNP_SEARCH_NAME, ARCHIVE, DYES, DEVICE, DATE
from src.DbConnector import DbConnector
from src.analyses.primary_analysis.PrimaryAnalysisUtils import get_archives, \
    get_dyes, get_devices

#=============================================================================
# Class
#=============================================================================
class ParameterFactory(object):
    
    _DB_CONNECTOR = DbConnector.Instance()
    
    @staticmethod
    def format():
        """ 
        Create a parameter instance for defining the return format of the 
        result.
        """
        return CaseSensitiveStringParameter(FORMAT, "Format of result.",
                                            FORMATS._fields,
                                            default=FORMATS.json, # @UndefinedVariable
                                            allow_multiple=False)

    @staticmethod
    def sequences(required=False, allow_multiple=True,
                  param_type=PARAMETER_TYPES.query):        # @UndefinedVariable
        """ Create a parameter instance for specifying sequence(s). """
        return CaseSensitiveStringParameter(SEQUENCE, "Comma separated " \
                                            "sequence(s). ",
                                            param_type=param_type, 
                                            required=required,
                                            allow_multiple=allow_multiple)

    @staticmethod
    def sequence_names(required=False, allow_multiple=True,
                       param_type=PARAMETER_TYPES.query):   # @UndefinedVariable
        """ Create a parameter instance for specifying sequence name(s). """
        return CaseSensitiveStringParameter(SEQUENCE_NAME, "Comma separated " \
                                            "sequence name(s). ",
                                            param_type=param_type, 
                                            required=required,
                                            allow_multiple=allow_multiple)

    @staticmethod
    def snpsearch_name(required=False, allow_multiple=True,
                       param_type=PARAMETER_TYPES.query):   # @UndefinedVariable
        """ Create a parameter instance for specifying chromosome number. """
        return CaseSensitiveStringParameter(SNP_SEARCH_NAME, "Comma " \
                                            "separated integers specifying " \
                                            "snp search name. ",
                                            required=required, 
                                            allow_multiple=allow_multiple,
                                            param_type=param_type)

    @staticmethod
    def chromosome_num(required=False, allow_multiple=True,
                       param_type=PARAMETER_TYPES.query):   # @UndefinedVariable
        """ Create a parameter instance for specifying chromosome number. """
        return CaseSensitiveStringParameter(CHR_NUM, "Comma separated " \
                                            "integers specifying chromosome " \
                                            "numbers. ", required=required, 
                                            allow_multiple=allow_multiple,
                                            param_type=param_type)

    @staticmethod
    def chromosome_start(required=False, allow_multiple=True, 
                         param_type=PARAMETER_TYPES.query): # @UndefinedVariable
        """ 
        Create a parameter instance for specifying start position of chromosome. 
        """
        return CaseSensitiveStringParameter(CHR_START, "Comma separated " \
                                            "integers specifying chromosome " \
                                            "start position. ", 
                                            required=required, 
                                            allow_multiple=allow_multiple, 
                                            param_type=param_type)

    @staticmethod
    def chromosome_stop(required=False, allow_multiple=True, 
                        param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        """ 
        Create a parameter instance for specifying end position of chromosome. 
        """
        return CaseSensitiveStringParameter(CHR_STOP, "Comma separated "\
                                            "integers  specifying chromosome " \
                                            "end position.", required=required, 
                                            allow_multiple=allow_multiple, 
                                            param_type=param_type)

    @staticmethod
    def probes(required=False, allow_multiple=True,
               param_type=PARAMETER_TYPES.query):           # @UndefinedVariable
        """ Create a parameter instance for specifying probe(s). """
        return UpperCaseStringParameter(PROBE, "Comma separated probe(s). ",
                                        param_type=param_type, 
                                        required=required,
                                        allow_multiple=allow_multiple)

    @staticmethod
    def boolean(name, description, default_value=True, required=False):
        """ Create a parameter instance for setting a flag to True or False."""
        return BooleanParameter(name, description, default=default_value, 
                                required=required)

    @staticmethod
    def integer(name, description, required=False, default=None,
                minimum=None, maximum=None):
        """ Create a parameter instance for specifying an integer. """
        return IntegerParameter(name, description, required=required,
                                allow_multiple=False, default=default,
                                minimum=minimum, maximum=maximum,
                                equality=EQUALITY.less_than_or_equal_to)  # @UndefinedVariable

    @staticmethod
    def file(description):
        """ Create a parameter instance for uploading a file."""
        return FileParameter(FILE, description)

    @staticmethod
    def filenames(required=True, allow_multiple=True,
                  param_type=PARAMETER_TYPES.query):        # @UndefinedVariable
        """ Create a parameter instance for specifying filename(s). """
        return CaseSensitiveStringParameter(FILENAMES, "Comma separated list " \
                                            "of target filename(s) to delete.",
                                            param_type=param_type, 
                                            required=required,
                                            allow_multiple=allow_multiple)
        
    @staticmethod
    def archive(required=True, param_type=PARAMETER_TYPES.query):  # @UndefinedVariable
        return CaseSensitiveStringParameter(ARCHIVE, "Archive directory name.",
                               required=required, 
                               allow_multiple=False,
                               enum=get_archives())

    @staticmethod
    def dyes(required=True, allow_multiple=True,
             param_type=PARAMETER_TYPES.query):             # @UndefinedVariable
        return CaseSensitiveStringParameter(DYES, "Comma separated list of " \
                                            "dye names.", required=required, 
                                            allow_multiple=allow_multiple,
                                            enum=get_dyes())

    @staticmethod
    def device(required=True, param_type=PARAMETER_TYPES.query): # @UndefinedVariable
        return CaseSensitiveStringParameter(DEVICE, "Device name.",
                                            required=required, 
                                            allow_multiple=False,
                                            enum=get_devices())
        
    @staticmethod
    def uuid(required=True, allow_multiple=True,
             param_type=PARAMETER_TYPES.query):             # @UndefinedVariable
        ''' Create a parameter instance for specifying uuid(s). '''
        return LowerCaseStringParameter(UUID, "Comma separated uuid(s). ",
                                        param_type=param_type, 
                                        required=required,
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
                               enum=cls._DB_CONNECTOR.distinct_sorted(collection, 
                                                                      UUID))    
    @staticmethod
    def lc_string(name, description, alias=None, required=True, 
                  allow_multiple=False, enum=None):
        return LowerCaseStringParameter(name, description,
                               alias=alias, required=required, 
                               allow_multiple=allow_multiple, enum=enum)

    @staticmethod
    def cs_string(name, description, alias=None, required=True, 
                  allow_multiple=False, enum=None):
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
        
    @classmethod
    def job_uuid(cls, collection):
        job_uuids = cls._DB_CONNECTOR.distinct(collection, UUID)
        return cls.lc_string(UUID, "Comma separated job UUID(s).", 
                             allow_multiple=True, enum=job_uuids)
        
    @classmethod
    def date(cls, required=True):
        ''' Create a parameter instance for selecting date(s). '''
        return DateParameter(DATE, "Run date of the form YYYY_MM_DD.", 
                             required=required)
