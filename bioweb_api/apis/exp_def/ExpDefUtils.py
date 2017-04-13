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
from bioweb_api.apis.ApiConstants import VARIANTS, UUID, ID, EXP_DEF, NAME, DYES, \
    TYPE

from gbutils.exp_def.exp_def_handler import ExpDefHandler
from secondary_analysis.genotyping.genotyper_utils import get_target_id

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
    for reference in experiment.references:
        for variant in reference.variants:
            variant_strings.append(get_target_id(reference, variant))
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
    columns[DYES]               = 1
    columns[TYPE]               = 1

    column_names = columns.keys()
    column_names.remove(ID)

    exp_defs = _DB_CONNECTOR.find(EXP_DEF_COLLECTION, {}, columns)
    APP_LOGGER.info('Retrieved %d experiment definitions.' \
                    % (len(exp_defs), ))
    return (exp_defs, column_names, None)

def update_experiment_definitions():
    """
    Update EXP_DEF_COLLECTION with new experiment definitions.
    """
    exp_def_fetcher = ExpDefHandler()

    db_uuids = set(_DB_CONNECTOR.distinct(EXP_DEF_COLLECTION, UUID))
    cur_uuids = set(exp_def_fetcher.experiment_uuids)
    new_uuids = cur_uuids - db_uuids
    obselete_uuids = db_uuids - cur_uuids
    new_exp_defs = list()
    for uuid in new_uuids:
        experiment = exp_def_fetcher.get_experiment_definition(uuid)
        if experiment is not None:
            update = {UUID: uuid, NAME: experiment.name, DYES: list(experiment.dyes),
                      TYPE: experiment.exp_type}
            if experiment.exp_type == 'HOTSPOT':
                update[VARIANTS] = format_variants(experiment)
            new_exp_defs.append(update)
    if new_exp_defs:
        _DB_CONNECTOR.insert(EXP_DEF_COLLECTION, new_exp_defs)

    if obselete_uuids:
        _DB_CONNECTOR.remove(EXP_DEF_COLLECTION,
                             {UUID: {"$in": list(obselete_uuids)}})
