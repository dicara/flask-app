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

from collections import namedtuple, OrderedDict
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

JOB_STATUS_TUPLE = namedtuple('JobStatus',
                              [
                               'submitted',
                               'running',
                               'succeeded',
                               'failed',
                              ])
JOB_STATUS = JOB_STATUS_TUPLE(*JOB_STATUS_TUPLE._fields)

#=============================================================================
# Miscellaneous Constants 
#=============================================================================
PAGE             = "page"
FORMAT           = "format"
MISSING_VALUE    = ""
SEQUENCE_NAME    = "sequence_name"
CHR_NUM          = "chr_num"
CHR_START        = "chr_start"
CHR_STOP         = "chr_stop"
SNP_SEARCH_NAME  = 'snp_search_name'
PROBE            = "probe"
FILE             = "file"
FILENAME         = "filename"
FILEPATH         = "filepath"
FILENAMES        = "filenames"
ARCHIVES         = "archives"
ARCHIVE          = "archive"
TIME_FORMAT      = "%Y_%m_%d__%H_%M_%S"
ID               = "_id"
URL              = "url"
CONFIG_URL       = "config_url"
DATE             = "date"
DATESTAMP        = "datestamp"
SUBMIT_DATESTAMP = "submit_datestamp"
START_DATESTAMP  = "start_datestamp"
FINISH_DATESTAMP = "finish_datestamp"
TYPE             = "type"
ERROR            = "error"
UUID             = "uuid"
STATUS           = "status"
JOB_NAME         = "job_name"
PROBES           = "probes"
TARGETS          = "targets"
ABSORB           = "absorb"
NUM              = "num"
RESULT           = "result"
DYES             = "dyes"
DYE              = "dye"
DEVICES          = "devices"
DEVICE           = "device"
JOB_TYPE_NAME    = "job_type"
CONFIG           = "config"
RUN_ID           = "run_id"
SAMPLE_ID        = "sample_id"
PASS             = "pass"
FAIL             = "fail"

#=============================================================================
# Probe Experiment Constants
#=============================================================================
PROBE_ID         = "probe_id"
FAM              = "fam"
FAM_SD           = "fam_sd"
JOE              = "joe"
JOE_SD           = "joe_sd"
OBSERVED_RESULT  = "observed_result"
EXPECTED_RESULT  = "expected_result"

PROBE_EXPERIMENT_HEADERS                  = OrderedDict()
PROBE_EXPERIMENT_HEADERS[PROBE_ID]        = lambda x: x
PROBE_EXPERIMENT_HEADERS[FAM]             = lambda x: float(x)
PROBE_EXPERIMENT_HEADERS[FAM_SD]          = lambda x: float(x)
PROBE_EXPERIMENT_HEADERS[JOE]             = lambda x: float(x)
PROBE_EXPERIMENT_HEADERS[JOE_SD]          = lambda x: float(x)
PROBE_EXPERIMENT_HEADERS[OBSERVED_RESULT] = lambda x: x
PROBE_EXPERIMENT_HEADERS[EXPECTED_RESULT] = lambda x: x

# Metadata
APPLICATION       = "application"
SEQUENCE          = "sequence"
COSMIC_ID         = "cosmic_id"
MUTATION_POSITION = "mutation_position"

PROBE_METADATA_HEADERS = [
                          PROBE_ID,
                          APPLICATION,
                          SEQUENCE,
                          COSMIC_ID,
                          MUTATION_POSITION,
                         ]

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

JOB_TYPE_TUPLE = namedtuple('JobType',
                            [
                             'absorption',
                             'pa_process',
                            ])
JOB_TYPE = JOB_TYPE_TUPLE(*JOB_TYPE_TUPLE._fields)