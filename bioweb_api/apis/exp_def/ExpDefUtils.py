'''
Copyright 2016 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Yuewei Sheng
@date:   August 22, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from collections import OrderedDict

from bioweb_api import EXP_DEF_COLLECTION
from bioweb_api.DbConnector import DbConnector
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.ApiConstants import VARIANTS, UUID, ID, EXP_DEF, NAME

#=============================================================================
# Private Static Variables
#=============================================================================
_DB_CONNECTOR = DbConnector.Instance()

#=============================================================================
# Functions
#=============================================================================
def format_variants(experiment):
    """
    Return a list of formatted string of variants in an experiment definition.
    """
    variant_strings = list()
    for variant in experiment.variants:
        loc = variant.coding_pos if variant.coding_pos is not None else variant.location
        variant_strings.append('{0} {1}{2}>{3}'.format(variant.reference,
                                                       loc,
                                                       variant.expected,
                                                       variant.variation))
    return variant_strings


def get_experiment_defintions():
    """
    Retrieve experiment definition from EXP_DEF_COLLECTION.
    """
    columns                     = OrderedDict()
    columns[ID]                 = 0
    columns[UUID]               = 1
    columns[NAME]               = 1
    columns[VARIANTS]           = 1

    column_names = columns.keys()
    column_names.remove(ID)

    exp_defs = _DB_CONNECTOR.find(EXP_DEF_COLLECTION, {}, columns)
    APP_LOGGER.info('Retrieved %d experiment definitions.' \
                    % (len(exp_defs), ))
    return (exp_defs, column_names, None)
