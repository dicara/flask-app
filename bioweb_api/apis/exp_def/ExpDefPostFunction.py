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
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import UUID, NAME, VARIANTS
from bioweb_api import EXP_DEF_COLLECTION
from bioweb_api.apis.exp_def.ExpDefUtils import format_variants
from bioweb_api.utilities.io_utilities import make_clean_response

from primary_analysis.experiment.experiment_definitions import ExperimentDefinitions
from expdb.defs import HotspotExperiment

#=============================================================================
# Class
#=============================================================================
class ExpDefPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return 'refresh'

    @staticmethod
    def summary():
        return "Populating MongoDB exp_def collection with experiment \
                definitions in http://expdb."

    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        try:
            exp_defs = ExperimentDefinitions()

            new_exp_defs, num = list(), 0       # num: total number of inserts and updates
            for uuid in exp_defs.experiment_uuids:
                doc = cls._DB_CONNECTOR.find_one(EXP_DEF_COLLECTION, UUID, uuid)
                if doc is None:
                    name = exp_defs.get_experiment_name(uuid)
                    exp_def = exp_defs.get_experiment_defintion(uuid)
                    experiment = HotspotExperiment.from_dict(exp_def)
                    new_exp_defs.append({UUID: uuid,
                                         NAME: name,
                                         VARIANTS: format_variants(experiment)})
                else:
                    if NAME not in doc:
                        name = exp_defs.get_experiment_name(uuid)
                        update = { '$set': {NAME: name} }
                        cls._DB_CONNECTOR.update(EXP_DEF_COLLECTION,
                                                 {UUID: uuid},
                                                 update)
                        num += 1

            if new_exp_defs:
                cls._DB_CONNECTOR.insert(EXP_DEF_COLLECTION, new_exp_defs)
                num += len(new_exp_defs)

            return make_clean_response({'Number of Inserts/Updates': [num]}, 200)
        except Exception as e:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)


#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ExpDefPostFunction()
    print function
