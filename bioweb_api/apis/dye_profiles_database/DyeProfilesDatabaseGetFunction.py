
#=============================================================================
# Imports
#=============================================================================
from collections import OrderedDict

from bioweb_api.apis.AbstractGetFunction import AbstractGetFunction
from bioweb_api.apis.parameters.ParameterFactory import ParameterFactory
from bioweb_api.apis.dye_profiles_database.constants import DYE_STOCKS_COLLECTION, \
    DYE_NAME, LOT_NUMBER, MANUFACTURER, DYE_STOCK_UUID, LASER_POWER, GAIN, DATE, \
    CONCENTRATION_UGML, PEAK_INTENSITY, DETECTION_UUID, DETECTIONS_COLLECTION, \
    PROFILES_COLLECTION
from bioweb_api.apis.ApiConstants import ID

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
        return "Retrieve list of primary analysis process jobs."

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
        dye_stock_data = cls._DB_CONNECTOR.find(DYE_STOCKS_COLLECTION, {})
        detection_data = cls._DB_CONNECTOR.find(DETECTIONS_COLLECTION, {})

        columns                     = OrderedDict()
        columns[PEAK_INTENSITY]     = 1
        columns[CONCENTRATION_UGML] = 1
        columns[DYE_STOCK_UUID]     = 1
        columns[DETECTION_UUID]     = 1


        data = cls._DB_CONNECTOR.find(PROFILES_COLLECTION, {}, columns)

        # append detection and dye stock data to each profile
        for profile in data:
            # append detection data
            for detection in detection_data:
                if profile[DETECTION_UUID] == detection[DETECTION_UUID]:
                    profile[DATE] = detection[DATE]
                    profile[GAIN] = detection[GAIN]
                    profile[LASER_POWER] = detection[LASER_POWER]
                    break
            # append dye stock data
            for dye_stock in dye_stock_data:
                if profile[DYE_STOCK_UUID] == dye_stock[DYE_STOCK_UUID]:
                    profile[DYE_NAME] = dye_stock[DYE_NAME]
                    profile[LOT_NUMBER] = dye_stock[LOT_NUMBER]
                    break

        # remove uuids and mongo ids
        unneeded_ids = [ID, DETECTION_UUID, DYE_STOCK_UUID]
        for profile in data:
            for id in unneeded_ids:
                del profile[id]

        column_names = data[0].keys()

        return (data, column_names, None)

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = DyeProfilesDatabaseGetFunction()
    print function