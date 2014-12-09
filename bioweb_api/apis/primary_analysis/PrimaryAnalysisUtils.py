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
import sys
import shutil

from primary_analysis.dye_datastore import Datastore
from primary_analysis.cmds.process import process

from bioweb_api import ARCHIVES_PATH, TMP_PATH, DYES_COLLECTION, DEVICES_COLLECTION, \
    ARCHIVES_COLLECTION
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api.utilities import io_utilities
from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.ApiConstants import ARCHIVE, DYE, DEVICE

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

def update_archives():
    '''
    Update the database with available primary analysis archives.
    
    @return True if database is successfully updated, False otherwise
    '''
    APP_LOGGER.info("Updating database with available archives...")
    if os.path.isdir(ARCHIVES_PATH):
        
        # Remove archives named similarly (same name, different capitalization)
        archives    = os.listdir(ARCHIVES_PATH)
        lc_archives = [a.lower() for a in archives]
        dups        = set(a for a in archives if lc_archives.count(a.lower()) > 1)
        archives    = [a for a in archives if a not in dups]
        archives    = filter(lambda x: os.path.isdir(os.path.join(ARCHIVES_PATH,x)), archives)
        records     = [{ARCHIVE: archive} for archive in archives]
        
        # There is a possible race condition here. Ideally these operations 
        # would be performed in concert atomically
        _DB_CONNECTOR.remove(ARCHIVES_COLLECTION, {})
        _DB_CONNECTOR.insert(ARCHIVES_COLLECTION, records)
    else:
        APP_LOGGER.error("Couldn't locate archives path to update database.")
        return False

    APP_LOGGER.info("Database successfully updated with available archives.")
    return True
    
def update_dyes():
    '''
    Update the database with available dyes.
    
    @return True if database is successfully updated, False otherwise
    '''
    APP_LOGGER.info("Updating database with available dyes...")
    try:
        records = [{DYE: dye} for dye in _DATASTORE.dyes()]
        
        # There is a possible race condition here. Ideally these operations 
        # would be performed in concert atomically
        _DB_CONNECTOR.remove(DYES_COLLECTION, {})
        _DB_CONNECTOR.insert(DYES_COLLECTION, records)
    except:
        APP_LOGGER.info("Failed to update database with available dyes: %s" 
                        % str(sys.exc_info()))
        return False
    
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
        
        # There is a possible race condition here. Ideally these operations 
        # would be performed in concert atomically
        _DB_CONNECTOR.remove(DEVICES_COLLECTION, {})
        _DB_CONNECTOR.insert(DEVICES_COLLECTION, records)
    except:
        APP_LOGGER.info("Failed to update database with available devices: %s" 
                        % str(sys.exc_info()))
        return False
    
    APP_LOGGER.info("Database successfully updated with available devices.")
    return True

def execute_process(archive, dyes, device, outfile_path, config_path, uuid):
    '''
    Execute the primary analysis process command. This function copies the 
    provided archive to tmp space and executes primary analysis process on 
    all PNGs found in the archive.
    
    @param archive      - Archive directory name where the TDI images live.
    @param dyes         - Set of dyes used in this run.
    @param device       - Device used to generate the TDI images for this run.
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
            print >>f, "  dyes: [%s]" % ", ".join(map(lambda x: "\"%s\"" % x, dyes))
            
        images = filter_images(os.listdir(tmp_path)) 
        images = map(lambda image: os.path.join(tmp_path, image), images)
        
        # Run primary analysis process
        process(tmp_config_path, images, tmp_path)
        
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
        
def filter_images(files):
    """
    Filter a list of files to only return valid image files (i.e. pngs and
    bins).
    
    @param files: list of TDI images
    """
    return filter(lambda x: x.endswith(".png") or x.endswith(".bin"), files)