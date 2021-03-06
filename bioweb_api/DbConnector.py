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
from pymongo import MongoClient
from pymongo.results import BulkWriteResult

from . import DATABASE_URL, DATABASE_PORT, DATABASE_NAME

#=============================================================================
# Connect to MongoDB
#=============================================================================
_CLIENT = MongoClient(DATABASE_URL, DATABASE_PORT, connect=False)
_DB     = _CLIENT[DATABASE_NAME]

#===============================================================================
# Class
#===============================================================================
class DbConnector(object):
    '''
    This class is intended to be a singleton. It handles communication (i.e.
    queries) with MongoDB. Every call to the _DB should go through this
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
    def insert(collection, records):
        '''
        This function performs a MongoDB insert. The insert command signature is
        db.collection.insert(<collection>, <records>). Collection is the
        name of the collection to receive the records.  Records
        specifies the documents to insert.

        Note that Mongo raises an exception if 'records' is empty.  This
        routine guards against an empty insert, and just supplies a return
        value for zero records inserted.

        @param collection   - Name of collection to perform find on.
        @param records      - List of documents to insert.

        @return WriteResult - a standard Mongo result object.
        '''
        if len(records) > 0:
            return _DB[collection].insert(records)
        else:
            return BulkWriteResult({ "nInserted" : 0 })

    @staticmethod
    def find(collection, criteria, projection=None):
        '''
        This function performs a MongoDB find. The find command signature is
        db.collection.find(<criteria>, <projection>). Criteria are the search
        terms (pass an empty dictionary {} to return all documents). Projection
        specifies the fields to return (pass None to return all documents).

        @param collection - Name of collection to perform find on.
        @param criteria   - Dictionary of search terms. Empty dictionary or None
                            to return all records.
        @param projection - Array of field names to return. None to return all.

        @return List of records - empty list if no records are found.
        '''
        return list(_DB[collection].find(criteria, projection))

    @staticmethod
    def find_one(collection, field_name, field_value):
        '''
        This function performs a MongoDB find_one. The first record with the
        provided field_name and field_value will be returned.

        @param collection  - Name of collection to perform find on.
        @param field_name  - Name of field to search for.
        @param field_value - Value of field to search for.

        @return First record found meeting search criteria.
        '''
        return _DB[collection].find_one({field_name: field_value})

    @staticmethod
    def find_max(collection, field_name):
        """
        This function performs a MongoDB find_one and returns a document with
        maximum value in field_name.

        @param collection  - Name of collection to perform find on.
        @param field_name  - Name of field to search for.
        """
        return _DB[collection].find_one(sort=[(field_name, -1)])

    @classmethod
    def find_from_params(cls, collection, params_dict, fields):
        '''
        This function performs a MongoDB find. The find command signature is
        db.collection.find(<criteria>, <projection>). This function generates
        the proper criteria dictionary from params_dict. The <projection> is
        simply the provided fields.

        @param collection   - Name of collection to perform find on.
        @param params_dict  - Dictionary of parameters to use as search criteria.
        @param fields       - List of field names to return in resultant records.

        @return List of records found that meet the search criteria.
        '''
        criteria = { param.name: {"$in": v} for param,v in params_dict.items() }
        return cls.find(collection, criteria, fields)

    @staticmethod
    def distinct(collection, column_name):
        '''
        Call distinct on the provide column_name in the provided collection.
        '''
        return list(_DB[collection].distinct(column_name))


    @classmethod
    def distinct_sorted(cls, collection, column_name, is_string=True):
        '''
        Call distinct on the provide column_name in the provided collection. If
        the column contains strings, then return case-insensitively sorted
        results. Otherwise, simply sort the results.
        '''
        if is_string:
            return sorted(filter(lambda x: x is not None,
                                 cls.distinct(collection, column_name)),
                          key=lambda s: s.lower())
        else:
            return sorted(filter(lambda x: x is not None,
                                 cls.distinct(collection, column_name)))

    @staticmethod
    def remove(collection, criteria, parameters={}):
        return _DB[collection].remove(criteria, parameters)

    @staticmethod
    def update(collection, query, update):
        _DB[collection].update(query, update)

    @staticmethod
    def save(collection, document):
        _DB[collection].save(document)

#===========================================================================
# Ensure the initial instance is created.
#===========================================================================
DbConnector.Instance()

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    from . import PA_PROCESS_COLLECTION
    db_connector = DbConnector.Instance()
    print db_connector.find(PA_PROCESS_COLLECTION,None,None)
