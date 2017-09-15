'''
Copyright 2015 Bio-Rad Laboratories, Inc.

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
@date:   Mar 3, 2015
'''

#=============================================================================
# Imports
#=============================================================================
import os
import shutil
import sys
import traceback

from datetime import datetime
from uuid import uuid4

from bioweb_api.apis.image.ImageApiHelperFunctions import check_ham_tar_structure
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import FILENAME, ERROR, RESULT, \
    EXP_DEF_NAME, EXP_DEF_UUID, NUM_IMAGES, DATESTAMP, UUID, NAME, \
    DESCRIPTION, URL, ID, STACK_TYPE, HAM, SURFACTANT, BETA, DEVICE, ARCHIVE, \
    USERS, SUBMIT_DATESTAMP, DATE, DYE_PROFILE_METRICS, JOB_STATUS, STATUS, \
    JOB_TYPE_NAME, JOB_TYPE
from bioweb_api import TMP_PATH, IMAGES_COLLECTION, RESULTS_PATH, HOSTNAME, \
    PORT
from bioweb_api.utilities.io_utilities import make_clean_response, \
    silently_remove_file, get_archive_dirs
from bioweb_api.utilities.logging_utilities import APP_LOGGER

from primary_analysis.experiment.experiment_definitions import ExperimentDefinitions

#=============================================================================
# Public Static Variables
#=============================================================================
DYE_PROFILE_RUN_IMAGES = "DyeProfileRunImages"

#=============================================================================
# Class
#=============================================================================
class DyeProfileImagesPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return DYE_PROFILE_RUN_IMAGES
   
    @staticmethod
    def summary():
        return "Add dye profile run images."
    
    @staticmethod
    def notes():
        return ""

    def response_messages(self):
        msgs = super(DyeProfileImagesPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "Image stack already exists. Delete the " \
                                  "existing image stack and retry."},
                     { "code": 404, 
                       "message": "Submission unsuccessful. Either no " \
                       "archive or more than one archive with >1 images was " \
                       "found."},
                     { "code": 415, 
                       "message": "File is not a valid image stack " \
                                  "tarball."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        cls._users_param    = ParameterFactory.lc_string(USERS, 
            "Username(s) of individual(s) that performed the run (e.g. ddicara)", 
            allow_multiple=True)
        cls._date_param     = ParameterFactory.date()
        cls._archive_param = ParameterFactory.archive()
        cls._beta_param     = ParameterFactory.integer(BETA, 
            "Beta (e.g. 17)", required=True, minimum=1, maximum=100)
        cls._device_param   = ParameterFactory.cs_string(DEVICE, 
            "Device description (e.g. PDMS bonded on COP)") 
        cls._dye_profile_metrics_param = ParameterFactory.dye_profile_metrics()
        cls._surfactant_param = ParameterFactory.cs_string(SURFACTANT,
            "Surfactant (e.g. RAN 002-105).")

        parameters = [
                      cls._users_param,
                      cls._date_param,
                      cls._archive_param,
                      cls._beta_param,
                      cls._device_param,
                      cls._dye_profile_metrics_param,
                      cls._surfactant_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        users            = params_dict[cls._users_param]
        date             = params_dict[cls._date_param][0]
        archive_name     = params_dict[cls._archive_param][0]
        beta             = params_dict[cls._beta_param][0]
        device           = params_dict[cls._device_param][0]
        dye_prof_metrics = params_dict[cls._dye_profile_metrics_param]
        surfactant       = params_dict[cls._surfactant_param][0]
        
        json_response = {}
        
        # Ensure archive directory is valid
        try:
            archives = get_archive_dirs(archive_name)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)
        
        # Ensure only one valid archive is found
        if len(archives) != 1:
            APP_LOGGER.warning("Expected 1 archive, found %d" % len(archives))
            return make_clean_response(json_response, 404)

        response = {
                    USERS: users,
                    DATE: date,
                    ARCHIVE: archives[0],
                    BETA: beta,
                    DEVICE: device,
                    DYE_PROFILE_METRICS: dye_prof_metrics,
                    SURFACTANT: surfactant,
                    STATUS: JOB_STATUS.submitted,                # @UndefinedVariable
                    JOB_TYPE_NAME: JOB_TYPE.dye_profile_images,  # @UndefinedVariable
                    SUBMIT_DATESTAMP: datetime.today(),
                   }
        status_code = 200
        
        
        
        
        try:
            
#             # Create helper functions
#             callable = PaProcessCallable(archive, dyes, device,
#                                              major, minor,
#                                              offset, use_iid, 
#                                              outfile_path, 
#                                              config_path,
#                                              response[UUID], 
#                                              cls._DB_CONNECTOR)
#             callback = make_process_callback(response[UUID], 
#                                              outfile_path, 
#                                              config_path,
#                                              cls._DB_CONNECTOR)
# 
#             # Add to queue and update DB
#             cls._DB_CONNECTOR.insert(PA_PROCESS_COLLECTION, [response])
#             cls._EXECUTION_MANAGER.add_job(response[UUID], 
#                                            abs_callable, callback)
        except:
            APP_LOGGER.exception(traceback.format_exc())
            response[ERROR]  = str(sys.exc_info()[1])
            status_code = 500
        finally:
            if ID in response:
                del response[ID]
        
        
        
        
        
        
        
        http_status_code = 200
        uuid             = str(uuid4())
        tmp_archive_path = os.path.join(TMP_PATH, uuid + ".tar.gz")
        archive_path     = os.path.join(RESULTS_PATH, uuid + ".tar.gz")
        json_response    = { 
                            FILENAME: image_stack_tgz.filename,
                            UUID: uuid,
                            DATESTAMP: datetime.today(),
                           }

        try:
            # check tar file
            image_stack_tgz.save(tmp_archive_path)
            image_stack_tgz.close()
            tar_error, nimgs = check_ham_tar_structure(tmp_archive_path, HAM)

            # check for existing image stacks
            existing_stacks = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                                     {NAME: img_stack_name, STACK_TYPE: HAM},
                                                     [NAME])

            # check for exp def
            exp_defs     = ExperimentDefinitions()
            exp_def_uuid = exp_defs.get_experiment_uuid(exp_def_name)

            if existing_stacks:
                http_status_code = 403
                json_response[ERROR] = "Image stack with given name already " \
                            "exists."
            elif not exp_def_uuid:
                http_status_code = 404
                json_response[ERROR] = "Couldn't locate UUID for " \
                    "experiment definition."
            elif tar_error:
                APP_LOGGER.error(tar_error)
                http_status_code = 415
                json_response[ERROR] = tar_error
            else:
                url = "http://%s/results/%s/%s" % (HOSTNAME, PORT,
                                                   os.path.basename(archive_path))
                shutil.copy(tmp_archive_path, archive_path)
                json_response[RESULT]       = archive_path
                json_response[URL]          = url
                json_response[NAME]         = img_stack_name
                json_response[DESCRIPTION]  = short_desc
                json_response[EXP_DEF_NAME] = exp_def_name
                json_response[EXP_DEF_UUID] = exp_def_uuid
                json_response[NUM_IMAGES]   = nimgs
                json_response[STACK_TYPE]  = HAM
                cls._DB_CONNECTOR.insert(IMAGES_COLLECTION,
                                         [json_response])
        except IOError:
            APP_LOGGER.exception(traceback.format_exc())
            http_status_code     = 415
            json_response[ERROR] = str(sys.exc_info()[1])
        except:
            APP_LOGGER.exception(traceback.format_exc())
            http_status_code     = 500
            json_response[ERROR] = str(sys.exc_info()[1])
        finally:
            if ID in json_response:
                del json_response[ID]
            silently_remove_file(tmp_archive_path)
        
        return make_clean_response(json_response, http_status_code)
    
#===============================================================================
# Callable/Callback Functionality
#===============================================================================
class PaProcessCallable(object):
    """
    Callable that executes the process command.
    """
    def __init__(self, archive, dyes, device, major, minor, offset, use_iid,
                 outfile_path, config_path, uuid, db_connector):
        self.archive      = archive
        self.db_connector = db_connector
        self.query        = {UUID: uuid}
    
    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}     
        self.db_connector.update(PA_PROCESS_COLLECTION, self.query, update)
        return execute_process(self.archive, self.dyes, self.device, self.major,
                               self.minor, self.offsets, self.use_iid, 
                               self.outfile_path, self.config_path, 
                               self.query[UUID])
        
def make_process_callback(uuid, outfile_path, config_path, db_connector):
    """
    Return a closure that is fired when the job finishes. This 
    callback updates the DB with completion status, result file location, and
    an error message if applicable.
    
    @param uuid: Unique job id in database
    @param outfile_path - Path where the final analysis.txt file should live.
    @param config_path  - Path where the final configuration file should live.
    @param db_connector: Object that handles communication with the DB
    """
    query = {UUID: uuid}
    def process_callback(future):
        try:
            _ = future.result()
            update = { "$set": { 
                                 STATUS: JOB_STATUS.succeeded, # @UndefinedVariable
                                 RESULT: outfile_path,
                                 CONFIG: config_path,
                                 FINISH_DATESTAMP: datetime.today(),
                                 URL: "http://%s/results/%s/%s" % (HOSTNAME, PORT, uuid),
                                 CONFIG_URL: "http://%s/results/%s/%s.cfg" % (HOSTNAME, PORT, uuid),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(PA_PROCESS_COLLECTION, query, {})) > 0:
                db_connector.update(PA_PROCESS_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(config_path)
        except:
            error_msg = str(sys.exc_info()[1])
            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   RESULT: None, 
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(PA_PROCESS_COLLECTION, query, {})) > 0:
                db_connector.update(PA_PROCESS_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
                silently_remove_file(config_path)
        
    return process_callback
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = DyeProfileRunPostFunction()
    print function        