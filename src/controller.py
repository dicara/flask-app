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
import flask

from . import app
from flask import jsonify, abort, make_response, request
from apis.idtClient import IDTClient
from pkg_resources import resource_filename #@UnresolvedImport
from .crossdomain_decorator import crossdomain

#===============================================================================
# Public Global Variables
#===============================================================================
ORIGIN      = '*'

#===============================================================================
# Functions
#===============================================================================
@app.route('/')
@crossdomain(origin=ORIGIN)
def index():
    return "Hello, World!"

@app.route('/MeltingTemps/Rest')
@crossdomain(origin=ORIGIN)
def melting_temp_rest():
    if "name" not in request.args:
        abort(404)
    elif "sequence" not in request.args:
        abort(404)
    
    name = request.args.getlist("name")[0]
    sequence = request.args.getlist("sequence")[0]
    
    idt_client = IDTClient()
    melting_temp = idt_client.get_melting_temp(sequence)
    
    return jsonify({"name": name, "sequence": sequence, "melting_temp": melting_temp})

@app.route('/MeltingTemps')
@crossdomain(origin=ORIGIN)
def melting_temp():
    templates_path = resource_filename(__name__,'templates')
    print templates_path
#     return flask.render_template(resource_filename(__name__,'templates/test.html'))
    return flask.render_template('test.html')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)