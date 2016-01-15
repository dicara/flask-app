#=============================================================================
# Imports
#=============================================================================
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.drop_tools.library_generation_utilities import BARCODE_DYES

#=============================================================================
# Class
#=============================================================================
class BarcodeLibraryDyesGetFunction(AbstractGetFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "BarcodeDyes"
   
    @staticmethod
    def summary():
        return "Retrieve list of available barcode dyes."
    
    @staticmethod
    def notes():
        return "Retrieve list of available barcode dyes."
    
    @classmethod
    def parameters(cls):
        cls.refresh_parameter = ParameterFactory.boolean("refresh", 
                                                         "Refresh available barcode dyes.",
                                                         default_value=False)
        parameters = [
                      cls.refresh_parameter,
                      ParameterFactory.format(),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        if cls.refresh_parameter in params_dict and \
           params_dict[cls.refresh_parameter][0]:
            BARCODE_DYES.keys()
            
        dyes = [{"dye": dye} for dye in BARCODE_DYES.keys()]
        return (dyes, None, None)
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = BarcodeLibraryDyesGetFunction()
    print function