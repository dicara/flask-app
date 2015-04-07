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
@date:   Mar 12, 2014
'''

# =============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.parameters.DateParameter import DateParameter
from bioweb_api.apis.parameters.BooleanParameter import BooleanParameter
from bioweb_api.apis.parameters.IntegerParameter import IntegerParameter
from bioweb_api.apis.parameters.FloatParameter import FloatParameter
from bioweb_api.apis.parameters.SortParameter import SortParameter
from bioweb_api.apis.parameters.UnmodifiedStringParameter import UnmodifiedStringParameter
from bioweb_api.apis.parameters.LowerCaseStringParameter import LowerCaseStringParameter
from bioweb_api.apis.parameters.UpperCaseStringParameter import UpperCaseStringParameter
from bioweb_api.apis.parameters.CaseSensitiveStringParameter import CaseSensitiveStringParameter
from bioweb_api.apis.parameters.FileParameter import FileParameter
from bioweb_api.apis.parameters.KeyValueParameter import KeyValueParameter
from bioweb_api.apis.ApiConstants import PARAMETER_TYPES, FORMAT, FORMATS, SEQUENCE, \
    SEQUENCE_NAME, PROBE, EQUALITY, FILE, FILENAMES, UUID, CHR_NUM, CHR_START, \
    CHR_STOP, SNP_SEARCH_NAME, ARCHIVE, DYES, DEVICE, DATE, DYE_LEVELS, EXP_DEF
from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.primary_analysis.PrimaryAnalysisUtils import get_archives, \
    get_dyes, get_devices

from primary_analysis.experiment.experiment_definitions import ExperimentDefinitions

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
    def archive(required=True):
        return CaseSensitiveStringParameter(ARCHIVE, "Archive directory name.",
                               required=required, 
                               allow_multiple=False,
                               enum=get_archives())

    @staticmethod
    def dyes(name=DYES, description=None, required=True, allow_multiple=True,
             default=None):
        if not description:
            description = "Comma separated list of dye names."
        return CaseSensitiveStringParameter(name, description, 
                                            required=required, 
                                            allow_multiple=allow_multiple,
                                            default=default,
                                            enum=get_dyes())

    @staticmethod
    def dye(name, description, required=False, default=None):
        return CaseSensitiveStringParameter(name, description, 
                                            required=required, 
                                            allow_multiple=False,
                                            enum=get_dyes(),
                                            default=default)

    @staticmethod
    def device(required=True):
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
                  allow_multiple=False, enum=None, default=None):
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
    def dye_levels(cls):
        keys_parameter   = cls.dyes()
        values_parameter = cls.integer("name", "description", minimum=1)
        description      = "Comma separated list of <dye>:<level> pairs."
        return KeyValueParameter(DYE_LEVELS, description, keys_parameter,
                                 values_parameter)
    
    @classmethod
    def job_uuid(cls, collection):
        job_uuids = cls._DB_CONNECTOR.distinct(collection, UUID)
        return cls.lc_string(UUID, "Comma separated job UUID(s).", 
                             allow_multiple=True, enum=job_uuids)
        
    @classmethod
    def date(cls, required=True, enum=None):
        ''' Create a parameter instance for selecting date(s). '''
        return DateParameter(DATE, "Run date of the form YYYY_MM_DD.", 
                             required=required, enum=enum)
        
    @classmethod
    def experiment_definition(cls):
        exp_defs = ExperimentDefinitions()
        return cls.cs_string(EXP_DEF, "Experiment definition.", required=True, 
                             enum=exp_defs.experiment_names)
