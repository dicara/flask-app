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
        self.idt_client = IDTClient()
        
        # Input Name,Sequence file
        input_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                  _PROBES_FILENAME)
        self.assertTrue(os.path.isfile(input_path))
        self.assertTrue(False)
        probes_dict = dict()
        with open(input_path) as f:
            f.readline()
            i = 0
            for line in f:
                fields = line.strip().split(",")
                probes_dict[fields[0]] = fields[1]
        self.probes_dict = probes_dict
        
        # Expected Name,Sequence/Tm file
        expected_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                     _EXPECTED_RESULT_FILENAME)
        self.assertTrue(os.path.isfile(expected_path))
        self.expected_result_path = expected_path

    def test_idt_client(self):
        observed_result_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                            _OBSERVED_RESULT_FILENAME)
        with open(observed_result_path, 'w') as f:
            print >>f, ",".join(["Name","Sequence","Tm"])
            for i, (k,v) in enumerate(self.probes_dict.iteritems()):
                print "%s:\t%s\t%s" % (str(i),k,v)
                melting_temp = self.idt_client.get_melting_temp(v)
                print melting_temp
                print >>f, ",".join([k,v,str(melting_temp.tm)])
        
        msg = "%s file not found." % _OBSERVED_RESULT_FILENAME
        self.assertTrue(os.path.isfile(observed_result_path), msg)
        msg = "Observed result (%s) doesn't match expected result (%s)" % (observed_result_path, self.expected_result_path)
        self.assertTrue(filecmp.cmp(self.expected_result_path, 
                                    observed_result_path), msg)
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()