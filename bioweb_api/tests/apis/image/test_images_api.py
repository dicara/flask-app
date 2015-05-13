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
@date:   Mar 4, 2015
'''

#=============================================================================
# Imports
#=============================================================================
import os
import unittest

from bioweb_api import app
from bioweb_api.apis.image.ImagesPostFunction import IMAGES
from bioweb_api.apis.image.MonitorImagesPostFunction import MONITOR_IMAGES
from bioweb_api.apis.image.ReplayImagesPostFunction import REPLAY_IMAGES
from bioweb_api.tests.test_utils import get_data, delete_data, \
    add_url_argument, upload_file, post_data
from bioweb_api.apis.ApiConstants import EXP_DEF, NAME, DESCRIPTION, UUID,\
    NUM_IMAGES, STACK_TYPE, MONITOR1, MONITOR2, HAM_NAME, MON1_NAME, MON2_NAME

#=============================================================================
# Public Static Variables
#=============================================================================

#=============================================================================
# Private Static Variables
#=============================================================================
_TEST_DIR       = os.path.abspath(os.path.dirname(__file__))
_IMAGES_URL     = os.path.join("/api/v1/Image", IMAGES)
_MON_IMAGES_URL = os.path.join("/api/v1/Image", MONITOR_IMAGES)
_REPLAY_IMAGES_URL = os.path.join("/api/v1/Image", REPLAY_IMAGES)
_HAM_IMAGES     = "ham_images.tgz"
_MON1_IMAGES    = "mon1_images.tgz"
_MON2_IMAGES    = "mon2_images.tgz"
_PNG_IMAGES     = "png_images.tgz"
_BIN_IMAGES     = "bin_images.tgz"
_NO_IMAGES      = "empty.tgz"
_NOT_AN_ARCHIVE = "not_an_archive.txt"
_INVALID_HAM_NAME = "invalid_ham_name.tgz"
_INVALID_MON_NAME = "invalid_mon_name.tgz"

#=============================================================================
# Class
#=============================================================================
class TestImagesAppi(unittest.TestCase):

    def setUp(self):
        self._client = app.test_client(self)
        
    def test_invalid_exp_def(self):
        url = _IMAGES_URL
        url = add_url_argument(url, EXP_DEF, 'invalid_exp_def', True)
        url = add_url_argument(url, NAME, 'invalid_exp_def')
        url = add_url_argument(url, DESCRIPTION, 'Invalid exp def.')
        upload_file(self, _TEST_DIR, url, _PNG_IMAGES, 404)

    def test_empty_archive(self):
        url = _IMAGES_URL
        url = add_url_argument(url, EXP_DEF, 'test_golden_run', True)
        url = add_url_argument(url, NAME, 'empty_archive')
        url = add_url_argument(url, DESCRIPTION, 'Empty archive.')
        upload_file(self, _TEST_DIR, url, _NO_IMAGES, 415)
        
    def test_not_an_archive(self):
        url = _IMAGES_URL
        url = add_url_argument(url, EXP_DEF, 'test_golden_run', True) 
        url = add_url_argument(url, NAME, 'not_an_archive') 
        url = add_url_argument(url, DESCRIPTION, 'Not an archive.')
        upload_file(self, _TEST_DIR, url, _NOT_AN_ARCHIVE, 415)

    def test_invalid_ham_dir_name(self):
        url = _IMAGES_URL
        url = add_url_argument(url, EXP_DEF, 'test_golden_run', True)
        url = add_url_argument(url, NAME, 'invalid ham dir name')
        url = add_url_argument(url, DESCRIPTION, 'invalid ham dir name')
        upload_file(self, _TEST_DIR, url, _INVALID_HAM_NAME, 415)

    def test_invalid_mon_dir_name(self):
        url = _MON_IMAGES_URL
        url = add_url_argument(url, STACK_TYPE, MONITOR1, True)
        url = add_url_argument(url, NAME, 'invalid monitor dir name')
        url = add_url_argument(url, DESCRIPTION, 'invalid monitor dir name')
        upload_file(self, _TEST_DIR, url, _INVALID_MON_NAME, 415)
        
    def test_bin_images(self):
        # Upload image stack
        url = _IMAGES_URL
        url = add_url_argument(url, EXP_DEF, 'test_golden_run', True)
        url = add_url_argument(url, NAME, 'bin_images')
        url = add_url_argument(url, DESCRIPTION, 'Binary image stack.')

        response = upload_file(self, _TEST_DIR, url, _BIN_IMAGES, 200)
        msg = "Expected number of images (%d) not equal to observed (%d)." % \
            (4, response[NUM_IMAGES])
        self.assertEqual(response[NUM_IMAGES], 4, msg)

        # Delete image stack
        url = add_url_argument(_IMAGES_URL, UUID, response[UUID], True)
        delete_data(self, url, 200)

    def test_images(self):
        """
        Test the POST, GET and DELETE images APIs.
        """
        # Upload image stack
        url = _IMAGES_URL
        url = add_url_argument(url, EXP_DEF, 'test_golden_run', True)
        url = add_url_argument(url, NAME, 'golden_run')
        url = add_url_argument(url, DESCRIPTION, 'Short description.')

        response = upload_file(self, _TEST_DIR, url, _PNG_IMAGES, 200)
        image_stack_uuid = response[UUID]

        # Ensure duplicate image stacks cannot be uploaded
        response = upload_file(self, _TEST_DIR, url, _PNG_IMAGES, 403)

        # Ensure image stack exists in the database and can be retrieved
        response = get_data(self, _IMAGES_URL, 200)
        record_found = False
        for record in response[IMAGES]:
            if record[UUID] == image_stack_uuid:
                record_found = True
        msg = "Image stack %s doesn't exist in the database." % image_stack_uuid
        self.assertTrue(record_found, msg)

        # Delete image stack
        url = add_url_argument(_IMAGES_URL, UUID, image_stack_uuid, True)
        delete_data(self, url, 200)

        # Ensure image stack no longer exists in the database
        response = get_data(self, _IMAGES_URL, 200)
        for record in response[IMAGES]:
            msg = "Image stack %s still exists in the database." % record[UUID]
            self.assertNotEqual(image_stack_uuid, record[UUID], msg)

    def test_monitor_images(self):
        """
        Test the POST, GET and DELETE images APIs.
        """
        # Upload image stack
        url = _MON_IMAGES_URL
        url = add_url_argument(url, STACK_TYPE, MONITOR1, True)
        url = add_url_argument(url, NAME, 'monitor1_images_name')
        url = add_url_argument(url, DESCRIPTION, 'monitor1 images description')

        response = upload_file(self, _TEST_DIR, url, _MON1_IMAGES, 200)
        image_stack_uuid = response[UUID]

        # Ensure duplicate image stacks cannot be uploaded
        upload_file(self, _TEST_DIR, url, _MON1_IMAGES, 403)

        # Ensure image stack exists in the database and can be retrieved
        response = get_data(self, _MON_IMAGES_URL, 200)
        record_found = False
        for record in response[MONITOR_IMAGES]:
            if record[UUID] == image_stack_uuid:
                record_found = True
        msg = "Monitor image stack %s doesn't exist in the database." % image_stack_uuid
        self.assertTrue(record_found, msg)

        # Delete image stack
        url = add_url_argument(_IMAGES_URL, UUID, image_stack_uuid, True)
        delete_data(self, url, 200)

        # Ensure image stack no longer exists in the database
        response = get_data(self, _MON_IMAGES_URL, 200)
        for record in response[MONITOR_IMAGES]:
            msg = "Monitor image stack %s still exists in the database." % record[UUID]
            self.assertNotEqual(image_stack_uuid, record[UUID], msg)

    def test_replay_get(self):
        """
        Test the POST, GET and DELETE images APIs.
        """

        # Upload ham image stack
        ham_url = _IMAGES_URL
        ham_url = add_url_argument(ham_url, EXP_DEF, 'test_golden_run', True)
        ham_url = add_url_argument(ham_url, NAME, 'golden_run')
        ham_url = add_url_argument(ham_url, DESCRIPTION, 'Short description.')
        ham_response = upload_file(self, _TEST_DIR, ham_url, _HAM_IMAGES, 200)
        ham_uuid = ham_response[UUID]

        # Upload monitor 1 image stack
        mon1_url = _MON_IMAGES_URL
        mon1_url = add_url_argument(mon1_url, STACK_TYPE, MONITOR1, True)
        mon1_url = add_url_argument(mon1_url, NAME, 'monitor1_images_name')
        mon1_url = add_url_argument(mon1_url, DESCRIPTION, 'monitor1 images description')
        mon1_response = upload_file(self, _TEST_DIR, mon1_url, _MON1_IMAGES, 200)
        mon1_uuid = mon1_response[UUID]

        # Upload monitor 2 image stack
        mon2_url = _MON_IMAGES_URL
        mon2_url = add_url_argument(mon2_url, STACK_TYPE, MONITOR2, True)
        mon2_url = add_url_argument(mon2_url, NAME, 'monitor2_images_name')
        mon2_url = add_url_argument(mon2_url, DESCRIPTION, 'monitor2 images description')
        mon2_response = upload_file(self, _TEST_DIR, mon2_url, _MON2_IMAGES, 200)
        mon2_uuid = mon2_response[UUID]

        # create a replay image stack from existing stacks
        replay_url = _REPLAY_IMAGES_URL
        replay_url = add_url_argument(replay_url, NAME, 'replay_images_name', True)
        replay_url = add_url_argument(replay_url, HAM_NAME, 'golden_run')
        replay_url = add_url_argument(replay_url, MON1_NAME, 'monitor1_images_name')
        replay_url = add_url_argument(replay_url, MON2_NAME, 'monitor2_images_name')
        replay_url = add_url_argument(replay_url, DESCRIPTION, 'replay images description')
        replay_response = post_data(self, replay_url, 200)
        replay_uuid = replay_response[UUID]

        # try to add replay image stack with same name
        replay_url = _REPLAY_IMAGES_URL
        replay_url = add_url_argument(replay_url, NAME, 'replay_images_name', True)
        replay_url = add_url_argument(replay_url, HAM_NAME, 'golden_run')
        replay_url = add_url_argument(replay_url, MON1_NAME, 'monitor1_images_name')
        replay_url = add_url_argument(replay_url, MON2_NAME, 'monitor2_images_name')
        replay_url = add_url_argument(replay_url, DESCRIPTION, 'replay images description')
        post_data(self, replay_url, 403)

        # try to add replay image stack comprised of the same ham/mon image stacks
        replay_url = _REPLAY_IMAGES_URL
        replay_url = add_url_argument(replay_url, NAME, 'different_replay_images_name', True)
        replay_url = add_url_argument(replay_url, HAM_NAME, 'golden_run')
        replay_url = add_url_argument(replay_url, MON1_NAME, 'monitor1_images_name')
        replay_url = add_url_argument(replay_url, MON2_NAME, 'monitor2_images_name')
        replay_url = add_url_argument(replay_url, DESCRIPTION, 'replay images description')
        post_data(self, replay_url, 403)

        # Delete image stacks
        url = add_url_argument(_IMAGES_URL, UUID, ham_uuid, True)
        delete_data(self, url, 200)
        url = add_url_argument(_IMAGES_URL, UUID, mon1_uuid, True)
        delete_data(self, url, 200)
        url = add_url_argument(_IMAGES_URL, UUID, mon2_uuid, True)
        delete_data(self, url, 200)
        url = add_url_argument(_IMAGES_URL, UUID, replay_uuid, True)
        delete_data(self, url, 200)



#=============================================================================
# Main
#=============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()