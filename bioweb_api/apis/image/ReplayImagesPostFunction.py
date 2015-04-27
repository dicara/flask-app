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
import tempfile

from datetime import datetime
from uuid import uuid4

from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.ApiConstants import FILENAME, ERROR, RESULT, \
    VALID_IMAGE_EXTENSIONS,DATESTAMP, UUID, NAME, URL, ID, HAM_NAME, \
    MON1_NAME, MON2_NAME, STACK_TYPE, MONITOR1, MONITOR2, HAM, REPLAY
from bioweb_api import TMP_PATH, IMAGES_COLLECTION, RESULTS_PATH, HOSTNAME, \
    PORT
from bioweb_api.utilities.io_utilities import make_clean_response, \
    silently_remove_file

#=============================================================================
# Public Static Variables
#=============================================================================
REPLAY_IMAGES = 'ReplayImages'

#=============================================================================
# Helper Functions
#=============================================================================
def add_imgs(replay_tar_file, existing_tar, tmp_path, stack_type):
    """
    Adds images from existing image files into a the replay tar file.

    @param replay_tar_file: Tarfile object that is writable.
    @param existing_tar:    String specifying path to tar file containing image stacks
    @param tmp_path:        String specifying temporary directory to tar/untar
    @param stack_type:      String specifying name of image type (will be name of root dir)
    """
    tf = tarfile.open(existing_tar)
    tf.extractall(tmp_path)

    replay_tar_file.add(os.path.join(tmp_path, stack_type), stack_type)
    shutil.rmtree(os.path.join(tmp_path, stack_type))


#=============================================================================
# Class
#=============================================================================
class ReplayImagesPostFunction(AbstractPostFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return REPLAY_IMAGES
   
    @staticmethod
    def summary():
        return 'Add replay camera image stacks'
    
    @staticmethod
    def notes():
        return ''

    def response_messages(self):
        msgs = super(ReplayImagesPostFunction, self).response_messages()
        msgs.extend([
                     { 'code': 403, 
                       'message': 'Image stack already exists. Delete the ' \
                                  'existing image stack and retry.'},
                     { 'code': 415, 
                       'message': 'File is not a valid image stack ' \
                                  'tarball.'},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):

        existing_ham_stacks  = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                              {STACK_TYPE: HAM},
                                              [NAME])

        existing_mon1_stacks = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                              {STACK_TYPE: MONITOR1},
                                              [NAME])

        existing_mon2_stacks = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                              {STACK_TYPE: MONITOR2},
                                              [NAME])
        uniq_ham  = set([rec[NAME] for rec in existing_ham_stacks])
        uniq_mon1 = set([rec[NAME] for rec in existing_mon1_stacks])
        uniq_mon2 = set([rec[NAME] for rec in existing_mon2_stacks])

        cls._name_param = ParameterFactory.cs_string(NAME,
            'Unique name to give this image stack.')
        cls._ham_imgs   = ParameterFactory.available_stacks(HAM_NAME,
            'Existing ham image stack.', uniq_ham)
        cls._mon1_imgs  = ParameterFactory.available_stacks(MON1_NAME,
            'Existing monitor camera 1 image stack.', uniq_mon1)
        cls._mon2_imgs  = ParameterFactory.available_stacks(MON2_NAME,
            'Existing monitor camera 2 image stack.', uniq_mon2)

        parameters = [
                      cls._name_param,
                      cls._ham_imgs,
                      cls._mon1_imgs,
                      cls._mon2_imgs,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        replay_stack_name = params_dict[cls._name_param][0]
        ham_stack_name    = params_dict[cls._ham_imgs][0]
        mon1_stack_name   = params_dict[cls._mon1_imgs][0]
        mon2_stack_name   = params_dict[cls._mon2_imgs][0]
        http_status_code  = 200
        uuid              = str(uuid4())
        json_response     = {DATESTAMP: datetime.today()}

        try:
            # check for existing exists
            existing_replay_stacks = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                                  {NAME: replay_stack_name, STACK_TYPE: REPLAY},
                                                  [NAME, RESULT])

            existing_ham_stacks    = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                                  {STACK_TYPE: HAM},
                                                  [RESULT])

            existing_mon1_stacks   = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                                  {STACK_TYPE: MONITOR1},
                                                  [RESULT])

            existing_mon2_stacks   = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                                  {STACK_TYPE: MONITOR2},
                                                  [RESULT])

            similar_replay_stacks  = cls._DB_CONNECTOR.find(IMAGES_COLLECTION,
                                                  {HAM_NAME: ham_stack_name,
                                                   MON1_NAME: mon1_stack_name,
                                                   MON2_NAME: mon2_stack_name,
                                                   STACK_TYPE: REPLAY},
                                                  [NAME, RESULT])
            # verify replay stack name is unique
            if existing_replay_stacks:
                http_status_code = 403
                json_response[ERROR] = 'Replay image stack with given name already ' \
                            'exists.'
            # check if similar replay stack already exists
            elif similar_replay_stacks:
                similar_name = similar_replay_stacks[0][NAME]
                http_status_code = 403
                json_response[ERROR] = 'Similar replay stack named "%s" already exists.' % similar_name
            # if no similar stack exists enter it into the database
            else:
                tmp_path = ''
                try:
                    # temporary path for taring, untaring, etc...
                    tmp_path = tempfile.mkdtemp()

                    # make readme
                    readme_file_name = 'README'
                    readme_path = os.path.join(tmp_path, readme_file_name)
                    readme_str = '\n'.join([ham_stack_name, mon1_stack_name, mon2_stack_name])
                    with open(readme_path, 'w') as fh:
                        fh.write(readme_str)

                    # create new tar file
                    new_tf_name = uuid+'.tar.gz'
                    new_tf_path = os.path.join(tmp_path, new_tf_name)
                    new_tf = tarfile.open(new_tf_path, 'w:gz')

                    # add readme and images
                    new_tf.add(readme_path, readme_file_name)
                    add_imgs(new_tf, existing_ham_stacks[0][RESULT], tmp_path, HAM)
                    add_imgs(new_tf, existing_mon1_stacks[0][RESULT], tmp_path, MONITOR1)
                    add_imgs(new_tf, existing_mon2_stacks[0][RESULT], tmp_path, MONITOR2)
                    new_tf.close()

                    # move new tar file to results directory
                    archive_path = os.path.join(RESULTS_PATH, new_tf_name)
                    shutil.move(new_tf_path, archive_path)

                    # insert into database
                    url = 'http://%s/results/%s/%s' % (HOSTNAME, PORT, os.path.basename(archive_path))
                    json_response[FILENAME]   = new_tf_name
                    json_response[RESULT]     = archive_path
                    json_response[URL]        = url
                    json_response[UUID]       = uuid
                    json_response[HAM_NAME]   = ham_stack_name
                    json_response[MON1_NAME]  = mon1_stack_name
                    json_response[MON2_NAME]  = mon2_stack_name
                    json_response[NAME]       = replay_stack_name
                    json_response[STACK_TYPE] = REPLAY
                    cls._DB_CONNECTOR.insert(IMAGES_COLLECTION, [json_response])
                except:
                    http_status_code     = 500
                    json_response[ERROR] = str(sys.exc_info()[1])
                finally:
                    shutil.rmtree(tmp_path)

        except:
            http_status_code     = 500
            json_response[ERROR] = str(sys.exc_info()[1])
        finally:
            if ID in json_response:
                del json_response[ID]


        return make_clean_response(json_response, http_status_code)
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == '__main__':
    function = ReplayImagesPostFunction()
    print function        