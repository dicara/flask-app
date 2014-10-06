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
@date:   Oct 6, 2014
'''

#=============================================================================
# Imports
#=============================================================================
import unittest
import os
import filecmp

from collections import OrderedDict

from bioweb_api import app
from bioweb_api.tests.test_utils import get_data

#=============================================================================
# Private Global Variables
#=============================================================================
_IDT                      = "IDT"
_NAME                     = "Name"
_SEQUENCE                 = "Sequence"
_TM                       = "Tm"
_PROBES_FILENAME          = "test_probes.csv"
_EXPECTED_RESULT_FILENAME = "expected_melting_temps.txt"
_OBSERVED_RESULT_FILENAME = "observed_melting_temps.txt"
_MELTING_TEMPERATURE_URL  = "/api/v1/MeltingTemperature"
_IDT_URL                  = os.path.join(_MELTING_TEMPERATURE_URL, _IDT)

#=============================================================================
# Class
#=============================================================================
class TestMeltingTemperatureAPI(unittest.TestCase):
    
    def setUp(self):
        self._client = app.test_client(self)

        # Input Name,Sequence file
        input_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                  _PROBES_FILENAME)
        self.assertTrue(os.path.isfile(input_path))
        probes_dict = OrderedDict()

        with open(input_path) as f:
            f.readline()
            for line in f:
                fields = line.strip().split(",")
                probes_dict[fields[0]] = fields[1]
        self.probes_dict = probes_dict
   
        # Expected Name,Sequence/Tm file
        expected_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                     _EXPECTED_RESULT_FILENAME)
        self.assertTrue(os.path.isfile(expected_path))
        self.expected_result_path = expected_path
        
    def testMeltingTemperatures(self):
        url = _IDT_URL + "?sequence_name=%s&sequence=%s" % \
            (",".join(self.probes_dict.keys()), 
             ",".join(self.probes_dict.values()))
        response = get_data(self, url, 200)
        results  = {x[_NAME]: (x[_TM],x[_SEQUENCE]) for x in response[_IDT]}
        with open(_OBSERVED_RESULT_FILENAME, 'w') as f:
            print >>f, "\t".join([_NAME, _SEQUENCE, _TM])
            for name in sorted(results.keys()):
                tm  = str(results[name][0])
                seq = results[name][1]
                print >>f, "\t".join([name, seq, tm])
                
        msg = "Expected Tm's (%s) don't match observed Tm's (%s)." % \
            (self.expected_result_path, self.observed_result_path)
        self.assertTrue(filecmp.cmp(self.expected_result_path, 
                                    _OBSERVED_RESULT_FILENAME), msg)
                
#=============================================================================
# Main
#=============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()