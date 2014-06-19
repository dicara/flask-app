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
@date:  Jun 12, 2014
'''

#===============================================================================
# Imports
#===============================================================================
import unittest
import os
import time
import filecmp

from src.apis.melting_temperature.idtClient import IDTClient

#===============================================================================
# Global Private Variables
#===============================================================================
_PROBES_FILENAME = "test_probes.csv"
_EXPECTED_RESULT_FILENAME = "expected_melting_temps.txt"
_OBSERVED_RESULT_FILENAME = "observed_melting_temps.txt"

#===============================================================================
# Test
#===============================================================================
class Test(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_validation(self):
        pass
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()