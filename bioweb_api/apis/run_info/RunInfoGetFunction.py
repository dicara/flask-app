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
@date:   Apr 11, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from datetime import timedelta, datetime

from bioweb_api import RUN_REPORT_COLLECTION
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.parameters.DateParameter import DateParameter
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.apis.ApiConstants import ID, UUID, RUN_REPORT
from bioweb_api.apis.run_info.RunInfoUtils import get_run_reports, update_run_reports

#=============================================================================
# Function
#=============================================================================
def daterange(start_date, end_date):
    """
    Generator function to iterate over a range of dates.
    """
    for i in xrange(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(i)

#=============================================================================
# Class
#=============================================================================
class RunInfoGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return RUN_REPORT

    @staticmethod
    def summary():
        return "Retrieve list of run reports."

    @staticmethod
    def notes():
        return "Returns a list of instrumental run reports that exist in " \
            "the run report datastore."

    @classmethod
    def parameters(cls):
        cls.refresh_parameter = ParameterFactory.boolean("refresh",
                                                         "Refresh available " \
                                                         "run reports.",
                                                         default_value=False)
        cls.cart_sn_parameter = ParameterFactory.cartridge_sn()
        cls.start_date = DateParameter("start", "Start date of the form YYYY_MM_DD.",
                                       allow_multiple=False,
                                       required=False)
        cls.end_date = DateParameter("end", "End date of the form YYYY_MM_DD.",
                                     allow_multiple=False,
                                     required=False)
        cls.uuid_parameter = ParameterFactory.uuid(required=False,
                                                   allow_multiple=False)
        parameters = [
                      cls.cart_sn_parameter,
                      cls.refresh_parameter,
                      cls.start_date,
                      cls.end_date,
                      cls.uuid_parameter,
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        uuid = None
        if cls.uuid_parameter in params_dict and \
            params_dict[cls.uuid_parameter][0]:
            uuid = params_dict[cls.uuid_parameter][0]

        # if uuid exists, return a single report with all fields
        if uuid is not None:
            report = cls._DB_CONNECTOR.find_one(RUN_REPORT_COLLECTION, UUID, uuid)
            if report is None:
                APP_LOGGER.debug("Run report uuid=%s does not exist." % uuid)
                return ([], [], None)

            del report[ID]
            return ([report], report.keys(), None)

        if cls.refresh_parameter in params_dict and \
           params_dict[cls.refresh_parameter][0]:
            if cls.start_date in params_dict and params_dict[cls.start_date][0]:
                start_date = params_dict[cls.start_date][0]
                if cls.end_date in params_dict and params_dict[cls.end_date][0]:
                    end_date = params_dict[cls.end_date][0]
                else:
                    end_date = datetime.now()
                # Old file location 05_10_17
                date_folders = [d.strftime("%m_%d_%y")
                                for d in daterange(start_date, end_date)]
                # New file location 2017_05/10
                date_folders.extend(d.strftime("%Y_%m/%d")
                                    for d in daterange(start_date, end_date))
            else:
                date_folders = None
            update_run_reports(date_folders)

        if cls.cart_sn_parameter in params_dict and \
            params_dict[cls.cart_sn_parameter][0]:
            return get_run_reports(params_dict[cls.cart_sn_parameter][0])
        else:
            return get_run_reports()

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = RunInfoGetFunction()
    print function
