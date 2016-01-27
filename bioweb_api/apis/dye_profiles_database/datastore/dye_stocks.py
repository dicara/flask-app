import uuid

from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.dye_profiles_database.constants import VALID_DYE_NAMES, DYE_NAME, \
    LOT_NUMBER, MANUFACTURER, DYE_STOCK_UUID, DYE_STOCKS_COLLECTION


class DyeStocks(object):
    def __init__(self, new_dye_stocks=None):
        """
        @param new_dye_stocks:  A list of DyeStock objects
        """
        if new_dye_stocks is None:
            new_dye_stocks = list()

        self.new_dye_stocks = new_dye_stocks

        # get existing database dye stock documents
        self._db = DbConnector.Instance()
        self.existing_dye_stocks = list()
        for existing_doc in self._db.find(DYE_STOCKS_COLLECTION, None):
            existing_ds = DyeStock(dye_name=existing_doc[DYE_NAME],
                                   lot_number=existing_doc[LOT_NUMBER],
                                   manufacturer=existing_doc[MANUFACTURER],
                                   dye_stock_uuid=existing_doc[DYE_STOCK_UUID],
                                   verify=False)
            self.existing_dye_stocks.append(existing_ds)

        # remove duplicates
        self.rm_duplicates()

    def add_new_dye_stocks(self):
        if self.new_dye_stocks:
            new_docs = [nds.mongo_document for nds in self.new_dye_stocks]
            self._db.insert(DYE_STOCKS_COLLECTION, new_docs)

    def rm_duplicates(self):
        """
        Run this to remove dye stock objects that have duplicate values to
        existing database entries.
        """
        # get uniq representation of existing dye stock documents
        existing = set(eds.uniq_data for eds in self.existing_dye_stocks)
        # remove duplicates
        for idx in xrange(len(self.new_dye_stocks)-1, -1, -1):
            nds = self.new_dye_stocks[idx]
            if nds.uniq_data in existing:
                self.new_dye_stocks.pop(idx)

    def __iter__(self):
        """
        @return:    A generator for iterating over the DyeStock objects.
        """
        return (d for d in self.new_dye_stocks)

    def __getitem__(self, index):
        """
        @param index:   The index of the DyeStock object to return
        @return:        The DyeStock object at the specified index
        """
        return self.new_dye_stocks[index]

    def append(self, dye_stock):
        """
        @param dye_stock:   A DyeStock object
        """
        if not isinstance(dye_stock, DyeStock):
            raise Exception('Can only append DyeStock objects')
        self.new_dye_stocks.append(dye_stock)
        self.rm_duplicates()

    def extend(self, dye_stocks):
        """
        @param dye_stocks:   A list of DyeStock objects
        """
        for dye_stock in dye_stocks:
            if not isinstance(dye_stock, DyeStock):
                raise Exception('List must contain DyeStock objects')
        self.new_dye_stocks.extend(dye_stocks)
        self.rm_duplicates()

    def find_uuid(self, dye_name, lot_number, manufacturer):
        """
        Return the UUID associated with inputs

        @param dye_name:        String, dye stock name
        @param lot_number:      String, lot number
        @param manufacturer:    String, manufacturer
        @return:                String, UUID or None if no matching stocks
        """
        for dye_stock in self.existing_dye_stocks + self.new_dye_stocks:
            if dye_stock.dye_name == dye_name and \
               dye_stock.lot_number == lot_number and \
               dye_stock.manufacturer == manufacturer:
                return dye_stock.uuid


class DyeStock(object):
    """
    Ensures that dye stock database entries comply to a standardized format.
    Exceptions are raised if invalid entries are detected.  This class is also
    used to temporarily store existing database entries.
    """
    def __init__(self, dye_name, lot_number, manufacturer, dye_stock_uuid=None,
                 verify=True):
        """
        @param dye_name:        String, dye name
        @param lot_number:      String, dye stock lot number
        @param manufacturer:    String, dye stock manufacturer
        @param dye_stock_uuid:  String, uuid of dye stock
        @param verify:          Bool, whether or not to verify. Verification
                                is not necessary when this class is used to
                                temporarily store existing database entries.
        """
        self.dye_name = dye_name
        self.lot_number = lot_number
        self.manufacturer = manufacturer
        self.uuid = dye_stock_uuid
        if self.uuid is None:
            self.uuid = unicode(uuid.uuid4())

        if verify:
            self.verify()

    def verify(self):
        """
        Verify each attribute, functions called here should raise
        exceptions if invalid data is detected.
        """
        self._verify_name()
        self._verify_lot_number()

    def _verify_name(self):
        if not isinstance(self.dye_name, str):
            raise Exception('Dye name mut be a string.')
        if self.dye_name not in VALID_DYE_NAMES:
            raise Exception('Dye name %s is not valid' % str(self.dye_name))

    def _verify_lot_number(self):
        if not isinstance(self.lot_number, str):
            raise Exception('Lot number must be a string.')

    @property
    def uniq_data(self):
        """
        This defines what makes a database entry unique.  There can be no
        two database entries that share the same combinations of these values.
        These values are used to check for redundant entries.

        @return:    Tuple, contains a unique set of data that
                    no two database entries can have.
        """
        return (self.dye_name, self.lot_number, self.manufacturer)

    @property
    def mongo_document(self):
        """
        @return:    Dictionary, generates a mongodb entry
        """
        return {
            DYE_NAME: self.dye_name,
            LOT_NUMBER: self.lot_number,
            MANUFACTURER: self.manufacturer,
            DYE_STOCK_UUID: self.uuid
        }