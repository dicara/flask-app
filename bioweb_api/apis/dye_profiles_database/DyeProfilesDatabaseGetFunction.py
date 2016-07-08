#=============================================================================
# Imports
#=============================================================================
from bioweb_api import HOSTNAME
from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from profile_database.constants import DYE_STOCK_UUID, DETECTION_UUID, \
    DYE_NAME, DYE_FAM, DYE_JOE


from profile_database.datastore import Datastore

DYE_PROFILES_DATABASE = 'DyeProfilesDatabase'

#=============================================================================
# Class
#=============================================================================
class DyeProfilesDatabaseGetFunction(AbstractGetFunction):

    #===========================================================================
    # Overridden Methods
    #===========================================================================
    @staticmethod
    def name():
        return DYE_PROFILES_DATABASE

    @staticmethod
    def summary():
        return "Retrieve list of dye profiles."

    @staticmethod
    def notes():
        return ""

    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.format(),
                     ]
        return parameters

    @classmethod
    def process_request(cls, params_dict):
        data = Datastore(url=HOSTNAME).get_profiles()

        # remove uuids and mongo ids
        unneeded_ids = [DETECTION_UUID, DYE_STOCK_UUID]
        for profile in data:
            for id in unneeded_ids:
                del profile[id]

        # remove picoinjection and assay dyes
        not_barcode_dyes = {DYE_FAM, DYE_JOE}
        data = [profile for profile in data if profile[DYE_NAME] not in not_barcode_dyes]

        column_names = data[0].keys()
        return (data, column_names, None)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = DyeProfilesDatabaseGetFunction()
    print function