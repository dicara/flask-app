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
import stat
import errno
import csv
import collections
import numbers
import math

from datetime import datetime
from flask import make_response, jsonify

#===============================================================================
# Public Global Variables
#===============================================================================
TIME_FORMAT      = "%Y_%m_%d__%H_%M_%S"

#===============================================================================
# Utility Methods
#===============================================================================
def safe_make_dirs(dir_name):
    '''
    Makes directory structure, or ends gracefully if directory already exists
    '''
    try:
        os.makedirs(dir_name)
    except OSError, value:
        error_num = value.errno
        if error_num==183 or error_num==17 or error_num==errno.EEXIST:
            pass  # Directory already existed
        else:
            raise  # Reraise other errors
        
def silently_remove_file(filename):
    '''
    Attempt to remove a file, ignoring any thrown exceptions.
    '''
    try:
        os.remove(filename)
    except OSError:
        pass
    
def get_case_insensitive_dictreader(f, dialect, required_headers=None):
    '''
    Create a DictReader with the provided file handle and convert all headers to
    lowercase. If duplicate headers are found, raise an IOError. Similarly, if
    required_headers are included, raise an IOError if the file doesn't 
    contain any of the required headers.
    
    @param f       - File handle.
    @param dialect - Dialect of file being read.
    
    @return DictReader with all lowercase headers.
    '''
    reader = csv.DictReader(f, dialect=dialect)
    
    reader.fieldnames = map(lambda x: x.lower(), reader.fieldnames)
    
    # Ensure there aren't any duplicate headers.
    if len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise IOError("File contains duplicate headers: %s" % 
                      find_duplicates(reader.fieldnames))
        
    # Ensure that required headers are present in the file. 
    if required_headers and not set(reader.fieldnames) >= set(required_headers):
        raise IOError("Required headers are missing: %s" % 
                      list(set(required_headers) - set(reader.fieldnames)))
    
    return reader

def find_duplicates(in_list):
    '''
    Return a list of all duplicate items found in the provded list.
    '''
    return [x for x, y in collections.Counter(in_list).items() if y > 1]
    
def get_dialect(file_path, delimiters="\t,"):
    '''
    Return the dialect of the file. If dialect cannot be determined, return
    None. If the file doesn't exist, throw an IOError exception. 
    '''
    if not os.path.isfile(file_path):
        raise IOError("File not found: %s" % file_path)
    
    dialect = None
    with open(file_path) as f:
        try:
            dialect = csv.Sniffer().sniff(f.read(),delimiters=delimiters)
        except:
            pass
        
    return dialect

def get_python_mode(permissions):
    '''
    Given an array of permissions ([user, group, other] where 1=execute, 2=write, 
    and 4=read), determine the mode python can interpret to set the mode of a 
    path correctly.
    '''
    if len(permissions) != 3:
        raise Exception("Permissions array must contain 3 integer modes that are 1 <= mode <= 7, but array contained %s" % str(permissions))
    
    user  = permissions[0]
    group = permissions[1]
    other = permissions[2]
    
    mode = None
    if user == 1:
        mode = stat.S_IXUSR
    elif user == 2:
        mode = stat.S_IWUSR
    elif user == 3:
        mode = stat.S_IXUSR | stat.S_IWUSR
    elif user == 4:
        mode = stat.S_IRUSR
    elif user == 5:
        mode = stat.S_IXUSR | stat.S_IRUSR
    elif user == 6:
        mode = stat.S_IWUSR | stat.S_IRUSR
    elif user == 7:
        mode = stat.S_IXUSR | stat.S_IWUSR | stat.S_IRUSR
    else:
        raise Exception("User mode must be 1 <= mode <= 7 but is: %d" % mode)
    
    if group == 1:
        mode = mode | stat.S_IXGRP
    elif group == 2:
        mode = mode | stat.S_IWGRP
    elif group == 3:
        mode = mode | stat.S_IXGRP | stat.S_IWGRP
    elif group == 4:
        mode = mode | stat.S_IRGRP
    elif group == 5:
        mode = mode | stat.S_IXGRP | stat.S_IRGRP
    elif group == 6:
        mode = mode | stat.S_IWGRP | stat.S_IRGRP
    elif group == 7:
        mode = mode | stat.S_IXGRP | stat.S_IWGRP | stat.S_IRGRP
    else:
        raise Exception("Group mode must be 1 <= mode <= 7 but is: %d" % mode)
    
    if other == 1:
        mode = mode | stat.S_IXOTH
    elif other == 2:
        mode = mode | stat.S_IWOTH
    elif other == 3:
        mode = mode | stat.S_IXOTH | stat.S_IWOTH
    elif other == 4:
        mode = mode | stat.S_IROTH
    elif other == 5:
        mode = mode | stat.S_IXOTH | stat.S_IROTH
    elif other == 6:
        mode = mode | stat.S_IWOTH | stat.S_IROTH
    elif other == 7:
        mode = mode | stat.S_IXOTH | stat.S_IWOTH | stat.S_IROTH
    else:
        raise Exception("Other mode must be 1 <= mode <= 7 but is: %d" % mode)
    
    return mode

def make_clean_response(response, http_status_code):
    """
    Responses cannot contain python objects. Therefore, check that the response
    contains strings or numbers. If datetime is encountered, convert to a
    string. If NaN is encountered, convert it to None.
    
    @param response:
    @param http_status_code:
    """
    return make_response(jsonify(clean_item(response)), http_status_code)   

def clean_item(item):
    """
    This function ensures the provided item can be serialized and throws an 
    exception if not. Item may be a list, dict, string, number, or datetime 
    object. If the item is a list or dict, all of its elements must be a string, 
    number, or datetime object. Datetime objects are converted to strings of the
    form  YYYY_mm_dd__HH_MM_SS. Furthermore, NaN float values are converted to 
    None. The cleaned item is then returned.
    
    @param item: May be a list, dict, string, number, or datetime object.
    """
    if item is None:
        return None
    elif isinstance(item, list):
        for i in range(len(item)):
            item[i] = clean_item(item[i])
    elif isinstance(item, dict):
        for k,v in item.iteritems():
            item[k] = clean_item(v)
    elif isinstance(item, datetime):
        item = item.strftime(TIME_FORMAT)
    elif isinstance(item, basestring):
        pass
    elif isinstance(item, numbers.Number):
        # jsonify allows NaNs which are not valid json, so replace with None
        if isinstance(item, float) and math.isnan(item):
            item = None
    else:
        raise Exception("Unhandled type: %s" % type(item))
    
    return item