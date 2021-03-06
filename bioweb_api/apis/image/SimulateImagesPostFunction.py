'''
Copyright 2015 Bio-Rad Laboratories, Inc.

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
@date:   Mar 4, 2015
'''

#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractPostFunction import AbstractPostFunction

#=============================================================================
# Public Static Variables
#=============================================================================
SIMULATE_IMAGES = "SimulateImages"

#=============================================================================
# Private Static Variables
#=============================================================================

#=============================================================================
# Class
#=============================================================================
class SimulateImagesPostFunction(AbstractPostFunction):
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return SIMULATE_IMAGES
   
    @staticmethod
    def summary():
        return "Generate simulated TDI images."
    
    @staticmethod
    def notes():
        return ""

    def response_messages(self):
        msgs = super(SimulateImagesPostFunction, self).response_messages()
        msgs.extend([
                     { "code": 403, 
                       "message": "Image stack already exists. Delete the " \
                                  "existing image stack and retry."},
                     { "code": 404, 
                       "message": "Submission unsuccessful. No experiment " \
                       "definition found matching input criteria."},
                     { "code": 415, 
                       "message": "File is not a valid image stack " \
                                  "tarball."},
                    ])
        return msgs
    
    @classmethod
    def parameters(cls):
        cls._file_param       = ParameterFactory.file("Image stack tgz file.")
        cls._exp_defs_param   = ParameterFactory.experiment_definition()
        cls._name_param       = ParameterFactory.cs_string(NAME,
            "Unique name to give this image stack.")
        cls._short_desc_param = ParameterFactory.cs_string(DESCRIPTION, 
            "Short description of image stack.")

        parameters = [
                      cls._file_param,
                      cls._exp_defs_param,
                      cls._name_param,
                      cls._short_desc_param,
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        image_stack_tgz  = params_dict[cls._file_param][0]
        exp_def_name     = params_dict[cls._exp_defs_param][0]
        img_stack_name   = params_dict[cls._name_param][0]
        short_desc       = params_dict[cls._short_desc_param][0]
        http_status_code = 200
        uuid             = str(uuid4())
        tmp_archive_path = os.path.join(TMP_PATH, uuid)
        archive_path     = os.path.join(RESULTS_PATH, uuid + ".tgz")
        json_response    = { 
                            FILENAME: image_stack_tgz.filename,
                            UUID: uuid,
                            DATESTAMP: datetime.today(),
                           }

        if img_stack_name in cls._DB_CONNECTOR.distinct(IMAGES_COLLECTION, NAME):
            http_status_code = 403
            json_response[ERROR] = "Image stack with given name already " \
                        "exists."
        else:
            try:
                exp_defs         = ExperimentDefinitions()
                exp_def_uuid     = exp_defs.get_experiment_uuid(exp_def_name)
    
                if not exp_def_uuid:
                    http_status_code = 404
                    json_response[ERROR] = "Couldn't locate UUID for " \
                        "experiment definition."
                else:
                    image_stack_tgz.save(tmp_archive_path)
                    image_stack_tgz.close()
                    
                    if not tarfile.is_tarfile(tmp_archive_path):
                        http_status_code = 415
                        json_response[ERROR] = "File is not a valid tarfile."
                    else:
                        # Ensure stack contains bin or png images
                        archive = tarfile.open(tmp_archive_path, mode='r')
                        imgs = list()
                        for ext in VALID_IMAGE_EXTENSIONS:
                            imgs += fnmatch.filter(archive.getnames(), 
                                                       '*.%s' % ext)
                        if len(imgs) < 1:
                            http_status_code = 415
                            json_response[ERROR] = "No images found in " \
                                "provided archive."
                        else:
                            url = "http://%s/results/%s/%s" % (HOSTNAME, PORT, 
                                uuid)
                            shutil.copy(tmp_archive_path, archive_path)
                            json_response[RESULT]       = archive_path
                            json_response[URL]          = url
                            json_response[NAME]         = img_stack_name
                            json_response[DESCRIPTION]  = short_desc
                            json_response[EXP_DEF_NAME] = exp_def_name
                            json_response[EXP_DEF_UUID] = exp_def_uuid
                            json_response[NUM_IMAGES]   = len(imgs)
                            cls._DB_CONNECTOR.insert(IMAGES_COLLECTION, 
                                                     [json_response])
            except IOError:
                http_status_code     = 415
                json_response[ERROR] = str(sys.exc_info()[1])
            except:
                http_status_code     = 500
                json_response[ERROR] = str(sys.exc_info()[1])
            finally:
                if ID in json_response:
                    del json_response[ID]
                silently_remove_file(tmp_archive_path)
        
        return make_clean_response(json_response, http_status_code)
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = SimulateImagesPostFunction()
    print function                