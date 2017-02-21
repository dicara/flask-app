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



#=============================================================================
# Miscellaneous Constants
#=============================================================================
ABSORB           = "absorb"
AC_DOCUMENT      = 'ac_document'
ARCHIVE          = "archive"
ARCHIVES         = "archives"
AC_MODEL         = 'assay_caller_model'
CARTRIDGE_SN     = 'cart_serial'
CHR_NUM          = "chr_num"
CHR_START        = "chr_start"
CHR_STOP         = "chr_stop"
CTRL_FILTER      = 'ctrl_filter'
CTRL_THRESH      = "ctrl_thresh"
CONFIG           = "config"
CONFIG_URL       = "config_url"
CONTINUOUS_PHASE = 'continuous_phase'
DATE             = "date"
DATESTAMP        = "datestamp"
DEVICE           = "device"
DEVICES          = "devices"
DESCRIPTION      = "description"
DIFF_PARAMS      = "diff_params"
DYE              = "dye"
DYES             = "dyes"
DYES_LOTS        = "dyes_lots"
DROP_AVE_DIAMETER = "drop_ave_diameter"
DROP_STD_DIAMETER = "drop_std_diameter"
DYE_METRICS      = "dye_metrics"
EP_DOCUMENT      = "ep_document"
ERROR            = "error"
EXP_DEF          = "exp_def"
EXP_DEF_NAME     = EXP_DEF + "_name"
EXP_DEF_UUID     = EXP_DEF + "_uuid"
EXPLORATORY      = "EXPLORATORY"
FA_JOB_START_DATESTAMP = 'fa_job_start_datestamp'
FAIL             = "fail"
FAILED           = 'failed'
FILE             = "file"
FILENAME         = "filename"
FILENAMES        = "filenames"
FILEPATH         = "filepath"
FILTERED_DYES    = "filtered_dyes"
FINISH_DATESTAMP = "finish_datestamp"
FORMAT           = "format"
FULL_ANALYSIS_UUID = 'full_analysis_uuid'
GT_DOCUMENT      = 'gt_document'
HAM_NAME         = "ham_name"
HAM              = "ham"
HAM_UUID         = "ham_uuid"
HDF5_DATASET     = "hdf5_dataset"
HDF5_PATH        = "hdf5_path"
HOTSPOT          = "HOTSPOT"
ID               = "_id"
ID_DOCUMENT      = 'id_document'
IGNORE_LOWEST_BARCODE = 'ignore_lowest_barcode'
IS_HDF5          = 'is_hdf5'
IGNORED_DYES     = "ignored_dyes"
JOB_NAME         = "job_name"
JOB_NAME_DESC    = "Unique name to give this job."
JOB_TYPE_NAME    = "job_type"
KDE_PNG          = "kde_png"
KDE_PNG_URL      = "kde_png_url"
KDE_PNG_SUM      = "kde_png_sum"
KDE_PNG_SUM_URL  = "kde_png_sum_url"
MAJOR            = "major"
MAX_UNINJECTED_RATIO = "max_uninj_ratio"
MINOR            = "minor"
MISSING_VALUE    = ""
MIX_VOL          = "mix_vol"
MON1_NAME        = "mon1_name"
MONITOR1         = "monitor_cam_1"
MON2_NAME        = "mon2_name"
MONITOR2         = "monitor_cam_2"
NAME             = "name"
NBARCODES        = "nbarcodes"
NUM              = "num"
NUM_IMAGES       = "num_images"
OFFSETS          = "offsets"
PA_DATA_SOURCE   = 'pa_data_src'
PA_DOCUMENT      = 'pa_document'
PA_MIN_NUM_IMAGES = 10 # Minimum number of images required to run
PA_PROCESS_UUID  = "pa_process_uuid"
PAGE             = "page"
PASS             = "pass"
PDF              = "pdf"
PDF_URL          = "pdf_url"
PLATE_PLOT_URL   = "plate_plot_url"
PLOT             = "plot"
PLOT_URL         = "plot_url"
PNG              = "png"
PNG_URL          = "png_url"
PNG_SUM          = "png_sum"
PNG_SUM_URL      = "png_sum_url"
PROBE            = "probe"
PROBES           = "probes"
REPLAY           = "replay"
REPORT           = "report"
REPORT_URL       = "report_url"
RESULT           = "result"
RUN_ID           = "run_id"
RUNNING          = 'running'
REQUIRED_DROPS   = "required_drops"
SA_ASSAY_CALLER_UUID = "sa_assay_caller_uuid"
SA_GENOTYPER_UUID = "sa_genotyper_uuid"
SA_IDENTITY_UUID = "sa_identity_uuid"
SAMPLE_ID        = "sample_id"
SCATTER_PLOT     = "scatter_plot"
SCATTER_PLOT_URL = "scatter_plot_url"
SEQUENCE_NAME    = "sequence_name"
SEQUENCING       = "SEQUENCING"
SNP_SEARCH_NAME  = 'snp_search_name'
SQ_DOCUMENT      = "sq_document"
STACK_TYPE       = "stack_type"
START_DATESTAMP  = "start_datestamp"
STATUS           = "status"
STRICT           = "strict"
SUBMIT_DATESTAMP = "submit_datestamp"
SUBMITTED        = 'submitted'
SUCCEEDED        = 'succeeded'
TARGETS          = "targets"
TEMPORAL_PLOT_URL = 'temporal_plot_url'
TOTAL_VOL        = "total_vol"
TYPE             = "type"
URL              = "url"
UUID             = "uuid"
USE_IID          = "use_iid"
USE_PICO1_FILTER = 'use_pico1_filter'
VARIANT_MASK     = "variant_mask"
VARIANTS         = "variants"
VCF              = "vcf"
RUN_REPORT       = "run_report"
RUN_REPORT_FULL_ANALYSIS = "run_report/full_analysis"
UNIFIED_PDF      = "unified_pdf"
UNIFIED_PDF_URL  = "unified_pdf_url"

VALID_HAM_IMAGE_EXTENSIONS = ["bin", "png"]
VALID_HDF5_EXTENSIONS = {'.h5'}
VALID_MON_IMAGE_EXTENSIONS = ["jpg"]

#=============================================================================
# Secondary Analysis Constants
#=============================================================================
ASSAY_DYE          = "assay_dye"
AC_TRAINING_FACTOR = 'ac_training_factor'
COV_TYPE           = "cov_type"
DYE_LEVELS         = "dye_levels"
PICO1_DYE          = "pico1_dye"
PICO2_DYE          = "pico2_dye"
ID_TRAINING_FACTOR = "id_training_factor"
NUM_PROBES         = "num_probes"
OUTLIERS           = "outliers"
THRESHOLD          = "threshold"
UI_THRESHOLD       = "ui_threshold"
TRAINING_FACTOR    = "training_factor"


#=============================================================================
# Secondary Analysis Parameter Descriptions
#=============================================================================
IGNORE_LOWEST_BARCODE_DESCRIPTION = "Ignore the data from the barcode with " \
                                    "the lowest intenstisy"
NUM_PROBES_DESCRIPTION = "Number of unique probes used to determine size of " \
    "the required training set."
TRAINING_FACTOR_DESCRIPTION = "Used to compute the size of the training " \
    "set: size = num_probes*training_factor."
UI_THRESHOLD_DESCRIPTION = "Fiducial decomposition intensity threshold " \
    "below which a drop decomposition will be excluded from fiducial " \
    "pre-filter training."
REQ_DROPS_DESCRIPTION = "Number of drops to use in genotyping (0 to use all available)."
CTRL_FILTER_DESCRIPTION = "Use negative control drops to filter out false positives."
CTRL_THRESH_DESCRIPTION = "Maximum percent that negative control drops can " \
    "intersect positive population."
CONTINUOUS_PHASE_DESCRIPTION = "Check this if picoinjection was done with " \
                              "continuous phase instead of slugs."
MAX_UI_RATIO_DESCRIPTION = "The maximum allowed uninjected to injected ratio" \
                            "for the pico KDE filter."
ASSAY_CALLER_MODEL_DESCRIPTION = "The model used by assay caller to tag " \
                                 "positive/negative drops"
USE_PICO1_FILTER_DESCRIPTION = "Turn on/off picoinjection 1 filtering"

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
APPLICATION       = "application"
SEQUENCE          = "sequence"
COSMIC_ID         = "cosmic_id"
MUTATION_POSITION = "mutation_position"

PROBE_METADATA_HEADERS = [
                          PROBE_ID,
                          SEQUENCE,
                          COSMIC_ID,
                          MUTATION_POSITION,
                         ]


JOB_STATUS_TUPLE = namedtuple('JobStatus',
                              [
                               SUBMITTED,
                               RUNNING,
                               SUCCEEDED,
                               FAILED,
                              ])
JOB_STATUS = JOB_STATUS_TUPLE(*JOB_STATUS_TUPLE._fields)


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
                             'full_analysis',
                             'pa_process',
                             'pa_plots',
                             'pa_convert_images',
                             'sa_identity',
                             'sa_assay_calling',
                             'sa_genotyping',
                            ])
JOB_TYPE = JOB_TYPE_TUPLE(*JOB_TYPE_TUPLE._fields)
