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
import traceback

from . import app
from .crossdomain_decorator import crossdomain
from .apis.ApiManager import ApiManager, API_BASE_ROUTE, API_DOCS_BASE_ROUTE
from .apis.ApiConstants import PAGE
from .utilities.logging_utilities import APP_LOGGER 

from flask import jsonify, abort, make_response, request
from collections import defaultdict

#===============================================================================
# Public Global Variables
#===============================================================================
API_MANAGER = ApiManager()
ORIGIN      = '*'

#===============================================================================
# APIs
#===============================================================================
@app.route('/')
@crossdomain(origin=ORIGIN)
def index():
    return "Hello, World!"

@app.route(API_DOCS_BASE_ROUTE)
@crossdomain(origin=ORIGIN)
def api_resource_listing():
    swagger_resource_listing = API_MANAGER.getSwaggerResourceListing()
    if swagger_resource_listing:
        return jsonify(swagger_resource_listing)
    abort(404)

@app.route("%s/<version>/<name>" % API_DOCS_BASE_ROUTE)
@crossdomain(origin=ORIGIN)
def api_declarations(version, name):
    swagger_api_declaration = API_MANAGER.getSwaggerApiDeclaration(name, version)
    if swagger_api_declaration:
        return jsonify(swagger_api_declaration)
    abort(404)
    
@app.route("%s/<version>/<name>" % API_BASE_ROUTE)
@crossdomain(origin=ORIGIN)
def api(version, name):
    #REPLACE WITH HTML DOCS!!!
    swagger_api_declaration = API_MANAGER.getSwaggerApiDeclaration(name, version)
    if swagger_api_declaration:
        return jsonify(swagger_api_declaration)
    abort(404)

@app.route('%s/<version>/<name>/<path:path>' % API_BASE_ROUTE, methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@crossdomain(origin=ORIGIN, headers="Origin, X-Requested-With, Content-Type, Accept")
def function(version, name, path):
    try:
        version = version.lower()
        api_function = API_MANAGER.get_api_function(name, version, path, request.method)
        if api_function:
            
            # For example path "MeltingTemperatures/IDT/{name}/{sequence}", 
            # dynamic_path_fields would be [<name>, <sequence>]
            dynamic_path   = path[len(api_function.static_path()):]
            dynamic_path   = dynamic_path.lstrip(os.path.sep)
            dynamic_fields = dynamic_path.split(os.path.sep)
            
            # Make query parameter keys case-insensitive - force them all to lower 
            query_params = defaultdict(list)
            for k in request.args.keys():
                for arg in request.args.getlist(k):
                    query_params[k.lower()].extend(arg.split(","))
            for k,v in request.files.iteritems():
                if isinstance(v,(list,tuple)):
                    query_params[k.lower()].extend(v)
                else:
                    query_params[k.lower()].append(v)
                    
            response, _, page_info = api_function.handle_request(query_params, dynamic_fields)
            if response:
                pagination_headers = create_link_headers(api_function, request, page_info)
                if pagination_headers:
                    response.headers["Link"] = ",".join(pagination_headers)
                return response
    except:
        APP_LOGGER.info("Error processing API request: %s" % traceback.format_exc())
        abort(500)
    abort(404)
    
def create_link_headers(api_function, request, pagination_info):
    pagination_headers = list()
    if pagination_info:
        page      = pagination_info[0]
        num_pages = pagination_info[2]
        request_url = request.url
        cur_page_string = "%s=%d" % (PAGE, page)
        if page > 1:
            if cur_page_string in request_url:
                first_page_url = request_url.replace(cur_page_string,"%s=%d" % (PAGE, 1))
                prev_page_url  = request_url.replace(cur_page_string,"%s=%d" % (PAGE, page-1))
            else:
                first_page_url = request_url + "&%s=%d" % (PAGE, 1)
                prev_page_url  = request_url + "&%s=%d" % (PAGE, page-1)
            
            pagination_headers.append("<%s>; rel=\"first\"" % first_page_url)
            pagination_headers.append("<%s>; rel=\"previous\"" % prev_page_url)
        if page < num_pages:
            if cur_page_string in request_url:
                next_page_url = request_url.replace("%s=%d" % (PAGE, page),"%s=%d" % (PAGE, page+1))
                last_page_url = request_url.replace("%s=%d" % (PAGE, page),"%s=%d" % (PAGE, num_pages))
            else:
                next_page_url = request_url + "&%s=%d" % (PAGE, page+1)
                last_page_url = request_url + "&%s=%d" % (PAGE, num_pages)
            pagination_headers.append("<%s>; rel=\"next\"" % next_page_url)
            pagination_headers.append("<%s>; rel=\"last\"" % last_page_url)
    return pagination_headers

#===============================================================================
# Helper Functions
#===============================================================================
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)