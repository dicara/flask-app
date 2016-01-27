import datetime
import uuid

from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.dye_profiles_database.constants import VALID_INSTRUMENTS, \
    VALID_DETECTION_CHIP_TYPES, DETECTIONS_COLLECTION, DATE, DETECTION_CHIP_TYPE, \
    USER, INSTRUMENT, LINE_RATE, LASER_POWER, OIL_PSI, DROP_PSI, GAIN, \
    DETECTION_UUID


class Detections(object):
    def __init__(self, new_detections=None):
        """
        @param new_detections:  A list of Detection objects
        """
        if new_detections is None:
            new_detections = list()

        self.new_detections = new_detections

        # get existing database detection documents
        self._db = DbConnector.Instance()
        self.existing_detections = list()
        for existing_doc in self._db.find(DETECTIONS_COLLECTION, None):
            existing_detection = Detection(date=existing_doc[DATE],
                                           detection_chip_type=existing_doc[DETECTION_CHIP_TYPE],
                                           user=existing_doc[USER],
                                           instrument=existing_doc[INSTRUMENT],
                                           line_rate=existing_doc[LINE_RATE],
                                           laser_power=existing_doc[LASER_POWER],
                                           oil_psi=existing_doc[OIL_PSI],
                                           drop_psi=existing_doc[DROP_PSI],
                                           gain=existing_doc[GAIN],
                                           detection_uuid=existing_doc[DETECTION_UUID],
                                           verify=False)
            self.existing_detections.append(existing_detection)

        # run here in case user entered profiles on initialization
        self.rm_duplicates()

    def add_new_detections(self):
        """
        Add detections to the database.
        """
        if self.new_detections:
            new_docs = [nd.mongo_document for nd in self.new_detections]
            self._db.insert(DETECTIONS_COLLECTION, new_docs)

    def rm_duplicates(self):
        """
        Run this to remove detection objects that have duplicate values to
        existing database entries.
        """
        # get uniq representation of existing detection documents
        existing = set(ed.uniq_data for ed in self.existing_detections)
        # remove duplicates
        for idx in xrange(len(self.new_detections)-1, -1, -1):
            nd = self.new_detections[idx]
            if nd.uniq_data in existing:
                self.new_detections.pop(idx)

    def __iter__(self):
        """
        @return:    A generator for iterating over the Detection objects.
        """
        return (d for d in self.new_detections)

    def __getitem__(self, index):
        """
        @param index:   The index of the Detection object to return
        @return:        The Detection object at the specified index
        """
        return self.new_detections[index]

    def append(self, detection):
        """
        @param detection:   A Detection object
        """
        if not isinstance(detection, Detection):
            raise Exception('Can only append Detection objects')
        self.new_detections.append(detection)
        self.rm_duplicates()

    def extend(self, detections):
        """
        @param detections:   A list of Detection objects
        """
        for detection in detections:
            if not isinstance(detection, Detection):
                raise Exception('List must contain Detection objects')
        self.new_detections.extend(detections)
        self.rm_duplicates()

    def find_uuid(self, date, detection_chip_type, user, instrument,
                 line_rate, laser_power, oil_psi, drop_psi, gain):
        """
        Get detection uuid from existing and new detections

        @param date:                String, date in format YYYYMMDD
        @param detection_chip_type: String, usually plastic or pdms
        @param user:                String, user performing detection
        @param instrument:          String, detection device; beta7, beta10, etc
        @param line_rate:           Integer, line rate used at detection
        @param laser_power:         Integer, laser power in milliwatts
        @param oil_psi:             Float, oil pressure
        @param drop_psi:            Float, drop pressure
        @param gain:                Integer, gain used during detection
        @return:                    String, uuid of detection
        """
        for detection in self.existing_detections + self.new_detections:
            if detection.date == date and \
               detection.detection_chip_type == detection_chip_type and \
               detection.user == user and \
               detection.instrument == instrument and \
               detection.line_rate == line_rate and \
               detection.laser_power == laser_power and \
               detection.oil_psi == oil_psi and \
               detection.drop_psi == drop_psi and \
               detection.gain == gain:
                return detection.uuid


class Detection(object):
    """
    Ensures that detection database entries comply to a standardized format.
    Exceptions are raised if invalid entries are detected. This class is also
    used to temporarily store existing database entries.
    """
    def __init__(self, date, detection_chip_type, user, instrument,
                 line_rate, laser_power, oil_psi, drop_psi, gain,
                 detection_uuid=None, verify=True):
        """
        @param date:                String, date in format YYYYMMDD
        @param detection_chip_type: String, usually plastic or pdms
        @param user:                String, user performing detection
        @param instrument:          String, detection device; beta7, beta10, etc
        @param line_rate:           Integer, line rate used at detection
        @param laser_power:         Integer, laser power in milliwatts
        @param oil_psi:             Float, oil pressure
        @param drop_psi:            Float, drop pressure
        @param gain:                Integer, gain used during detection
        @param detection_uuid:      String, uuid of detection
        @param verify:              Bool, whether or not to verify. Verification
                                    is not necessary when this class is used to
                                    temporarily store existing database entries.
        """
        self.date = date
        self.detection_chip_type = detection_chip_type
        self.drop_psi = drop_psi
        self.gain = gain
        self.instrument = instrument
        self.laser_power = laser_power
        self.line_rate = line_rate
        self.oil_psi = oil_psi
        self.user = user
        self.uuid = detection_uuid
        if self.uuid is None:
            self.uuid = unicode(uuid.uuid4())

        if verify:
            self.verify()

    def verify(self):
        """
        Verify each attribute, functions called here should raise exceptions
        if invalid data is detected.
        """
        self._verify_date()
        self._verify_detection_chip_type()
        self._verify_drop_psi()
        self._verify_gain()
        self._verify_instrument()
        self._verify_laser_power()
        self._verify_line_rate()
        self._verify_oil_psi()
        self._verify_user()

    def _verify_detection_chip_type(self):
        if not isinstance(self.detection_chip_type, str):
            raise Exception('Detection chip type must be a string')
        if self.detection_chip_type not in VALID_DETECTION_CHIP_TYPES:
            raise Exception('Detection chip type must be: %s.  Received %s' %
                            (str(VALID_DETECTION_CHIP_TYPES), self.detection_chip_type))

    def _verify_instrument(self):
        if not isinstance(self.instrument, str):
            raise Exception('Instrument must be a string')

        if self.instrument not in VALID_INSTRUMENTS:
            raise Exception('Instrument must be: %s.  Received %s' %
                            (str(VALID_INSTRUMENTS), self.instrument))

    def _verify_drop_psi(self):
        if not isinstance(self.drop_psi, float):
            raise Exception('Drop PSI must be a float.')

    def _verify_oil_psi(self):
        if not isinstance(self.oil_psi, float):
            raise Exception('Oil PSI must be a float.')

    def _verify_laser_power(self):
        if not isinstance(self.laser_power, int):
            raise Exception('Laser power must be an integer.')

    def _verify_gain(self):
        if not isinstance(self.gain, int):
            raise Exception('Gain must be a integer.')

    def _verify_line_rate(self):
        if not isinstance(self.line_rate, int):
            raise Exception('Line rate must be a integer.')

    def _verify_user(self):
        if not isinstance(self.user, str):
            raise Exception('User must be a string')

    def _verify_date(self):
        if not isinstance(self.date, str):
            raise Exception('Detection date is not a string')

        # check date format
        try:
            datetime.datetime.strptime(self.date, '%Y%m%d')
        except:
            raise Exception('Detection date format is invalid.  Date format '\
                            'must be a string with format YYYYMMDD')

    @property
    def uniq_data(self):
        """
        This defines what makes a database entry unique.  There can be no
        two database entries that share the same combinations of these values.
        These values are used to check for redundant entries.

        @return:    Tuple, contains a unique set of data that
                    no two database entries can have.
        """
        return (self.date, self.detection_chip_type, self.drop_psi,
                self.gain, self.instrument, self.laser_power, self.line_rate,
                self.oil_psi)

    @property
    def mongo_document(self):
        """
        @return:    Dictionary, generates a mongodb entry
        """
        return {
            DATE: self.date,
            DETECTION_CHIP_TYPE: self.detection_chip_type,
            DROP_PSI: self.drop_psi,
            GAIN: self.gain,
            INSTRUMENT: self.instrument,
            LASER_POWER: self.laser_power,
            LINE_RATE: self.line_rate,
            OIL_PSI: self.oil_psi,
            USER: self.user,
            DETECTION_UUID: self.uuid
        }