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

from collections import namedtuple
from src import PORT, HOSTNAME

#=============================================================================
# RESTful location of services
#=============================================================================
API           = "api"
API_DOCS      = os.path.join(API, "api-docs")

API_BASE_URL       = "http://%s:%s/%s" % (HOSTNAME, PORT, API)
API_DOCS_BASE_URL  = "http://%s:%s/%s" % (HOSTNAME, PORT, API_DOCS)

#=============================================================================
# Swagger Constants 
#=============================================================================
SWAGGER_VERSION = "1.2"

# Swagger Primitives (type) table taken from 
# https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#431-primitives
#############################################################
# Common Name  #  type     #  format     #  Comments        #
#############################################################
# integer      #  integer  #  int32      #  signed 32 bits  #
# long         #  integer  #  int64      #  signed 64 bits  #
# float        #  number   #  float      #                  #
# double       #  number   #  double     #                  #  
# string       #  string   #             #                  #
# byte         #  string   #  byte       #                  #   
# boolean      #  boolean  #             #                  #   
# date         #  string   #  date       #                  #
# dateTime     #  string   #  date-time  #                  #
#############################################################

SWAGGER_TYPES_TUPLE = namedtuple('SwaggerTypes',
                                 [
                                  'integer',
                                  'number',
                                  'string',
                                  'boolean',
                                  'path',
                                  'File',
                                 ])
SWAGGER_TYPES = SWAGGER_TYPES_TUPLE(*SWAGGER_TYPES_TUPLE._fields)

SWAGGER_FORMATS_TUPLE = namedtuple('SwaggerFormats',
                                   [
                                    'int32',
                                    'int64',
                                    'float',
                                    'double',
                                    'date',
                                   ])
SWAGGER_FORMATS = SWAGGER_FORMATS_TUPLE(*SWAGGER_FORMATS_TUPLE._fields)

PARAMETER_TYPES_TUPLE = namedtuple('ParameterTypes',
                                   [
                                    'path',
                                    'query',
                                    'body',
                                    'header',
                                    'form',
                                   ])
PARAMETER_TYPES = PARAMETER_TYPES_TUPLE(*PARAMETER_TYPES_TUPLE._fields)

#=============================================================================
# Miscellaneous Constants 
#=============================================================================
PAGE          = "page"
FORMAT        = "format"
MISSING_VALUE = ""
SEQUENCE      = "sequence"
SEQUENCE_NAME = "sequence_name"
CHR_NUM       = "chr_num"
CHR_START     = "chr_start"
CHR_STOP      = "chr_stop"
SNP_SEARCH_NAME = 'snp_search_name'
PROBE         = "probe"
FILE          = "file"
FILENAME      = "filename"
FILEPATH      = "filepath"
FILENAMES     = "filenames"
TIME_FORMAT   = "%Y_%m_%d__%H_%M_%S"
ID            = "_id"
URL           = "url"
DATESTAMP     = "datestamp"
TYPE          = "type"
ERROR         = "error"
UUID          = "uuid"

#=============================================================================
# Miscellaneous namedtuples 
#=============================================================================
FORMATS_TUPLE = namedtuple('Formats',
                           [
                            'json',
                            'tsv',
                            'csv',
                           ])

FORMATS = FORMATS_TUPLE(*FORMATS_TUPLE._fields)

METHODS_TUPLE = namedtuple('Methods',
                           [
                            'POST',
                            'GET',
                            'PUT',
                            'DELETE',
                           ])

METHODS = METHODS_TUPLE(*METHODS_TUPLE._fields)

EQUALITY_TUPLE = namedtuple('Equality',
                            [
                             'greater_than',
                             'less_than',
                             'greater_than_or_equal_to',
                             'less_than_or_equal_to',
                            ])
EQUALITY = EQUALITY_TUPLE(*EQUALITY_TUPLE._fields)