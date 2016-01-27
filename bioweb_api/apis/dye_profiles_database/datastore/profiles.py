from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.dye_profiles_database.constants import DYE_STOCK_UUID, DETECTION_UUID, \
    CONCENTRATION_UGML, PROFILE, PEAK_INTENSITY, PROFILES_COLLECTION


class Profiles(object):
    """
    A container for Profile objects.  Used to check database for
    redundant entries and enter new profiles.
    """
    def __init__(self, profiles=None):
        """
        @param profiles:    A list of profile objects
        """
        if profiles is None:
            profiles = list()

        self.new_profiles = profiles

        # check existing profiles
        self._db = DbConnector.Instance()
        self.existing_profiles = list()
        # Don't used the profiles array data, just check UUIDs and concentration
        for existing_doc in self._db.find(PROFILES_COLLECTION, None, {PROFILE: 0}):
            existing_prof = Profile(dye_stock_uuid=existing_doc[DYE_STOCK_UUID],
                                    detection_uuid=existing_doc[DETECTION_UUID],
                                    profile=None,
                                    concentration_ugml=existing_doc[CONCENTRATION_UGML],
                                    peak_intensity=None,
                                    verify=False)
            self.existing_profiles.append(existing_prof)

        self.rm_duplicates()

    def rm_duplicates(self):
        """
        Duplicate profiles cannot be entered, remove them here.
        """
        # get unique representation of existing profile documents
        existing = set(prof.uniq_data for prof in self.existing_profiles)
        # remove duplicates
        for idx in xrange(len(self.new_profiles)-1, -1, -1):
            nd = self.new_profiles[idx]
            if nd.uniq_data in existing:
                self.new_profiles.pop(idx)

    def add_new_profiles(self):
        if self.new_profiles:
            new_docs = [prof.mongo_document for prof in self.new_profiles]
            self._db.insert(PROFILES_COLLECTION, new_docs)

    def __iter__(self):
        """
        @return:    A generator for iterating over the Profile objects.
        """
        return (p for p in self.new_profiles)

    def __getitem__(self, index):
        """
        @param index:   The index of the Profile object to return
        @return:        The Profile object at the specified index
        """
        return self.new_profiles[index]

    def append(self, profile):
        """
        @param profile:   A Profile object
        """
        if not isinstance(profile, Profile):
            raise Exception('Can only append Profile objects')
        self.new_profiles.append(profile)
        self.rm_duplicates()

    def extend(self, profiles):
        """
        @param profiles:   A list of Profile objects
        """
        for profile in profiles:
            if not isinstance(profile, Profile):
                raise Exception('List must contain Profile objects')
        self.new_profiles.extend(profiles)
        self.rm_duplicates()


class Profile(object):
    """
    Ensures that profile database entries comply to a standardized format.
    Exceptions are raised if invalid entries are detected.  This class is also
    used to temporarily store existing database entries.
    """
    def __init__(self, dye_stock_uuid, detection_uuid, profile,
                 concentration_ugml, peak_intensity, verify=True):
        """
        @param dye_stock_uuid:      String, uuid of dye stock used to generate this profile
        @param detection_uuid:      String, uuid of detection used to generate this profile
        @param profile:             List of floats, the is the normalized profile
        @param concentration_ugml:  Float, concentration of dye in ug/ml
        @param peak_intensity:      Integer, peak intensity of dye peak
        @param verify:              Bool, whether or not to verify. Verification
                                    is not necessary when this class is used to
                                    temporarily store existing database entries.
        """
        self.dye_stock_uuid = dye_stock_uuid
        self.detection_uuid = detection_uuid
        self.profile = profile
        self.concentration_ugml = concentration_ugml
        self.peak_intensity = peak_intensity

        if verify:
            self.verify()

    def verify(self):
        """
        Verify each attribute, functions called here should raise
        exceptions if invalid data is detected.
        """
        self._verify_dye_stock_uuid()
        self._verify_detection_uuid()
        self._verify_concentration_ugml()
        self._verify_peak_intensity()

    def _verify_peak_intensity(self):
        if not isinstance(self.peak_intensity, int):
            raise Exception('Profile peak intensity is not an integer.')

    def _verify_concentration_ugml(self):
        if not isinstance(self.concentration_ugml, float):
            raise Exception('Profile concentration is not a float.')

    def _verify_dye_stock_uuid(self):
        if not isinstance(self.dye_stock_uuid, unicode):
            raise Exception('Profile dye stock UUID must be a unicode string.')

    def _verify_detection_uuid(self):
        if not isinstance(self.detection_uuid, unicode):
            raise Exception('Profile detection UUID is not a unicode string.')

    @property
    def uniq_data(self):
        """
        This defines what makes a database entry unique.  There can be no
        two database entries that share the same combinations of these values.
        These values are used to check for redundant entries.

        @return:    Tuple, contains a unique set of data that
                    no two database entries can have.
        """
        return (self.dye_stock_uuid, self.detection_uuid, self.concentration_ugml)

    @property
    def mongo_document(self):
        """
        @return:    Dictionary, generates a mongodb entry
        """
        return {
            DYE_STOCK_UUID: self.dye_stock_uuid,
            DETECTION_UUID: self.detection_uuid,
            PROFILE: self.profile,
            CONCENTRATION_UGML: self.concentration_ugml,
            PEAK_INTENSITY: self.peak_intensity
        }