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
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
import os
import re
import shutil
import yaml

import h5py

from bioweb_api import ARCHIVES_PATH, RUN_REPORT_COLLECTION, RUN_REPORT_PATH, \
    HDF5_COLLECTION, ARCHIVES_COLLECTION, ARCHIVES_PATH
from bioweb_api.apis.ApiConstants import ID, UUID, HDF5_PATH, HDF5_DATASET, ARCHIVE
from bioweb_api.apis.run_info.constants import CARTRIDGE_SN_TXT, CHIP_SN_TXT, \
    CHIP_REVISION_TXT, DATETIME, DEVICE_NAME_TXT, EXIT_NOTES_TXT, \
    EXP_DEF_NAME_TXT, REAGENT_INFO_TXT, RUN_ID_TXT, RUN_DESCRIPTION_TXT, \
    RUN_REPORT_PATH, USER_TXT, RUN_REPORT_TXTFILE, RUN_REPORT_YAMLFILE, \
    TDI_STACKS_TXT, DEVICE_NAME, EXP_DEF_NAME, REAGENT_INFO, USER, \
    IMAGE_STACKS, RUN_DESCRIPTION, FILE_TYPE, UTAG, FA_UUID_MAP, SAMPLE_NAME, \
    CARTRIDGE_SN, CARTRIDGE_BC, CARTRIDGE_SN_OLD, RUN_ID, EXPERIMENT_PURPOSE, \
    PICO1_DYE
from bioweb_api.apis.run_info.model.run_report import RunReportWebUI, RunReportClientUI
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.DbConnector import DbConnector

#=============================================================================
# Private Static Variables
#=============================================================================
_DB_CONNECTOR = DbConnector.Instance()

ALLOWED_EXTENSIONS = ['.h5']

#=============================================================================
# RESTful location of services
#=============================================================================
def get_run_reports(cartridge_sn=None):
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
    columns[SAMPLE_NAME]        = 1
    columns[CARTRIDGE_SN]       = 1
    columns[CARTRIDGE_SN_OLD]   = 1
    columns[CARTRIDGE_BC]       = 1
    columns[IMAGE_STACKS]       = 1
    columns[FA_UUID_MAP]        = 1
    columns[EXPERIMENT_PURPOSE] = 1
    columns[PICO1_DYE]          = 1

    column_names = columns.keys()
    column_names.remove(ID)

    if cartridge_sn is None:
        reports = _DB_CONNECTOR.find(RUN_REPORT_COLLECTION,
                                        {UUID: {'$exists': True},
                                         DEVICE_NAME: {'$ne': ''},
                                         EXP_DEF_NAME: {'$ne': None},
                                         IMAGE_STACKS: {'$ne': None,
                                                        '$not': {'$size': 0}}},
                                     columns)
    else:
        reports = _DB_CONNECTOR.find(RUN_REPORT_COLLECTION,
                                        {UUID: {'$exists': True},
                                         DEVICE_NAME: {'$ne': ''},
                                         EXP_DEF_NAME: {'$ne': None},
                                         IMAGE_STACKS: {'$ne': None,
                                                        '$not': {'$size': 0}},
                                         '$or': [{CARTRIDGE_SN: cartridge_sn},
                                                 {CARTRIDGE_SN_OLD: cartridge_sn},
                                                 {'{0}.{1}'.format(CARTRIDGE_BC, 'serial_num'): cartridge_sn}]},
                                     columns)
    APP_LOGGER.info('Retrieved %d run reports with image stack(s)' \
                    % (len(reports), ))
    return (reports, column_names, None)

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
                    key, value = key.strip(), value.strip()
                    if key == USER_TXT and value:
                        data[key] = [user.strip() for user in value.split(',')]
                    elif key in [RUN_DESCRIPTION_TXT, EXIT_NOTES_TXT, TDI_STACKS_TXT]:
                        values = [value]
                        j = i + 1
                        while j < len(lines) and ':' not in lines[j]:
                            values.append(lines[j].strip())
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
        report_obj = RunReportWebUI.from_dict(**data)
        return report_obj.as_dict()
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
        data[USER] = [user.strip() for user in data[USER].split(',')]
        report_obj = RunReportWebUI.from_dict(**data)
        return report_obj.as_dict()
    except KeyError as e:
        APP_LOGGER.info("Try making RunReportClientUI object from YAML file, %s"
                        % report_file)
        try:
            report_obj = RunReportClientUI.from_dict(**data)
            return report_obj.as_dict()
        except:
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

def get_hdf5_datasets(log_data, date_folder, time_folder):
    """
    Fetch the HDF5 archives associated with a run report.

    @param log_data:            the document of run report yaml
    @param date_folder:         the date folder where run report lives
    @param time_folder:         the time sub folder where run report lives
    """
    run_id = log_data[RUN_ID]
    hdf5_paths = [os.path.join(RUN_REPORT_PATH, date_folder, time_folder, f + '.h5')
                  for f in [run_id, run_id + '-baseline']]
    all_datasets = set()

    for path in hdf5_paths:
        exist_records = _DB_CONNECTOR.find(HDF5_COLLECTION, {HDF5_PATH: path})
        if exist_records:
            all_datasets.update(set(r[HDF5_DATASET] for r in exist_records))
            continue

        new_records = list()
        try:
            with h5py.File(path) as h5_file:
                dataset_names = h5_file.keys()
            for dsname in dataset_names:
                if re.match(r'^\d{4}-\d{2}-\d{2}_\d{4}\.\d{2}', dsname):
                    new_records.append({
                        HDF5_PATH: path,
                        HDF5_DATASET: dsname,
                    })
        except:
            APP_LOGGER.exception('Unable to get dataset information from HDF5 file: %s' % path)

        if new_records:
            APP_LOGGER.info('Found %d datasets from HDF5 file: %s' % (len(new_records), path))
            _DB_CONNECTOR.insert(HDF5_COLLECTION, new_records)
            all_datasets.update(set(r[HDF5_DATASET] for r in new_records))

    return all_datasets


def update_image_stacks(log_data):
    """
    Check whether the image_stacks in a run report document exist in archive collection.
    If not, add them to database.
    """
    if log_data is None or IMAGE_STACKS not in log_data: return

    new_records = list()
    for image_stack in log_data[IMAGE_STACKS]:
        exist_record = _DB_CONNECTOR.find_one(ARCHIVES_COLLECTION, ARCHIVE, image_stack)
        if not exist_record and os.path.isdir(os.path.join(ARCHIVES_PATH, image_stack)):
            new_records.append({ARCHIVE: image_stack})

    if new_records:
        APP_LOGGER.info('Found %d image stacks: %s' % (len(new_records), new_records))
        _DB_CONNECTOR.insert(ARCHIVES_COLLECTION, new_records)


def update_run_reports(date_folders=None):
    '''
    Update the database with available run reports.  It is not an error
    if zero reports are available at this moment.

    @return True if database is successfully updated, False otherwise
    '''
    APP_LOGGER.info("Updating database with available run reports...")

    # fetch utags from run report collection
    db_utags = _DB_CONNECTOR.distinct(RUN_REPORT_COLLECTION, UTAG)

    if os.path.isdir(RUN_REPORT_PATH):
        if date_folders is None:
            try:
                latest_date = _DB_CONNECTOR.find_max(RUN_REPORT_COLLECTION, DATETIME)[DATETIME]
            except TypeError:
                latest_date = None

            def valid_date(folder):
                if latest_date is None: return True
                date_obj = datetime.strptime(folder, '%m_%d_%y')
                return date_obj >= latest_date - timedelta(days=6)

            date_folders = [folder for folder in os.listdir(RUN_REPORT_PATH)
                            if re.match('\d+_\d+_\d+', folder) and valid_date(folder)]

        date_folders = [os.path.join(RUN_REPORT_PATH, f) for f in date_folders]
        date_folders = [f for f in date_folders if os.path.isdir(f)]

        reports = list()
        for folder in date_folders:
            for sf in os.listdir(folder):
                report_file_path = get_run_info_path(folder, sf)
                if report_file_path is None: continue

                date_obj = datetime.strptime(os.path.basename(folder), '%m_%d_%y')
                utag = set_utag(date_obj, sf)
                if utag not in db_utags: # if not exists, need to insert to collection
                    log_data = read_report_file(report_file_path, date_obj, utag)
                    if log_data is None:
                        log_data = {DATETIME: date_obj, UTAG: utag}
                    if IMAGE_STACKS in log_data:
                        # add image stacks to archive collection
                        update_image_stacks(log_data)
                        # find HDF5 datasets and add them to HDF5 collection
                        hdf5_datasets = get_hdf5_datasets(log_data, folder, sf)
                        log_data[IMAGE_STACKS].extend(hdf5_datasets)

                    reports.append(log_data)
                else: # if exists, check HDF5 collection for new datasets
                    log_data = _DB_CONNECTOR.find_one(RUN_REPORT_COLLECTION, UTAG, utag)

                    # If previously a run report was not there or had wrong format,
                    # the mongo documents only has three fields, _id, datetime, and
                    # unique_tag. If this occurs, try reading the run report again.
                    if len(log_data.keys()) == 3:
                        log_data = read_report_file(report_file_path, date_obj, utag)
                        # add image stacks to archive collection
                        update_image_stacks(log_data)

                    if log_data is not None and IMAGE_STACKS in log_data:
                        # find HDF5 datasets and add new records to HDF5 collection
                        new_datasets = set(get_hdf5_datasets(log_data, folder, sf))
                        if new_datasets:
                            # exclude uploaded HDF5 datasets
                            exist_datasets = set([d for d in log_data[IMAGE_STACKS]
                                                  if isinstance(d, str) or isinstance(d, unicode)])
                            new_datasets = list(new_datasets - exist_datasets)
                            if new_datasets:
                                _DB_CONNECTOR.update(
                                        RUN_REPORT_COLLECTION,
                                        {UTAG: utag},
                                        {"$addToSet": {IMAGE_STACKS:
                                            {'$each': new_datasets}}})
                                APP_LOGGER.info('Updated run report utag=%s with %d datasets'
                                                % (utag, len(new_datasets)))

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

def get_datasets_from_files(filepaths):
    """
    Given the paths of HDF5/image stack files, return a tuple of a dictionary and a boolean.
    The dictionary has (filepath, set of datasets) as key, value. The boolean indicates
    whether any file contains dataset(s) with duplicate name(s).

    @param filepaths:           filepaths
    """
    if not filepaths: return dict(), False

    all_exist_datasets = _DB_CONNECTOR.distinct(HDF5_COLLECTION, HDF5_DATASET)
    fp_to_datasets = defaultdict(set)
    duplicate = False
    for fp in filepaths:
        if fp.lower().endswith('.h5'):
            try:
                with h5py.File(fp, 'r') as h5_file:
                    dataset_names = h5_file.keys()
                for dsname in dataset_names:
                    if not dsname.lower().startswith("laser_power"):
                        if dsname not in all_exist_datasets:
                            fp_to_datasets[fp].add(dsname)
                        else:
                            duplicate = True
            except:
                APP_LOGGER.exception('Unable to get dataset information from HDF5 file: %s' % fp)

    # check if there are duplicate datasets in fp_to_datasets
    unique_datasets = set()
    for datasets in fp_to_datasets.values():
        unique_datasets = unique_datasets | datasets
    if len(unique_datasets) < sum(len(d) for d in fp_to_datasets.values()):
        duplicate = True
    return fp_to_datasets, duplicate

def allowed_file(filepath):
    try:
        return os.path.isfile(filepath) and os.path.splitext(filepath)[1].lower() in ALLOWED_EXTENSIONS
    except:
        return False

if __name__ == '__main__':
    filepath = '/mnt/runs/run_analysis/modifiedH5/id1482786670-2016-12-26_1807.35-pilot7-filt.h5'
    uuid = '85feb5ad-0971-4743-a860-3303f276273a'
    add_datasets(filepath, uuid)