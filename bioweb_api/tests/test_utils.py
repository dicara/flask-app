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
@date:  Sep 30, 2014
'''

#===============================================================================
# Imports
#===============================================================================
import os
import json
import yaml

from StringIO import StringIO

from bioweb_api.apis.ApiConstants import ERROR 

#===============================================================================
# Utility Functions
#===============================================================================
def upload_file(test_case, test_dir, url, filename, exp_resp_code):
    path = os.path.join(test_dir, filename)
    with open(path) as f:
        response = test_case._client.post(url, 
                                          data={'file': (StringIO(f.read()), filename)}
                                         )
    assert_response_code(test_case, exp_resp_code, response, url)
    return json.loads(response.data)

def post_data(test_case, url, exp_resp_code):
    response = test_case._client.post(url)
    assert_response_code(test_case, exp_resp_code, response, url)
    return json.loads(response.data)

def get_data(test_case, url, exp_resp_code):
    response = test_case._client.get(url)
    assert_response_code(test_case, exp_resp_code, response, url)
    return json.loads(response.data)

def delete_data(test_case, url, exp_resp_code):
    response = test_case._client.delete(url)
    assert_response_code(test_case, exp_resp_code, response, url)
    return json.loads(response.data)
    
def assert_response_code(test_case, exp_resp_code, response, url):
    msg = "Expected response code (%s) doesn't match observed (%s) for " \
          "%s." % (exp_resp_code, response.status_code, url)
    try:
        data = json.loads(response.data)
        print data
        msg = append_errors(data, msg)
    except:
        pass
    test_case.assertEqual(response.status_code, exp_resp_code, msg)
  
  
def append_errors(response_data, msg):
    """
    Recursively search through the response data for all error messages and
    append them to the provided error message.
    
    @param response_data: json response data from API call
    @param msg: assertion error message
    """
    if isinstance(response_data, dict):
        for key in response_data:
            if key == ERROR:
                msg += "\nERROR: %s" % response_data[ERROR]
            append_errors(response_data[key], msg)
    return msg
  
def read_yaml(yaml_path):
    if not os.path.isfile(yaml_path):
        raise Exception("Provided yaml file either doesn't exist or isn't " \
                        "a file: %s" % yaml_path)
    with open(yaml_path) as f:
        data = yaml.load(f.read())
    return data

def write_yaml(yaml_path, data_dict, allow_exists=True):
    if not allow_exists and os.path.exists(yaml_path):
        raise Exception("Provided yaml file output already exists: %s" % yaml_path)
    with open(yaml_path, 'w') as f:
        f.write( yaml.dump(data_dict, default_flow_style=True) )
        
def add_url_argument(url, key, value, first_argument=False):
    sep = "&"
    if first_argument:
        sep = "?"
    return url + "%s%s=%s" % (sep, key, value)