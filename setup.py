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
      name             = 'bioweb-api',
      version          = '3.27',
      author           = 'Dan DiCara',
      author_email     = 'ddicara@gnubio.com',
      entry_points     = {'console_scripts': [
                                          'bioweb_api = bioweb_api.server:main',
                                         ]},
      packages         = find_packages(),
      install_requires = [
                          'nose>=1.3.4',
                          'coverage>=3.7.1',
                          'pymongo>=2.7',
                          'pyyaml>=3.10',
                          'simplejson>=3.3.1',
                          'Flask>=0.10.1',
                          'tornado>=3.2',
                          'redis>=2.9.1',
                          'futures>=2.1.6',
                          'numpy>=1.9.1',
                          'idt-analyzer>=0.3',
                          'ncbi-utilities>=0.2',
                          'probe-design>=0.3',
                          'primary-analysis>=2.13',
                          'predator==0.1',
                          'secondary-analysis==1.69.2',
                          'experiment-database==0.10.1',
                          'PyPDF2>=1.25.1',
                          'reportlab>=3.3.0',
                          'profile-db==0.4.1',
                          'gbutils>=1.5',
                         ],
      package_data     = {'': ['bioweb_api/templates/*'],},
      description      = _LONG_DESCRIPTION,
      test_suite       = 'nose.collector',
      zip_safe         = False,
)
