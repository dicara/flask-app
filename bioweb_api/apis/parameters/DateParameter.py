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

#=============================================================================
# Imports
#=============================================================================
import re

from datetime import datetime

from bioweb_api.apis.parameters.AbstractParameter import AbstractParameter 
from bioweb_api.apis.ApiConstants import SWAGGER_TYPES, SWAGGER_FORMATS

#=============================================================================
# Private Global Variables
#=============================================================================
_DATE_PATTERN = re.compile("^20[0-9]{2}_[0-9]{2}_[0-9]{2}$")

#=============================================================================
# Class
#=============================================================================
class DateParameter(AbstractParameter):
    '''
    This parameter parses a date parameter (of the form YYYY_MM_DD) provided in 
    the api call and translates it into a datetime object for searching the 
    database.
    '''

    #===========================================================================
    # Constructors
    #===========================================================================    
    ''' '''
    def __init__(self, name, description, required=False, allow_multiple=True, 
                 default=None, enum=None):
        super(DateParameter, self).__init__(name, name, description,
                                            required=required, 
                                            allow_multiple=allow_multiple)
        
        self._default = default
        self._format  = SWAGGER_FORMATS.date                # @UndefinedVariable
        self._enum    = enum
        
        if self.default and not _DATE_PATTERN.match(self.default):
            raise Exception("Default date (%s) doesn't match accepted pattern: YYYY_MM_DD." % self.default)

        if self.enum:
            for date in self.enum:
                if not _DATE_PATTERN.match(date):
                    raise Exception("Enum date (%s) doesn't match accepted pattern: YYYY_MM_DD." % date)
            self._ensure_default_in_enum()
        
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    @property
    def type(self):
        return SWAGGER_TYPES.string                         # @UndefinedVariable
    
    def _convert_args(self, raw_args):
        dates = map(self.__convert_date, raw_args)
        if self.enum:
            valid_dates = set(map(self.__convert_date, self.enum))
            if not set(dates).issubset(valid_dates):
                invalid_dates = set(dates).difference(valid_dates)
                raise Exception("Provided arguments %s not a subset of valid arguments: %s" % (invalid_dates, valid_dates))
        return dates
    
    #===========================================================================
    # Public Instance Methods
    #===========================================================================    
    
    @staticmethod
    def __convert_date(value):
        if isinstance(value, datetime):
            return value
        return datetime.strptime(value, "%Y_%m_%d")
 
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    print _DATE_PATTERN.match("2014_02_03")
#     parameter = DateParameter("DateParameter", "DateParameter description.",
#                               enum=['2014_02_05', '2013_02_04'])
#     print parameter
#     print parameter._convert_args(['2014_02_05'])