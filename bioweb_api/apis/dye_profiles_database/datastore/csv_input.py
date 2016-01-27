import pickle

import pandas

from bioweb_api.apis.dye_profiles_database.constants import DYE_NAME, LOT_NUMBER, \
    MANUFACTURER, DATE, DETECTION_CHIP_TYPE, USER, INSTRUMENT, LINE_RATE, \
    LASER_POWER, OIL_PSI, DROP_PSI, GAIN, CONCENTRATION_UGML, PEAK_INTENSITY, \
    NORMALIZED_PROFILE_PATH
from bioweb_api.apis.dye_profiles_database.datastore.detections import Detection, Detections
from bioweb_api.apis.dye_profiles_database.datastore.dye_stocks import DyeStock, DyeStocks
from bioweb_api.apis.dye_profiles_database.datastore.profiles import Profile, Profiles

DYE_STOCK_FIELDS = [
    LOT_NUMBER,
    DYE_NAME,
    MANUFACTURER,
]

DETECTION_FIELDS = [
    LASER_POWER,
    GAIN,
    LINE_RATE,
    OIL_PSI,
    DROP_PSI,
    INSTRUMENT,
    USER,
    DETECTION_CHIP_TYPE,
    DATE,
]


class CsvInput(object):
    """
    A wrapper for entering profiles into profile database through a csv file.
    All objects (DyeStocks, Detections, and Profiles) are checked
    """
    def __init__(self, csv_path, delimiter='\t'):
        """
        @param csv_path:    String, path to csv file
        @param delimiter:   String, csv delimiting character
        """
        self.csv_data = pandas.read_csv(csv_path, sep=delimiter)
        self.dye_stocks = DyeStocks()
        self.detections = Detections()
        self.profiles = Profiles()

    def parse(self):
        """
        Run this to parse the data from the csv file and create the
        objects needed for entry into the database.  Any errors (invalid data\
        types, missing fields) will be detected here.
        """
        self.get_dye_stocks()
        self.get_detections()
        self.get_profiles()

    def get_dye_stocks(self):
        """
        Generate DyeStock objects.
        """
        for _, row in self.csv_data[DYE_STOCK_FIELDS].drop_duplicates().iterrows():
            new_ds = DyeStock(dye_name=row[DYE_NAME],
                              lot_number=row[LOT_NUMBER],
                              manufacturer=row[MANUFACTURER])
            self.dye_stocks.append(new_ds)

    def get_detections(self):
        """
        Generate Detection objects.
        """
        for _, row in self.csv_data[DETECTION_FIELDS].drop_duplicates().iterrows():
            new_detection = Detection(date=str(row[DATE]),
                                      detection_chip_type=row[DETECTION_CHIP_TYPE],
                                      user=row[USER],
                                      instrument=row[INSTRUMENT],
                                      line_rate=row[LINE_RATE],
                                      laser_power=row[LASER_POWER],
                                      oil_psi=row[OIL_PSI],
                                      drop_psi=row[DROP_PSI],
                                      gain=row[GAIN])
            self.detections.append(new_detection)

    def get_profiles(self):
        """
        Generate Profile objects
        """
        for _, row in self.csv_data.iterrows():
            dye_stock_uuid = self.dye_stocks.find_uuid(
                                dye_name=row[DYE_NAME],
                                lot_number=row[LOT_NUMBER],
                                manufacturer=row[MANUFACTURER])

            detection_uuid = self.detections.find_uuid(date=str(row[DATE]),
                                                  detection_chip_type=row[DETECTION_CHIP_TYPE],
                                                  user=row[USER],
                                                  instrument=row[INSTRUMENT],
                                                  line_rate=row[LINE_RATE],
                                                  laser_power=row[LASER_POWER],
                                                  oil_psi=row[OIL_PSI],
                                                  drop_psi=row[DROP_PSI],
                                                  gain=row[GAIN])

            # csv file must specify path to a pickled list containing
            # the normalized dye profile
            with open(row[NORMALIZED_PROFILE_PATH]) as fh:
                profile = pickle.load(fh)

            new_profile = Profile(dye_stock_uuid=dye_stock_uuid,
                                  detection_uuid=detection_uuid,
                                  profile=profile,
                                  concentration_ugml=float(row[CONCENTRATION_UGML]),
                                  peak_intensity=row[PEAK_INTENSITY])
            self.profiles.append(new_profile)

    def populate_database(self):
        """
        Adds the data to the database. Run this only after parsing
        all database entries.  That way errors will be detected before
        database entry.
        """
        self.dye_stocks.add_new_dye_stocks()
        self.detections.add_new_detections()
        self.profiles.add_new_profiles()


if __name__ == '__main__':
    ci = CsvInput('/home/nbrown/Desktop/profile_db/profiles_working/database_entries.csv')
    ci.parse()
    ci.populate_database()