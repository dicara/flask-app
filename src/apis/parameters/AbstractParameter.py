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

from abc import ABCMeta, abstractmethod, abstractproperty

from src.apis.ApiConstants import PARAMETER_TYPES
from src.utilities.logging_utilities import APP_LOGGER

#=============================================================================
# Private Global Variables
#=============================================================================
_RE_TYPE         = type(re.compile("test"))

#=============================================================================
# Class
#=============================================================================
class AbstractParameter(object):
    __metaclass__ = ABCMeta
    
    ''' 
    An inherited instance of this class represents an input parameter to an API 
    function. It's name must match the column name in the database on which the 
    parameter is filtering. Instances of this class are used as keys in 
    parameter dictionaries. Therefore, the __hash__ and __eq__ methods are 
    implemented. Please note that only the name and alias are used to generate 
    the hash and evaluate equality. This is due to the fact that two different 
    parameters with the same name and alias should NEVER be defined on the same 
    API function. Also, the alias is strictly for use in generating the Swagger
    docs. It allows the mappping of non-descriptive column names in the database 
    to a more relevant names in the Swagger UI.
    
    NOTE: When the case_sensitive flag is set to True, the parameters returned
    by parse_args are no longer strings, but rather compiled case insensitive
    regex's that are interpreted by MongoDb. Furthermore, the _type 
    input argument is used to convert input strings to their appropriate type
    when parse_args is called (e.g. dates to datetime objects, numbers to ints 
    and floats, etc.).
    
    The properties in this class were derived based on the Swagger Parameter 
    shema found here:
    
    https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#524-parameter-object
    '''

    #===========================================================================
    # Constructors
    #===========================================================================    
    def __init__(self, name, alias, description, 
                 param_type=PARAMETER_TYPES.query,          # @UndefinedVariable
                 required=False, allow_multiple=True):
        '''
        Constructor
        '''
        # Swagger Parameter Object fields
        self._name           = self._ensureNotNone("name", name)
        self._alias          = self._ensureNotNone("alias", alias)
        self._description    = self._ensureNotNone("description", description)
        self._param_type     = self._ensureNotNone("param_type", param_type)
        self._required       = required
        self._allow_multiple = allow_multiple
        
        self._type          = None
        self._ref           = None
        self._format        = None
        self._default       = None
        self._enum          = None
        self._minimum       = None
        self._maximum       = None
        self._items         = None
        self._unique_items  = None
        self._equality      = None
        
        if self.param_type not in PARAMETER_TYPES:
            raise Exception("Unrecognized parameter type: %s." % self.param_type)

        if not isinstance(self.required, bool):
            raise Exception("Required type parameter must be a boolean but found: %s" % type(self.required))
        
        if not isinstance(self.allow_multiple, bool):
            raise Exception("Allow multiple parameter must be a boolean but found: %s" % type(self.allow_multiple))
 
    #===========================================================================
    # Abstract Methods
    #===========================================================================
    @abstractproperty
    def type(self):
        '''
        This is either a Swagger defined Primitive 
        (https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#431-primitives), 
        an array, or Swagger model id. It describes the input value type for 
        this query/path parameter. Documentation can be found at the following 
        link.
        
        https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#dataTypeType
        '''

        raise NotImplementedError("AbstractParameter subclass must implement _type property.")
        
    @abstractmethod
    def _convert_args(self, raw_args):
        ''' 
        This ensures that the input args are valid (e.g. if it's a number, is it
        within the allowable min/max range, or if an enum is provided, is this
        value included in the enum) and converts them to the correct type (e.g.
        int, float, date, string, etc.). 
        '''
        raise NotImplementedError("AbstractParameter subclass must implement _convert_args function.")
         
    #===========================================================================
    # Public Instance Methods
    #===========================================================================    
    def is_path(self):
        return self.param_type == PARAMETER_TYPES.path      # @UndefinedVariable
    
    def getParameterDict(self):
        param_dict = dict()
        param_dict["name"]          = self.alias
        param_dict["description"]   = self.description
        param_dict["paramType"]     = self.param_type
        param_dict["required"]      = self.required
        param_dict["allowMultiple"] = self.allow_multiple
        
        if self.type:
            param_dict["type"] = self.type
        if self.ref:
            param_dict["ref"] = self.ref
        if self.format:
            param_dict["format"] = self.format
        if self.default:
            param_dict["defaultValue"] = self.default
        if self.enum:
            param_dict["enum"] = self.enum
        if self.minimum:
            param_dict["minimum"] = self.minimum
        if self.maximum:
            param_dict["maximum"] = self.maximum
        if self.items:
            param_dict["items"] = self.items
        if self.unique_items:
            param_dict["uniqueItems"] = self.unique_items
            
        return param_dict
    
    def parse_args(self, raw_args):
        '''
        Convert input strings to their appropriate types.
        '''
        if len(raw_args) > 1 and not self.allow_multiple:
            APP_LOGGER.warning("Multiple parameter values for %s are not permitted. Only using the first value: %s." % (self.name, raw_args[0]))
            raw_args = raw_args[:1]
         
        if len(raw_args) < 1:
            if self.default:
                raw_args = [self.default]
            elif self.required:
                raise Exception("Required argument %s not provided." % self.name)
            
        return self._convert_args(raw_args)
    
    def _ensure_default_in_enum(self):
        if self.default and self.enum and self.default not in self.enum:
            raise Exception("Default (%s) not found in enum: %s" % (self.default, self.enum))
    
    #===========================================================================
    # Immutable Properties
    #===========================================================================    
    
    @property
    def name(self):
        ''' Internally used name (e.g. document attribute name for searching/filtering a database query).'''
        return self._name
        
    @property
    def alias(self):
        ''' Name of the parameter the user specifies in the RESTful API call.'''
        return self._alias
        
    @property
    def description(self):
        ''' Brief description of parameter for display in SWAGGER UI and docs. '''
        return self._description
        
    @property
    def param_type(self):
        return self._param_type
        
    @property
    def required(self):
        ''' Is this parameter required or not. '''
        return self._required

    @property
    def allow_multiple(self):
        ''' Are multiple values permitted or not. '''
        return self._allow_multiple
    
    @property
    def ref(self):
        return self._ref
    
    @property
    def format(self):
        return self._format
    
    @property
    def default(self):
        ''' Deafult parameter values. '''
        return self._default
    
    @property
    def enum(self):
        ''' List of allowable parameter values. '''
        return self._enum
    
    @property
    def minimum(self):
        return self._minimum
    
    @property
    def maximum(self):
        return self._maximum
    
    @property
    def items(self):
        return self._items
    
    @property
    def unique_items(self):
        return self._unique_items
    
    @property
    def equality(self):
        return self._equality
    
    #===========================================================================
    # Private Instance Methods
    #===========================================================================    
    def __repr__(self):
        s = ""
        for k,v in self.getParameterDict().iteritems():
            s += "%s:%s\n" % (k,v)
        return s
    
    def __key(self):
        return (self.name, self.alias)
    
    def __hash__(self):
        ''' Parameter name/alias combination should be unique for any given api function. '''
        return hash(self.__key())
    
    def __eq__(self, other):
        ''' Parameter name/alias combination should be unique for any given api function. '''
        return type(self) == type(other) and self.__key() == other.__key()
    
    #===========================================================================
    # Private Methods
    #===========================================================================    
    @staticmethod
    def _ensureNotNone(field_name, value):
        if not value:
            raise Exception("Field cannot be None: %s." % field_name)
        return value
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    # This should fail with TypeError!!!
    parameter = AbstractParameter("test_parameter", "Test parameter.")
    print parameter