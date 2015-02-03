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
@date:   Jan 30, 2015
'''

#=============================================================================
# Imports
#=============================================================================
import os
import sys

from uuid import uuid4
from datetime import datetime

from bioweb_api import PA_CONVERT_IMAGES_COLLECTION, RESULTS_PATH, HOSTNAME, PORT
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.utilities.io_utilities import make_clean_response, \
    get_archive_dirs, silently_remove_file
from bioweb_api.apis.ApiConstants import ERROR, JOB_NAME, ARCHIVE, UUID, \
    SUBMIT_DATESTAMP, START_DATESTAMP, FINISH_DATESTAMP, STATUS, JOB_STATUS, \
    JOB_TYPE_NAME, JOB_TYPE, ID, RESULT, URL
from bioweb_api.apis.primary_analysis.PrimaryAnalysisUtils import execute_convert_images

#=============================================================================
# Public Global Variables
#=============================================================================
CONVERT_IMAGES = "ConvertImages"

#=============================================================================
# Class
#=============================================================================
class ConvertImagesPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "ConvertImages"
   
    @staticmethod
    def summary():
        return "Convert binary images to pngs."
    
    @staticmethod
    def notes():
        return ""

    def response_messages(self):
        msgs = super(ConvertImagesPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "Job name already exists. Delete the " \
                                  "existing job or pick a new name."},
                     { "code": 404, 
                       "message": "Submission unsuccessful. At least 1 "\
                                  "images must exist in archive."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        cls.archives_param = ParameterFactory.archive()
        cls.job_name_param = ParameterFactory.lc_string(JOB_NAME, "Unique "\
                                                        "name to give this "
                                                        "job.")

        
        parameters = [
                      cls.archives_param,
                      cls.job_name_param,
                     ]
        return parameters
 
    @classmethod
    def process_request(cls, params_dict):
        archive_names  = params_dict[cls.archives_param]
        job_name       = params_dict[cls.job_name_param][0]
        
        json_response = {CONVERT_IMAGES: []}
        
        # Ensure archive directory is valid
        try:
            archives = list()
            for archive_name in archive_names:
                archives.extend(get_archive_dirs(archive_name, 
                                                 extensions=["bin"]))
        except:
            json_response[ERROR] = str(sys.exc_info()[1])
            return make_clean_response(json_response, 500)

        # Ensure at least one valid archive is found
        if len(archives) < 1:
            return make_clean_response(json_response, 404)
        
        # Process each archive
        status_codes  = []
        for i, archive in enumerate(archives):
            if len(archives) == 1:
                cur_job_name = job_name
            else:
                cur_job_name = "%s-%d" % (job_name, i)
                
            response = {
                        ARCHIVE: archive,
                        UUID: str(uuid4()),
                        STATUS: JOB_STATUS.submitted,       # @UndefinedVariable
                        JOB_NAME: cur_job_name,
                        JOB_TYPE_NAME: JOB_TYPE.pa_convert_images, # @UndefinedVariable
                        SUBMIT_DATESTAMP: datetime.today(),
                       }
            status_code = 200
            
            if cur_job_name in cls._DB_CONNECTOR.distinct(PA_CONVERT_IMAGES_COLLECTION, 
                                                          JOB_NAME):
                status_code = 403
            else:
                try:
                    outfile_path = os.path.join(RESULTS_PATH, response[UUID] + ".tar.gz")
                    
                    # Create helper functions
                    abs_callable = PaConvertImagesCallable(archive, 
                                                           outfile_path, 
                                                           response[UUID], 
                                                           cls._DB_CONNECTOR)
                    callback = make_process_callback(response[UUID], 
                                                     outfile_path, 
                                                     cls._DB_CONNECTOR)
    
                    # Add to queue and update DB
                    cls._DB_CONNECTOR.insert(PA_CONVERT_IMAGES_COLLECTION, 
                                             [response])
                    cls._EXECUTION_MANAGER.add_job(response[UUID], 
                                                   abs_callable, callback)
                    del response[ID]
                except:
                    response[ERROR]  = str(sys.exc_info()[1])
                    status_code = 500
            
            json_response[CONVERT_IMAGES].append(response)
            status_codes.append(status_code)
        
        # If all jobs submitted successfully, then 200 should be returned.
        # Otherwise, the maximum status code seems good enough.
        return make_clean_response(json_response, max(status_codes))
       
#===============================================================================
# Callable/Callback Functionality
#===============================================================================
class PaConvertImagesCallable(object):
    """
    Callable that executes the convert images command.
    """
    def __init__(self, archive, outfile_path, uuid, db_connector):
        self.archive      = archive
        self.outfile_path = outfile_path
        self.db_connector = db_connector
        self.query        = {UUID: uuid}
     
    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,      # @UndefinedVariable
                           START_DATESTAMP: datetime.today()}}     
        self.db_connector.update(PA_CONVERT_IMAGES_COLLECTION, self.query, 
                                 update)
        return execute_convert_images(self.archive, self.outfile_path,
                                      self.query[UUID])
         
def make_process_callback(uuid, outfile_path, db_connector):
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
                                 FINISH_DATESTAMP: datetime.today(),
                                 URL: "http://%s/results/%s/%s" % (HOSTNAME, 
                                                                   PORT, 
                                                                   os.path.basename(outfile_path)),
                               }
                    }
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(PA_CONVERT_IMAGES_COLLECTION, query, {})) > 0:
                db_connector.update(PA_CONVERT_IMAGES_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
        except:
            error_msg = str(sys.exc_info()[1])
            update    = { "$set": {STATUS: JOB_STATUS.failed, # @UndefinedVariable
                                   RESULT: None, 
                                   FINISH_DATESTAMP: datetime.today(),
                                   ERROR: error_msg}}
            # If job has been deleted, then delete result and don't update DB.
            if len(db_connector.find(PA_CONVERT_IMAGES_COLLECTION, query, {})) > 0:
                db_connector.update(PA_CONVERT_IMAGES_COLLECTION, query, update)
            else:
                silently_remove_file(outfile_path)
          
    return process_callback
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ConvertImagesPostFunction()
    print function
        