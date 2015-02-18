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
from bioweb_api import PORT, HOSTNAME

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
ABSORB           = "absorb"
ARCHIVE          = "archive"
ARCHIVES         = "archives"
CHR_NUM          = "chr_num"
CHR_START        = "chr_start"
CHR_STOP         = "chr_stop"
CONFIG           = "config"
CONFIG_URL       = "config_url"
DATE             = "date"
DATESTAMP        = "datestamp"
DEVICE           = "device"
DEVICES          = "devices"
DYE              = "dye"
DYES             = "dyes"
ERROR            = "error"
FAIL             = "fail"
FILE             = "file"
FILENAME         = "filename"
FILENAMES        = "filenames"
FILEPATH         = "filepath"
FINISH_DATESTAMP = "finish_datestamp"
FORMAT           = "format"
ID               = "_id"
JOB_NAME         = "job_name"
JOB_TYPE_NAME    = "job_type"
KDE_PLOT         = "kde_plot"
KDE_PLOT_URL     = "kde_plot_url"
MISSING_VALUE    = ""
NUM              = "num"
OFFSETS          = "offsets"          
PA_PROCESS_UUID  = "pa_process_uuid"
PAGE             = "page"
PASS             = "pass"
PLOT             = "plot"
PLOT_URL         = "plot_url"
PROBE            = "probe"
PROBES           = "probes"
RESULT           = "result"
RUN_ID           = "run_id"
SAMPLE_ID        = "sample_id"
SCATTER_PLOT     = "scatter_plot"
SCATTER_PLOT_URL = "scatter_plot_url"
SEQUENCE_NAME    = "sequence_name"
SNP_SEARCH_NAME  = 'snp_search_name'
START_DATESTAMP  = "start_datestamp"
STATUS           = "status"
STRICT           = "strict"
SUBMIT_DATESTAMP = "submit_datestamp"
TARGETS          = "targets"
TYPE             = "type"
URL              = "url"
UUID             = "uuid"

VALID_IMAGE_EXTENSIONS = ["bin", "png"] 

#=============================================================================
# Secondary Analysis Constants
#=============================================================================
ASSAY_DYE       = "assay_dye"
DYE_LEVELS      = "dye_levels"
FIDUCIAL_DYE    = "fiducial_dye"
NUM_PROBES      = "num_probes"
TRAINING_FACTOR = "training_factor"
THRESHOLD       = "threshold"
OUTLIERS        = "outliers"
COV_TYPE        = "cov_type"

#=============================================================================
# Probe Experiment Constants
#=============================================================================
PROBE_ID         = "probe_id"
FAM              = "fam"
JOE              = "joe"
SIGNAL           = "signal"
OBSERVED_RESULT  = "observed_result"
EXPECTED_RESULT  = "expected_result"

PROBE_EXPERIMENT_HEADERS                  = OrderedDict()
PROBE_EXPERIMENT_HEADERS[PROBE_ID]        = lambda x: x
PROBE_EXPERIMENT_HEADERS[FAM]             = lambda x: float(x)
PROBE_EXPERIMENT_HEADERS[JOE]             = lambda x: float(x)
PROBE_EXPERIMENT_HEADERS[SIGNAL]          = lambda x: float(x)
PROBE_EXPERIMENT_HEADERS[OBSERVED_RESULT] = lambda x: x
PROBE_EXPERIMENT_HEADERS[EXPECTED_RESULT] = lambda x: x

# Metadata
APPLICATION       = "Application"
SEQUENCE          = "sequence"
COSMIC_ID         = "cosmic_id"
MUTATION_POSITION = "mutation_position"

PROBE_METADATA_HEADERS = [
                          PROBE_ID,
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
                             'pa_plots',
                             'pa_convert_images',
                             'sa_identity',
                             'sa_assay_calling',
                            ])
JOB_TYPE = JOB_TYPE_TUPLE(*JOB_TYPE_TUPLE._fields)