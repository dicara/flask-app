'''
Copyright 2015 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
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
import tarfile

from datetime import datetime
from uuid import uuid4

from bioweb_api.apis.image.ImageApiHelperFunctions import check_tar_structure, \
    get_number_imgs
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import FILENAME, ERROR, RESULT, \
    NUM_IMAGES,DATESTAMP, UUID, NAME, DESCRIPTION, URL, ID, STACK_TYPE
from bioweb_api import TMP_PATH, IMAGES_COLLECTION, RESULTS_PATH, HOSTNAME, \
    PORT
from bioweb_api.utilities.io_utilities import make_clean_response, \
    silently_remove_file

#=============================================================================
# Public Static Variables
#=============================================================================
MONITOR_IMAGES = 'MonitorImages'

#=============================================================================
# Class
#=============================================================================
class MonitorImagesPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return MONITOR_IMAGES
   
    @staticmethod
    def summary():
        return 'Add monitor camera images.'
    
    @staticmethod
    def notes():
        return ''

    def response_messages(self):
        msgs = super(MonitorImagesPostFunction, self).response_messages()
        msgs.extend([
                     { 'code': 403, 
                       'message': 'Image stack already exists. Delete the ' \
                                  'existing image stack and retry.'},
                     { 'code': 404, 
                       'message': 'Submission unsuccessful. No experiment ' \
                       'definition found matching input criteria.'},
                     { 'code': 415, 
                       'message': 'File is not a valid image stack ' \
                                  'tarball.'},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        cls._file_param       = ParameterFactory.file('Image stack tgz file.')
        cls._stack_type_param = ParameterFactory.mon_camera_type(STACK_TYPE,
            'Monitor Camera Number')
        cls._name_param       = ParameterFactory.cs_string(NAME,
            'Unique name to give this image stack.')
        cls._short_desc_param = ParameterFactory.cs_string(DESCRIPTION,
            'Short description of image stack.')

        parameters = [
                      cls._file_param,
                      cls._stack_type_param,
                      cls._name_param,
                      cls._short_desc_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        image_stack_tgz  = params_dict[cls._file_param][0]
        stack_type       = params_dict[cls._stack_type_param][0]
        img_stack_name   = params_dict[cls._name_param][0]
        short_desc       = params_dict[cls._short_desc_param][0]
        http_status_code = 200
        uuid             = str(uuid4())
        tmp_archive_path = os.path.join(TMP_PATH, uuid + '.tar.gz')
        archive_path     = os.path.join(RESULTS_PATH, uuid + '.tar.gz')
        json_response    = { 
                            FILENAME: image_stack_tgz.filename,
                            UUID: uuid,
                            DATESTAMP: datetime.today(),
                           }

        try:
            # check tar file
            image_stack_tgz.save(tmp_archive_path)
            image_stack_tgz.close()

            tar_error = check_tar_structure(tmp_archive_path, stack_type)

            # check for existing image stacks
            existing_stacks = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                                     {NAME: img_stack_name, STACK_TYPE: stack_type},
                                                     [NAME])
            if existing_stacks:
                http_status_code = 403
                json_response[ERROR] = 'Image stack with given name already ' \
                            'exists.'
            elif tar_error:
                http_status_code = 415
                json_response[ERROR] = tar_error
            else:
                url = 'http://%s/results/%s/%s' % (HOSTNAME, PORT,
                                                   os.path.basename(archive_path))
                shutil.copy(tmp_archive_path, archive_path)
                json_response[RESULT]      = archive_path
                json_response[URL]         = url
                json_response[NAME]        = img_stack_name
                json_response[DESCRIPTION] = short_desc
                json_response[NUM_IMAGES]  = get_number_imgs(tmp_archive_path)
                json_response[STACK_TYPE]  = stack_type
                cls._DB_CONNECTOR.insert(IMAGES_COLLECTION,
                                         [json_response])
        except IOError:
            http_status_code     = 415
            json_response[ERROR] = str(sys.exc_info()[1])
        except:
            http_status_code     = 500
            json_response[ERROR] = str(sys.exc_info()[1])
        finally:
            if ID in json_response:
                del json_response[ID]
            silently_remove_file(tmp_archive_path)
        
        return make_clean_response(json_response, http_status_code)
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == '__main__':
    function = MonitorImagesPostFunction()
    print function        