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
    @staticmethod
    def insert(collection, rows):
        return DB[collection].insert(rows)
    
    @staticmethod
    def find(collection, criteria, projection):
        return list(DB[collection].find(criteria, projection))
    
    @staticmethod
    def distinct(collection, column_name):
        return list(DB[collection].distinct(column_name))
    
    @staticmethod
    def remove(collection, criteria):
        return DB[collection].remove(criteria)
    
    @staticmethod
    def get_distinct(collection, column_name, is_string=True):
        '''
        Call distinct on the provide column_name in the provided collection. If
        the column contains strings, then return case-insensitively sorted 
        results. Otherwise, simply sort the results.
        '''
        if is_string:
            return sorted(filter(lambda x: x is not None, 
                                 DB[collection].distinct(column_name)), 
                          key=lambda s: s.lower())
        else:
            return sorted(filter(lambda x: x is not None, 
                                 DB[collection].distinct(column_name)))
            
    @staticmethod
    def find_one(collection, column_name, column_value):
        print "colname %s" % column_name
        print "colval %s" %column_value
        return DB[collection].find({column_name: str(column_value)}), DB[collection].find_one({column_name: str(column_value)}), DB[collection].find_one()
            
#===========================================================================
# Ensure the initial instance is created.
#===========================================================================    
DbConnector.Instance()