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
@date:  Jun 23, 2014
'''

#===============================================================================
# Imports
#===============================================================================
import unittest
import os
import time
import filecmp

from src.analyses.probe_validation import validation

#===============================================================================
# Global Private Variables
#===============================================================================
_TARGETS_FILENAME = "targets.fasta"
_PROBES_FILENAME  = "probes.fasta"
_EXPECTED_RESULT_FILENAME = "expected_validation.txt"
_OBSERVED_RESULT_FILENAME = "observed_validation.txt"

#===============================================================================
# Test
#===============================================================================
class Test(unittest.TestCase):
    
    def setUp(self):
        self.targets_file = os.path.join(os.path.dirname(__file__), _TARGETS_FILENAME)
        self.probes_file  = os.path.join(os.path.dirname(__file__), _PROBES_FILENAME)
        self.absorb       = False
        self.num          = 3
        
        msg = "%s targets FASTA file not found." % self.targets_file
        self.assertTrue(os.path.isfile(self.targets_file), msg)
        msg = "%s probes FASTA file not found." % self.probes_file
        self.assertTrue(os.path.isfile(self.probes_file), msg)

    def test_validation(self):
        validation.validate(self.targets_file, self.probes_file, self.absorb, 
                            _OBSERVED_RESULT_FILENAME, self.num)
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()