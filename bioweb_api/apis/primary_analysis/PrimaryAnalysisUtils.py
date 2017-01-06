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
@date:   Jul 23, 2014
'''

#=============================================================================
# Imports
#=============================================================================
import os
import re
import sys
import shutil

import h5py

from bioweb_api import ARCHIVES_PATH, TMP_PATH, DYES_COLLECTION, \
    DEVICES_COLLECTION, ARCHIVES_COLLECTION, PROBE_METADATA_COLLECTION, \
    HDF5_COLLECTION, RUN_REPORT_PATH
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.utilities import io_utilities
from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.ApiConstants import ARCHIVE, DYE, DEVICE, ID, \
    VALID_HAM_IMAGE_EXTENSIONS, APPLICATION, HDF5_PATH, HDF5_DATASET, \
    PA_MIN_NUM_IMAGES, VALID_HDF5_EXTENSIONS
from primary_analysis.dye_datastore import Datastore
from primary_analysis.cmds.process import process
from primary_analysis.pa_images import convert_images

#=============================================================================
# Private Static Variables
#=============================================================================
_DB_CONNECTOR = DbConnector.Instance()
_DATASTORE    = Datastore()

#=============================================================================
# RESTful location of services
#=============================================================================
def get_archives():
    '''
    Return a listing of the archives directory.
    '''
    return _DB_CONNECTOR.distinct_sorted(ARCHIVES_COLLECTION, ARCHIVE)

def get_hdf5s():
    '''
    Return a listing of the hdf5 file and dataset.
    '''
    documents = _DB_CONNECTOR.find(HDF5_COLLECTION, None, [HDF5_PATH, HDF5_DATASET])
    for doc in documents:
        if ID in doc:
            del doc[ID]
    return documents

def get_hdf5_dataset_names():
    '''
    Return a listing of the hdf5 dataset names.
    '''
    return _DB_CONNECTOR.distinct_sorted(HDF5_COLLECTION, HDF5_DATASET)

def is_hdf5_archive(archive_name):
    if archive_name in get_hdf5_dataset_names():
        return True
    else:
        return False

def is_image_archive(archive_name):
    # remove separator from front and back of archive name
    path = archive_name.lstrip(os.sep)
    root_archive_name = path[:path.index(os.sep)] if os.sep in path else path
    if root_archive_name in get_archives():
        return True
    else:
        return False

def get_hdf5_dataset_path(dataset_name):
    documents = _DB_CONNECTOR.find(HDF5_COLLECTION, {HDF5_DATASET: dataset_name}, [HDF5_PATH])
    return documents[0][HDF5_PATH]

def parse_pa_data_src(pa_data_src_name):
    """
    Determine primary analysis data source type (HDF5 or image stack) and return
    a list containing the archive paths and dataset names

    @param pa_data_src_name:    String, name of data source, could be either
                                the HDF5 dataset name or a folder name containing
                                image stacks
    @return:                    A list of tuples, each tuple contains the primary analysis
                                datasource name and a bool indicating whether or not it is HDF5.
    """
    # archives is a list of tuples, each tuple contains the path and the dataset name
    archives = list()
    if is_hdf5_archive(pa_data_src_name):
        archives.append((pa_data_src_name, True))
        APP_LOGGER.info('%s is an HDF5 file.' % pa_data_src_name)
    elif is_image_archive(pa_data_src_name):
        image_archive_paths = io_utilities.get_archive_dirs(pa_data_src_name,
                                    min_num_images=PA_MIN_NUM_IMAGES)
        for img_src_name in image_archive_paths:
            archives.append((img_src_name, False,))
        APP_LOGGER.info('%s is an image stack.' % pa_data_src_name)
    else:
        raise Exception('Unable to determine if %s is an image stack or HDF5 file.' %
                        pa_data_src_name)

    return archives

def get_dyes():
    '''
    Retrieve a list of available dye names.
    '''
    return _DB_CONNECTOR.distinct_sorted(DYES_COLLECTION, DYE)

def get_devices():
    '''
    Retrieve a list of available devices.
    '''
    return _DB_CONNECTOR.distinct_sorted(DEVICES_COLLECTION, DEVICE)

def get_applications():
    '''
    Retrieve a list of available probe design experiment applications.
    '''
    return _DB_CONNECTOR.distinct_sorted(PROBE_METADATA_COLLECTION, APPLICATION)

def update_archives():
    '''
    Update the database with available primary analysis archives.  It is not
    an error if zero archives are available at this moment.
    
    @return True if database is successfully updated, False otherwise
    '''
    APP_LOGGER.info("Updating database with available archives...")
    _DB_CONNECTOR.remove(ARCHIVES_COLLECTION, {})
    if os.path.isdir(ARCHIVES_PATH):

        
        # Remove archives named similarly (same name, different capitalization)
        archives    = os.listdir(ARCHIVES_PATH)
        lc_archives = [a.lower() for a in archives]
        dups        = set(a for a in archives if lc_archives.count(a.lower()) > 1)
        archives    = [a for a in archives if a not in dups]
        archives    = [x for x in archives 
                       if os.path.isdir(os.path.join(ARCHIVES_PATH,x))]
        records     = [{ARCHIVE: archive} for archive in archives]
        
        APP_LOGGER.info("Found %d archives" % (len(archives)))
        if len(records) > 0:
            # There is a possible race condition here. Ideally these operations 
            # would be performed in concert atomically
            _DB_CONNECTOR.insert(ARCHIVES_COLLECTION, records)
    else:
        APP_LOGGER.error("Couldn't locate archives path '%s', to update database." % ARCHIVES_PATH)
        return False

    APP_LOGGER.info("Database successfully updated with available archives.")
    return True

def update_hdf5s():
    APP_LOGGER.info("Updating database with available HDF5 files...")

    # check if run report path exists
    if not os.path.isdir(RUN_REPORT_PATH):
        APP_LOGGER.error("Couldn't locate run report path '%s', to update database." % RUN_REPORT_PATH)
        return False

    # find new hdf5 files, using nested listdirs, way faster than glob, os.walk, or scandir
    # only search two subdirectories within the run report folder
    # assumes each the hdf5 file is in a subfolder in the run report folder
    database_paths = set(_DB_CONNECTOR.distinct_sorted(HDF5_COLLECTION, HDF5_PATH))
    current_paths = set()
    for par_ in os.listdir(RUN_REPORT_PATH):
        report_dir = os.path.join(RUN_REPORT_PATH, par_)
        if os.path.isdir(report_dir):
            for sub_ in os.listdir(report_dir):
                subdir = os.path.join(report_dir, sub_)
                if os.path.isdir(subdir):
                    hdf5s = [f for f in os.listdir(subdir) if os.path.splitext(f)[-1] in VALID_HDF5_EXTENSIONS]
                    hdf5_paths = [os.path.join(subdir, f) for f in hdf5s]
                    current_paths.update(hdf5_paths)

    # remove obsolete paths
    obsolete_paths = list(database_paths - current_paths)
    _DB_CONNECTOR.remove(HDF5_COLLECTION, {HDF5_PATH: {'$in': obsolete_paths}})

    # update database with any new files
    new_hdf5_paths = current_paths - database_paths
    new_records = list()
    for hdf5_path in new_hdf5_paths:
        try:
            with h5py.File(hdf5_path) as h5_file:
                dataset_names = h5_file.keys()
            for dsname in dataset_names:
                if re.match(r'^\d{4}-\d{2}-\d{2}_\d{4}\.\d{2}', dsname):
                    new_records.append({
                        HDF5_PATH: hdf5_path,
                        HDF5_DATASET: dsname,
                    })
        except:
            APP_LOGGER.exception('Unable to get dataset information from HDF5 file: %s' % hdf5_path)

    if new_records:
        # There is a possible race condition here. Ideally these operations
        # would be performed in concert atomically
        _DB_CONNECTOR.insert(HDF5_COLLECTION, new_records)
        APP_LOGGER.info('Updated database with %s new HDF5 files' % len(new_records))
    else:
        APP_LOGGER.info('Unable to find any new HDF5 files')

    return True

def update_dyes():
    '''
    Update the database with available dyes.
    
    @return True if database is successfully updated, False otherwise
    '''
    APP_LOGGER.info("Updating database with available dyes...")
    try:
        records = [{DYE: dye} for dye in _DATASTORE.dyes()]
        
        assert len(records) > 0, "Internal error: No dyes found"
        # There is a possible race condition here. Ideally these operations 
        # would be performed in concert atomically
        _DB_CONNECTOR.remove(DYES_COLLECTION, {})
        _DB_CONNECTOR.insert(DYES_COLLECTION, records)
    except:
        APP_LOGGER.info("Failed to update database with available dyes: %s", 
                        str(sys.exc_info()))
        raise
    
    APP_LOGGER.info("Database successfully updated with available dyes.")
    return True

def update_devices():
    '''
    Update the database with available devices.
    
    @return True if database is successfully updated, False otherwise
    '''
    APP_LOGGER.info("Updating database with available devices...")
    try:
        # devices are printed to stderr 
        records   = [{DEVICE: device} for device in _DATASTORE.devices()]
        
        assert len(records) > 0, "Internal error: No devices found"
        # There is a possible race condition here. Ideally these operations 
        # would be performed in concert atomically
        _DB_CONNECTOR.remove(DEVICES_COLLECTION, {})
        _DB_CONNECTOR.insert(DEVICES_COLLECTION, records)
    except:
        APP_LOGGER.info("Failed to update database with available devices: %s", 
                        str(sys.exc_info()))
        raise
    
    APP_LOGGER.info("Database successfully updated with available devices.")
    return True

def execute_convert_images(archive, outfile_path, uuid):
    '''
    Execute the primary analysis convert_imgs command. This function copies the 
    provided archive to tmp space and executes primary analysis convert_imgs on 
    all binaries found in the archive.
    
    @param archive      - Archive directory name where the TDI images live.
    @param outfile_path - File path to final destination of image tar.gz file.
    @param uuid         - Unique identifier for this job.
    '''
    archive_path     = os.path.join(ARCHIVES_PATH, archive)
    tmp_path         = os.path.join(TMP_PATH, uuid)
    destination      = os.path.join(TMP_PATH, uuid, archive)
    destination      = os.path.abspath(destination)
    try:
        # shutil.copytree does not play nicely when copying from samba drive to
        # Mac, so use a system command.
        io_utilities.safe_make_dirs(TMP_PATH)
        os.system("cp -fr %s %s" % (archive_path, tmp_path))
        
        images = io_utilities.filter_files(os.listdir(tmp_path), 
                                           extensions=["bin"]) 
        images =[os.path.join(tmp_path, image) for image in images]
        
        # Run primary analysis process
        convert_images(images, "png", destination)
        
        # Ensure images were converted, and if so create archive
        if os.path.exists(destination) and \
           len([x for x in os.listdir(destination) if x.endswith(".png")]) > 0:
            shutil.make_archive(destination, format='gztar', 
                                root_dir=os.path.dirname(destination),
                                base_dir=os.path.basename(destination))
        else:
            raise Exception("Convert images job failed: no images converted.")
        
        # Ensure archive exists
        out_tar_gz = destination + ".tar.gz"
        if os.path.exists(out_tar_gz):
            shutil.copy(out_tar_gz, outfile_path)
        else:
            raise Exception("Convert images job failed: no archive created.")
    finally:
        pass
        # Regardless of success or failure, remove the copied archive directory
        shutil.rmtree(tmp_path, ignore_errors=True)
        
def execute_process(archive, dyes, device, major, minor, offsets, use_iid, 
                    outfile_path, config_path, uuid):
    '''
    Execute the primary analysis process command. This function copies the 
    provided archive to tmp space and executes primary analysis process on 
    all PNGs found in the archive.
    
    @param archive      - Archive directory name where the TDI images live.
    @param dyes         - Set of dyes used in this run.
    @param device       - Device used to generate the TDI images for this run.
    @param major        - Major dye profile version.
    @param minor        - Minor dye profile version.
    @param offsets      - Range of offsets used to infer a dye model. The 
                          inference will offset the dye profiles in this range
                          to determine an optimal offset. 
    @param use_iid      - Use IID Peak Detection.
    @param outfile_path - Path where the final analysis.txt file should live.
    @param config_path  - Path where the final configuration file should live.
    @param uuid         - Unique identifier for this job.
    '''
    archive_path     = os.path.join(ARCHIVES_PATH, archive)
    tmp_path         = os.path.join(TMP_PATH, uuid)
    tmp_config_path  = os.path.join(tmp_path, "config.txt")
    try:
        # shutil.copytree does not play nicely when copying from samba drive to
        # Mac, so use a system command.
        io_utilities.safe_make_dirs(TMP_PATH)
        os.system("cp -fr %s %s" % (archive_path, tmp_path))

        with open(tmp_config_path, "w") as f:
            print >>f, "dye_map:"
            print >>f, "  device: %s" % device
            if major is not None:
                print >>f, "  major: %s" % major
            if minor is not None:
                print >>f, "  minor: %s" % minor
            print >>f, "  dyes: [%s]" % ", ".join([ "\"%s\"" % x for x in dyes])
            
        images = io_utilities.filter_files(os.listdir(tmp_path), 
                                           VALID_HAM_IMAGE_EXTENSIONS)
        images =[os.path.join(tmp_path, image) for image in images]
        
        # Run primary analysis process
        process(tmp_config_path, images, tmp_path, offsets=offsets, 
                use_iid=use_iid)
        
        # Ensure output file exists
        analysis_output_path = os.path.join(tmp_path, "analysis.txt")
        if not os.path.isfile(analysis_output_path): 
            raise Exception("Process job failed: analysis.txt not generated.")
        else:
            shutil.copy(analysis_output_path, outfile_path)
            shutil.copy(tmp_config_path, config_path)
    finally:
        # Regardless of success or failure, remove the copied archive directory
        shutil.rmtree(tmp_path, ignore_errors=True)
