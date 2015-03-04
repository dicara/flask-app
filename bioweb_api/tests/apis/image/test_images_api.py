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
from bioweb_api.tests.test_utils import get_data, delete_data, \
    add_url_argument, upload_file
from bioweb_api.apis.ApiConstants import EXP_DEF, NAME, DESCRIPTION, UUID,\
    NUM_IMAGES

#=============================================================================
# Public Static Variables
#=============================================================================

#=============================================================================
# Private Static Variables
#=============================================================================
_TEST_DIR       = os.path.abspath(os.path.dirname(__file__))
_IMAGES_URL     = os.path.join("/api/v1/Image", IMAGES)
_PNG_IMAGES     = "png_images.tgz"
_BIN_IMAGES     = "bin_images.tgz"
_NO_IMAGES      = "empty.tgz"
_NOT_AN_ARCHIVE = "not_an_archive.txt"

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

#=============================================================================
# Main
#=============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()