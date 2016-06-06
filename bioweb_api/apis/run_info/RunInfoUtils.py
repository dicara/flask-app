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
    IMAGE_STACKS, RUN_DESCRIPTION, FILE_TYPE, UTAG, FA_UUID_MAP
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
    columns[FA_UUID_MAP]        = 1

    column_names = columns.keys()
    column_names.remove(ID)

    reports = _DB_CONNECTOR.find(RUN_REPORT_COLLECTION, {}, columns)

    return (reports, column_names, None)

strip_str = lambda str : str.rstrip().lstrip()

def set_utag(date_obj, sf):
    date_str = "%s_%s_%s" % (date_obj.year, date_obj.month, date_obj.day)
    return '_'.join([date_str, sf])

def read_report_file_txt(report_file, date_obj, utag):
    """
    Extract information from a run_log.txt file, and returns a dictionary
    """
    try:
        with open(report_file, 'r') as rf:
            lines = rf.readlines()
        if not lines:
            APP_LOGGER.error("The log file, %s, is empty." % report_file)
            return None
        data = {FILE_TYPE: 'txt', DATETIME: date_obj, UTAG: utag}
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
    except IOError as e:
        APP_LOGGER.error("IOError raised: %s" % e)
        return None

def read_report_file_yaml(report_file, date_obj, utag):
    """
    Extract information from a run_log.yaml file, and returns a dictionary
    """
    try:
        with open(report_file, 'r') as rf:
            try:
                data = yaml.load(rf)
            except yaml.YAMLError as exc:
                APP_LOGGER.error("YMALError %s received" % exc)
                return None
        if not data:
            APP_LOGGER.debug("YAML file, %s, is empty." % report_file)
            return None
        data[DATETIME] = date_obj
        data[FILE_TYPE] = 'yaml'
        data[UTAG] = utag
        data[USER] = [strip_str(user) for user in data[USER].split(',')]
        report_obj = RunReport(**data)
        return report_obj.to_dict
    except KeyError as e:
        APP_LOGGER.error("KeyError raised: %s" % e)
        return None
    except IOError as e:
        APP_LOGGER.error("IOError raised: %s" % e)
        return None

def read_report_file(report_file, date_obj, utag):
    """
    Extract information from a run log file in txt or yaml format
    The path of a sample run_info file is:
    /mnt/runs/run_reprots/04_05_16/Tue05_1424_beta17/run_info.txt
    date_obj is based on 04_05_16
    utag is 2016_04_05_Tue05_1424_beta17
    """
    if not report_file:
        APP_LOGGER.debug("File pathname, %s, is an empty string." % report_file)
        return None

    basename = os.path.basename(report_file).lower()
    if basename.endswith('txt'):
        return read_report_file_txt(report_file, date_obj, utag)
    elif basename.endswith('yaml'):
        return read_report_file_yaml(report_file, date_obj, utag)
    else:
        APP_LOGGER.debug("File extension must be txt or yaml.")
        return None

def get_run_info_path(path, sub_folder):
    for f in [RUN_REPORT_TXTFILE, RUN_REPORT_YAMLFILE]:
        run_info_path = os.path.join(path, sub_folder, f)
        if os.path.isfile(run_info_path):
            return run_info_path
    return None

def update_run_reports():
    '''
    Update the database with available run reports.  It is not an error
    if zero reports are available at this moment.

    @return True if database is successfully updated, False otherwise
    '''
    APP_LOGGER.info("Updating database with available run reports...")

    if os.path.isdir(RUN_REPORT_PATH):
        date_folders = [folder for folder in os.listdir(RUN_REPORT_PATH)
                        if os.path.isdir(os.path.join(RUN_REPORT_PATH, folder))
                        and re.match('\d+_\d+_\d+', folder)]

        reports = list()
        for folder in date_folders:
            path = os.path.join(RUN_REPORT_PATH, folder)
            date_obj = datetime.strptime(folder, '%m_%d_%y')

            report_files_utags = [(get_run_info_path(path, sf), sf)
                                   for sf in os.listdir(path)]
            for sf in os.listdir(path):
                report_file_path = get_run_info_path(path, sf)
                if report_file_path is None: continue

                utag = set_utag(date_obj, sf)
                doc = _DB_CONNECTOR.find_one(RUN_REPORT_COLLECTION, UTAG, utag)
                if doc is None: # if not exist, need to insert to collection
                    log_data = read_report_file(report_file_path, date_obj, utag)
                    if log_data is not None:
                        reports.append(log_data)

        reports = [r for r in reports if r is not None]

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
