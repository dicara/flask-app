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
@date:   Jun 1, 2014
'''

#===============================================================================
# Imports
#===============================================================================
import os
from src import server
from setuptools import setup, find_packages

#===============================================================================
# Private global variables
#===============================================================================
_README           = os.path.join(os.path.dirname(__file__), 'README')
_LONG_DESCRIPTION = open(_README).read()

#===============================================================================
# Setup
#===============================================================================
setup(
      name             = 'flask-api',
      version          = server.__version__,
      author           = 'Dan DiCara',
      author_email     = 'ddicara@gnubio.com', 
      entry_points     = {'console_scripts': [
                                          'flask_api = src.server:main',
                                         ]},
      packages         = find_packages(),
      install_requires = [
                          'pymongo==2.7',
                          'pyyaml==3.10',
                          'simplejson==3.3.1',
                          'Flask==0.10.1',
                          'tornado==3.2',
                          'redis==2.9.1',
                          'suds==0.4',
                          'nose==1.3.3',
                          'futures==2.1.6',
                         ],
      package_data     = {'': ['src/templates/*'],},
      description      = _LONG_DESCRIPTION,
      test_suite       = 'nose.collector',
      zip_safe         = False,
)