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

#=============================================================================
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

from src.apis.ApiConstants import PARAMETER_TYPES, FORMAT, FORMATS, SEQUENCE

#=============================================================================
# Class
#=============================================================================
class ParameterFactory(object):
    
    @classmethod
    def format(cls):
        ''' Create a parameter instance for defining the return format of the result.'''
        return CaseSensitiveStringParameter(FORMAT, "Format of result.",
                                         FORMATS._fields,
                                         default=FORMATS.json, # @UndefinedVariable
                                         allow_multiple=False)

    @classmethod
    def sequence(cls, required=False, allow_multiple=True,
                 param_type=PARAMETER_TYPES.query): # @UndefinedVariable
        ''' Create a parameter instance for specifying oligonucleotide sequence(s). '''
        return UpperCaseStringParameter(SEQUENCE, "Comma separated oligonucleotide sequence(s).",
                               param_type=param_type, required=required,
                               allow_multiple=allow_multiple)