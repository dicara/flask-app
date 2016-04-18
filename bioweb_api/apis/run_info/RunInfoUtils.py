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
from collections import OrderedDict
from datetime import datetime
import os
import re
import yaml

from bioweb_api import ARCHIVES_PATH, RUN_REPORT_COLLECTION
from bioweb_api.apis.ApiConstants import ID, UUID
from bioweb_api.apis.run_info.constants import CARTRIDGE_SN_TXT, CHIP_SN_TXT, \
    CHIP_REVISION_TXT, DATETIME, DEVICE_NAME_TXT, EXIT_NOTES_TXT, \
    EXP_DEF_NAME_TXT, REAGENT_INFO_TXT, RUN_ID_TXT, RUN_DESCRIPTION_TXT, \
    RUN_REPORT_PATH, USER_TXT, RUN_REPORT_TXTFILE, RUN_REPORT_YAMLFILE, \
    TDI_STACKS_TXT, DEVICE_NAME, EXP_DEF_NAME, REAGENT_INFO, USER, \
    IMAGE_STACKS, RUN_DESCRIPTION, FILE_TYPE
from bioweb_api.apis.run_info.model.run_report import RunReport
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.DbConnector import DbConnector

#=============================================================================
# Private Static Variables
#=============================================================================
_DB_CONNECTOR = DbConnector.Instance()

#=============================================================================
# RESTful location of services
#=============================================================================
def get_run_reports():
    """
    Retrieve a list of run reports.
    """
    columns                     = OrderedDict()
    columns[ID]                 = 0
    columns[UUID]               = 1
    columns[USER]               = 1
    columns[DATETIME]           = 1
    columns[DEVICE_NAME]        = 1
    columns[EXP_DEF_NAME]       = 1
    columns[RUN_DESCRIPTION]    = 1
    columns[IMAGE_STACKS]       = 1

    column_names = columns.keys()
    column_names.remove(ID)

    reports = _DB_CONNECTOR.find(RUN_REPORT_COLLECTION, {}, columns)

    return (reports, column_names, None)

strip_str = lambda str : str.rstrip().lstrip()

def read_report_file_txt(report_file, date_obj):
    """
    Extract information from a run_log.txt file, and returns a dictionary
    """
    try:
        with open(report_file, 'r') as rf:
            lines = rf.readlines()
        if not lines:
            raise Exception("The log file is empty.")
        data = {FILE_TYPE: 'txt', DATETIME: date_obj}
        for i, line in enumerate(lines):
            if line.strip():
                try:
                    key, value = line.split(':')
                    key, value = strip_str(key), strip_str(value)
                    if key == USER_TXT and value:
                        data[key] = [strip_str(user) for user in value.split(',')]
                    elif key in [RUN_DESCRIPTION_TXT, EXIT_NOTES_TXT, TDI_STACKS_TXT]:
                        values = [value]
                        j = i + 1
                        while j < len(lines) and ':' not in lines[j]:
                            values.append(strip_str(lines[j]))
                            j += 1
                        if key == TDI_STACKS_TXT:
                            regex = ARCHIVES_PATH + '/[^/]+'
                            data[key] = re.findall(regex, ''.join(values))
                        else:
                            data[key] = ', '.join(values)
                    elif value:
                        data[key] = value
                except:
                    continue
        report_obj = RunReport(**data)
        return report_obj.to_dict
    except IOError:
        raise Exception("Could not open the run log file.")

def read_report_file_yaml(report_file, date_obj):
    """
    Extract information from a run_log.yaml file, and returns a dictionary
    """
    try:
        with open(report_file, 'r') as rf:
            try:
                data = yaml.load(rf)
            except yaml.YAMLError as exc:
                raise Exception("YMALError %s received" % (exc, ))
        data[DATETIME] = date_obj
        data[FILE_TYPE] = 'yaml'
        data[USER] = [strip_str(user) for user in data[USER].split(',')]
        report_obj = RunReport(**data)
        return report_obj.to_dict
    except IOError:
        raise Exception("Could not open the run log file.")

def read_report_file(report_file, date_obj):
    """
    Extract information from a run log file in txt or yaml format
    """
    if not report_file:
        raise Exception("File pathname is an empty string.")

    basename = os.path.basename(report_file).lower()
    if basename.endswith('txt'):
        return read_report_file_txt(report_file, date_obj)
    elif basename.endswith('yaml'):
        return read_report_file_yaml(report_file, date_obj)
    else:
        raise Exception("File extension must be txt or yaml.")

def update_run_reports():
    '''
    Update the database with available run reports.  It is not an error
    if zero reports are available at this moment.

    @return True if database is successfully updated, False otherwise
    '''
    APP_LOGGER.info("Updating database with available run reports...")
    _DB_CONNECTOR.remove(RUN_REPORT_COLLECTION, {})

    if os.path.isdir(RUN_REPORT_PATH):
        date_folders = [folder for folder in os.listdir(RUN_REPORT_PATH)
                        if os.path.isdir(os.path.join(RUN_REPORT_PATH, folder))
                        and re.match('\d+_\d+_\d+', folder)]

        reports = list()
        for folder in date_folders:
            path = os.path.join(RUN_REPORT_PATH, folder)
            date_obj = datetime.strptime(folder, '%m_%d_%y')

            report_files = [os.path.join(path, sub_folder, run_info_file)
                            for sub_folder in os.listdir(path)
                            for run_info_file in [RUN_REPORT_TXTFILE, RUN_REPORT_YAMLFILE]
                            if os.path.isfile(os.path.join(path, sub_folder,
                                                    run_info_file))]

            reports += [read_report_file(report_file, date_obj)
                        for report_file in report_files
                        if read_report_file(report_file, date_obj) is not None]

        APP_LOGGER.info("Found %d run reports" % (len(reports)))
        if len(reports) > 0:
            # There is a possible race condition here. Ideally these operations
            # would be performed in concert atomically
            _DB_CONNECTOR.insert(RUN_REPORT_COLLECTION, reports)
    else:
        APP_LOGGER.error("Couldn't locate run report path '%s', to update database." % ARCHIVES_PATH)
        return False

    APP_LOGGER.info("Database successfully updated with available run reports.")
    return True
