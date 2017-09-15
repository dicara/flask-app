#!/usr/bin/env python
'''
Copyright 2017 Bio-Rad Laboratories, Inc.

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
@date:   Jan 5, 2017
'''

#=============================================================================
# Imports
#=============================================================================
import os
from datetime import datetime

from bioweb_api.apis.run_info.RunInfoUtils import get_run_info_path, read_report_file, get_hdf5_datasets, set_utag
from bioweb_api.DbConnector import DbConnector
from bioweb_api import RUN_REPORT_COLLECTION
from bioweb_api.apis.run_info.constants import DATETIME, RUN_REPORT_PATH, \
    IMAGE_STACKS, UTAG
from bioweb_api.utilities.logging_utilities import APP_LOGGER

#=============================================================================
# Private Static Variables
#=============================================================================
_DB_CONNECTOR = DbConnector.Instance()

def update_run_report(date_folders):
    """
    List of date folders in the form MM_DD_YY that you want to update.

    @param date_folders:
    """
    # fetch utags in run report collection
    db_utags = _DB_CONNECTOR.distinct(RUN_REPORT_COLLECTION, UTAG)

    if os.path.isdir(RUN_REPORT_PATH):

        reports = list()
        for folder in date_folders:
            path = os.path.join(RUN_REPORT_PATH, folder)
            if not os.path.isdir(path):
                continue

            date_obj = datetime.strptime(folder, '%m_%d_%y')

            for sf in os.listdir(path):
                report_file_path = get_run_info_path(path, sf)
                if report_file_path is None: continue

                utag = set_utag(date_obj, sf)
                if utag not in db_utags: # if not exists, need to insert to collection
                    log_data = read_report_file(report_file_path, date_obj, utag)
                    if log_data is None:
                        log_data = {DATETIME: date_obj, UTAG: utag}
                    if IMAGE_STACKS in log_data:
                        hdf5_datasets= get_hdf5_datasets(log_data, folder, sf)

                        log_data[IMAGE_STACKS].extend(hdf5_datasets)

                    reports.append(log_data)
                    print report_file_path
                else: # if exists, check HDF5 collection for new datasets
                    log_data = _DB_CONNECTOR.find_one(RUN_REPORT_COLLECTION, UTAG, utag)

                    # If previously a run report was not there or had wrong format,
                    # the mongo documents only has three fields, _id, datetime, and
                    # unique_tag. If this occurs, try reading the run report again.
                    if len(log_data.keys()) == 3:
                        log_data = read_report_file(report_file_path, date_obj, utag)

                    if log_data is not None and IMAGE_STACKS in log_data:
                        hdf5_datasets = get_hdf5_datasets(log_data, folder, sf)
                        exist_datasets = log_data[IMAGE_STACKS]

                        if set(hdf5_datasets) - set(exist_datasets):
                            updated_datasets = list(set(hdf5_datasets) | set(exist_datasets))
                            _DB_CONNECTOR.update(
                                    RUN_REPORT_COLLECTION,
                                    {UTAG: utag},
                                    {"$set": {IMAGE_STACKS: updated_datasets}})

        APP_LOGGER.info("Found %d run reports" % (len(reports)))
        if len(reports) > 0:
            # There is a possible race condition here. Ideally these operations
            # would be performed in concert atomically
            _DB_CONNECTOR.insert(RUN_REPORT_COLLECTION, reports)
 
#=============================================================================
# Main
#=============================================================================
if __name__ == '__main__':
    run_report_dirs = ['12_22_16', '12_23_16', '12_26_16', '12_27_16', '12_28_16', '12_29_16']
    update_run_report(run_report_dirs)