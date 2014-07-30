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
@date:  Jul 23, 2014
'''


#=============================================================================
# Imports
#=============================================================================
import os
import subprocess

from collections import namedtuple
from src import USER_HOME_DIR
from src.utilities.logging_utilities import APP_LOGGER

#=============================================================================
# Public Global Variables
#=============================================================================
PA_TOOL_TUPLE = namedtuple("PaTool", ["process", "devices", "dyes", "plots"])
PA_TOOL       = PA_TOOL_TUPLE(*PA_TOOL_TUPLE._fields)

#############################################################################
#  Tool     # Description                                                   #   
#############################################################################
# barcodes  # Converts drop profiles into barcodes                          #
# cluster   # Finds clusters of drop profiles                               #
# convert   # Convert a list of images into the specified image format      #
# devices   # Lists the names of known devices                              #
# drops     # Extracts drop profiles from an image.                         #
# dyes      # Provides information about the available dye profiles         #
# extract   # Extract dye profiles from a profile run                       #
# model     # Calculates the dye model that best fits the provided profiles #
# process   # Extracts drop information from a list of image files          #
# profiles  # Constructs an drop profiles from barcodes                     #
# simulate  # Creates simulated TDI images                                  # 
# plots     #                                                               #
#############################################################################

#=============================================================================
# Private Global Variables
#=============================================================================
PA_PATH = os.path.join(USER_HOME_DIR, "bin", "pa")

#=============================================================================
# Class
#=============================================================================
class PrimaryAnalysisJob(object):

    #===========================================================================
    # Constructor
    #===========================================================================    
    def __init__(self, pa_tool, *args, **kwargs):
        if pa_tool not in PA_TOOL:
            raise Exception("Unrecognized primary analysis tool: %s." % 
                            pa_tool)

        self._pa_tool = pa_tool
        
        # Collect command line arguments        
        cmd_args = [PA_PATH, pa_tool]
        for key, value in kwargs.items():
            if key.startswith("-"):
                cmd_args.append(key)
            elif len(key) == 1:
                cmd_args.append("-" + key)
            else:
                cmd_args.append("--" + key)
            
            if not value:
                continue
            
            if isinstance(value, list):
                cmd_args.extend(list)
            else:
                cmd_args.append(value)
        
        cmd_args.extend(args)
        
        self._cmd_args= cmd_args
        
        
    def run(self):
        APP_LOGGER.info("Running primary analysis job: %s" % self._pa_tool)
        process = subprocess.Popen(self._cmd_args, stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        return process.communicate()        