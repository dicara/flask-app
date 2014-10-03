'''
Copyright (c) 2013 The Broad Institute, Inc. 
SOFTWARE COPYRIGHT NOTICE 
This software and its documentation are the copyright of the Broad Institute,
Inc. All rights are reserved.

This software is supplied without any warranty or guaranteed support
whatsoever. The Broad Institute is not responsible for its use, misuse, or
functionality.

@author: Dan DiCara
@date:   Oct 3, 2014
'''

#=============================================================================
# Imports
#=============================================================================
import unittest

from datetime import datetime
from copy import deepcopy

from bioweb_api.utilities.io_utilities import clean_item, TIME_FORMAT

#=============================================================================
# Public Global Variables
#=============================================================================

#=============================================================================
# Private Global Variables
#=============================================================================

#=============================================================================
# Class
#=============================================================================
class Test(unittest.TestCase):
    def test_clean_item(self):
        item = {
                "Numbers": [float('NaN'), 1, 2.0],
                "Datetime": datetime.today(),
                "NestedDict": {
                                "a": [1,2,3,float('NaN')],
                                "b": datetime.today(),
                              },
                "NestedList": [
                                float('NaN'),
                                datetime.today(),
                                "a",
                                1,
                                3.0,
                               ]
               }  
        exp_clean_item = deepcopy(item)
        exp_clean_item["Numbers"][0] = None
        exp_clean_item["Datetime"]   = exp_clean_item["Datetime"].strftime(TIME_FORMAT)
        exp_clean_item["NestedDict"]["a"][3] = None
        exp_clean_item["NestedDict"]["b"] = exp_clean_item["NestedDict"]["b"].strftime(TIME_FORMAT)
        exp_clean_item["NestedList"][0] = None
        exp_clean_item["NestedList"][1] = exp_clean_item["NestedList"][1].strftime(TIME_FORMAT)
        obs_clean_item = clean_item(item)
        msg = "Expected clean item (%s) doesn't match observed (%s)."  % \
            (exp_clean_item, obs_clean_item)
        self.assertEqual(obs_clean_item, exp_clean_item, msg)
        
#=============================================================================
# Main
#=============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_clean_item']
    unittest.main()