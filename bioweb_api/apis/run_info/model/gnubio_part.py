'''
Copyright 2016 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Yuewei Sheng
@date:   July 5th, 2016
'''

#=============================================================================
# Imports
#=============================================================================

from bioweb_api.apis.run_info.constants import APP_TYPE, CATALOG_NUM, EXPIRE_DATE, \
    GNUBIO_PART_TYPE, INTERNAL_PART_NUM, LOT_NUM, MANUFACTURE_DATE, SERIAL_NUM, \
    CUSTOMER_APP_NAME, VARIANT_MASK

#=============================================================================
# Classes
#=============================================================================

class GnubioPart(object):
    def __init__(self, app_type, catalog_num, exp_date, gnubio_part_type,
                 internal_part_num, lot_num, mfg_date, serial_num):
        self._app_type          = app_type
        self._catalog_num       = catalog_num
        self._exp_date          = exp_date
        self._gnubio_part_type  = gnubio_part_type
        self._internal_part_num = internal_part_num
        self._lot_num           = lot_num
        self._mfg_date          = mfg_date
        self._serial_num        = serial_num

    @property
    def app_type(self):
        return self._app_type

    @property
    def catalog_num(self):
        return self._catalog_num

    @property
    def exp_date(self):
        return self._exp_date

    @property
    def gnubio_part_type(self):
        return gnubio_part_type

    @property
    def internal_part_num(self):
        return self._internal_part_num

    @property
    def lot_num(self):
        return self._lot_num

    @property
    def mfg_date(self):
        return self._mfg_date

    @property
    def serial_num(self):
        return self._serial_num

    def as_dict(self):
        return {
                    APP_TYPE:           self._app_type,
                    CATALOG_NUM:        self._catalog_num,
                    EXPIRE_DATE:        self._exp_date,
                    GNUBIO_PART_TYPE:   self._gnubio_part_type,
                    INTERNAL_PART_NUM:  self._internal_part_num,
                    LOT_NUM:            self._lot_num,
                    MANUFACTURE_DATE:   self._mfg_date,
                    SERIAL_NUM:         self._serial_num
               }

    @classmethod
    def from_dict(cls, src):
        return cls(src[APP_TYPE],
                   src[CATALOG_NUM],
                   src[EXPIRE_DATE],
                   src[GNUBIO_PART_TYPE],
                   src[INTERNAL_PART_NUM],
                   src[LOT_NUM],
                   src[MANUFACTURE_DATE],
                   src[SERIAL_NUM])

class GnubioPartWithCustName(GnubioPart):
    def __init__(self, app_type, catalog_num, cust_app_name, exp_date, gnubio_part_type,
                 internal_part_num, lot_num, mfg_date, serial_num, variant_mask):
        super(GnubioPartWithCustName, self).__init__(app_type,
                                                     catalog_num,
                                                     exp_date,
                                                     gnubio_part_type,
                                                     internal_part_num,
                                                     lot_num,
                                                     mfg_date,
                                                     serial_num)
        self._cust_app_name = cust_app_name
        self._variant_mask = variant_mask

    @property
    def cust_app_name(self):
        return self._cust_app_name

    @property
    def variant_mask(self):
        return self._variant_mask

    def as_dict(self):
        ret = super(GnubioPartWithCustName, self).as_dict()
        ret.update({
            CUSTOMER_APP_NAME:      self.cust_app_name,
            VARIANT_MASK:           self.variant_mask
        })
        return ret

    @classmethod
    def from_dict(cls, src):
        return cls(src[APP_TYPE],
                   src[CATALOG_NUM],
                   src[CUSTOMER_APP_NAME],
                   src[EXPIRE_DATE],
                   src[GNUBIO_PART_TYPE],
                   src[INTERNAL_PART_NUM],
                   src[LOT_NUM],
                   src[MANUFACTURE_DATE],
                   src[SERIAL_NUM],
                   src[VARIANT_MASK])

class Cartridge(GnubioPart):
    def __repr__(self):
        return "Cartridge: %s" % self.as_dict()

class Kit(GnubioPartWithCustName):
    def __repr__(self):
        return "Kit: %s" % self.as_dict()

class Syringe(GnubioPartWithCustName):
    def __repr__(self):
        return "Syringe: %s" % self.as_dict()
