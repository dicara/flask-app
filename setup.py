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
      version          = '3.91.0',
      author           = 'Dan DiCara',
      author_email     = 'ddicara@gnubio.com',
      entry_points     = {'console_scripts': [
                                          'bioweb_api = bioweb_api.server:main',
                                         ]},
      packages         = find_packages(),
      install_requires = [
                          'biopython>=1.69',
                          'coverage>=4.4.1',
                          'experiment-database>=0.17.3',
                          'Flask>=0.12.2',
                          'futures>=3.0.5',
                          'gb-algorithms>=0.12.7',
                          'gbutils>=2.5.4',
                          'idt-analyzer>=0.3',
                          'matplotlib>=1.5.3',
                          'ncbi-utilities>=0.2',
                          'nose>=1.3.7',
                          'numpy>=1.12.1',
                          'pandas>=0.19.2',
                          'predator==0.2',
                          'primary-analysis>=2.40',
                          'probe-design>=0.3',
                          'profile-db>=0.10',
                          'pymongo>=3.4.0',
                          'PyPDF2>=1.26.0',
                          'redis>=2.10.5',
                          'reportlab>=3.4.0',
                          'scikit-learn==0.18.0',
                          'secondary-analysis>=3.25.1',
                          'simplejson>=3.10.0',
                          'tornado>=4.5.1',
                         ],
      package_data     = {'': ['bioweb_api/templates/*'],},
      description      = _LONG_DESCRIPTION,
      test_suite       = 'nose.collector',
      zip_safe         = False,
)
