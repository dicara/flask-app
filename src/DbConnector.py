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
from . import DB

#===============================================================================
# Class
#===============================================================================
class DbConnector(object):
    '''
    This class is intended to be a singleton. It handles communication (i.e.
    queries) with MongoDB. Every call to the DB should go through this 
    class.
    '''
    _INSTANCE = None
    
    #===========================================================================
    # Constructor
    #===========================================================================
    def __init__(self):
        # Enforce that it's a singleton
        if self._INSTANCE:
            raise Exception("%s is a singleton and should be accessed through the Instance method." % self.__class__.__name__)
    
    @classmethod
    def Instance(cls):
        if not cls._INSTANCE:
            cls._INSTANCE = DbConnector()
        return cls._INSTANCE
    
    #===========================================================================
    # Simple get methods
    #===========================================================================
    def insert(self, collection, rows):
        return DB[collection].insert(rows)
    
    def find(self, collection, criteria, projection):
        return list(DB[collection].find(criteria, projection))
    
    def distinct(self, collection, column_name):
        return list(DB[collection].distinct(column_name))
    
    def remove(self, collection, criteria):
        return DB[collection].remove(criteria)
        
#===========================================================================
# Ensure the initial instance is created.
#===========================================================================    
DbConnector.Instance()