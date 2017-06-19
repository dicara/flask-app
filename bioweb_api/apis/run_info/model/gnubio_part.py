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
    CUSTOMER_APP_NAME, VARIANT_MASK, PICO1_DYE, PICO2_DYE, PCR_LOW, PCR_MEDIUM, \
    PCR_HIGH, SMALL_PELTIER_1, SMALL_PELTIER_2, INCUBATION, ASSAY_DYE, TEMPERATURE

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

class Cartridge(GnubioPart):
    def __repr__(self):
        return "Cartridge: %s" % self.as_dict()

class Syringe(GnubioPart):
    def __init__(self, app_type, catalog_num, cust_app_name, exp_date, gnubio_part_type,
                 internal_part_num, lot_num, mfg_date, serial_num, variant_mask):
        super(Syringe, self).__init__(app_type,
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
        ret = super(Syringe, self).as_dict()
        ret.update({
            CUSTOMER_APP_NAME:      self.cust_app_name,
            VARIANT_MASK:           self.variant_mask
        })
        return ret

    def __repr__(self):
        return "Syringe: %s" % self.as_dict()

    @classmethod
    def from_dict(cls, src):
        # mask_code sits in 'exp_def' field in old run reports
        mask_code = None
        if VARIANT_MASK in src:
            mask_code = src[VARIANT_MASK]
        elif 'exp_def' in src:
            mask_code = src['exp_def']

        return cls(src[APP_TYPE],
                   src[CATALOG_NUM],
                   src[CUSTOMER_APP_NAME],
                   src[EXPIRE_DATE],
                   src[GNUBIO_PART_TYPE],
                   src[INTERNAL_PART_NUM],
                   src[LOT_NUM],
                   src[MANUFACTURE_DATE],
                   src[SERIAL_NUM],
                   mask_code)

class Kit(GnubioPart):
    def __init__(self, app_type, catalog_num, cust_app_name, exp_date, gnubio_part_type,
                 internal_part_num, lot_num, mfg_date, serial_num, assay_dye,
                 pico1_dye, pico2_dye, pcr_low, pcr_medium, pcr_high, small_peltier1,
                 small_peltier2):
        super(Kit, self).__init__(app_type,
                                      catalog_num,
                                      exp_date,
                                      gnubio_part_type,
                                      internal_part_num,
                                      lot_num,
                                      mfg_date,
                                      serial_num)
        self._cust_app_name     = cust_app_name
        self._assay_dye         = assay_dye
        self._pico1_dye         = pico1_dye
        self._pico2_dye         = pico2_dye
        self._pcr_low           = pcr_low
        self._pcr_medium        = pcr_medium
        self._pcr_high          = pcr_high
        self._small_peltier1    = small_peltier1
        self._small_peltier2    = small_peltier2

    @property
    def cust_app_name(self):
        return self._cust_app_name

    @property
    def assay_dye(self):
        return self._assay_dye

    @property
    def pico1_dye(self):
        return self._pico1_dye

    @property
    def pico2_dye(self):
        return self._pico2_dye

    @property
    def pcr_low(self):
        return self._pcr_low

    @property
    def pcr_medium(self):
        return self._pcr_medium

    @property
    def pcr_high(self):
        return self._pcr_high

    @property
    def small_peltier1(self):
        return self._small_peltier1

    @property
    def small_peltier2(self):
        return self._small_peltier2

    def as_dict(self):
        ret = super(Kit, self).as_dict()
        ret.update({
            CUSTOMER_APP_NAME:      self.cust_app_name,
            ASSAY_DYE:              self.assay_dye,
            PICO1_DYE:              self.pico1_dye,
            PICO2_DYE:              self.pico2_dye,
            PCR_LOW:                self.pcr_low,
            PCR_MEDIUM:             self.pcr_medium,
            PCR_HIGH:               self.pcr_high,
            SMALL_PELTIER_1:        self.small_peltier1,
            SMALL_PELTIER_2:        self.small_peltier2,
        })
        return ret

    def __repr__(self):
        return "Kit: %s" % self.as_dict()

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
                   src.get(ASSAY_DYE),
                   src.get(PICO1_DYE),
                   src.get(PICO2_DYE),
                   src.get(PCR_LOW),
                   src.get(PCR_MEDIUM),
                   src.get(PCR_HIGH),
                   src.get(SMALL_PELTIER_1),
                   src.get(SMALL_PELTIER_2))


class Temperature(object):
    def __init__(self, incubation, pcr_low, pcr_medium, pcr_high, small_peltier1,
                 small_peltier2):
        self._incubation        = incubation
        self._pcr_low           = pcr_low
        self._pcr_medium        = pcr_medium
        self._pcr_high          = pcr_high
        self._small_peltier1    = small_peltier1
        self._small_peltier2    = small_peltier2

    @property
    def incubation(self):
        return self._incubation

    @property
    def pcr_low(self):
        return self._pcr_low

    @property
    def pcr_medium(self):
        return self._pcr_medium

    @property
    def pcr_high(self):
        return self._pcr_high

    @property
    def small_peltier1(self):
        return self._small_peltier1

    @property
    def small_peltier2(self):
        return self._small_peltier2

    def __repr__(self):
        return "temperature: %s" % self.as_dict()

    def as_dict(self):
        return {INCUBATION:         self.incubation,
                PCR_LOW:            self.pcr_low,
                PCR_MEDIUM:         self.pcr_medium,
                PCR_HIGH:           self.pcr_high,
                SMALL_PELTIER_1:    self.small_peltier1,
                SMALL_PELTIER_2:    self.small_peltier2}

    @classmethod
    def from_dict(cls, src):
        if src is None: return None
        return cls(src.get(INCUBATION),
                   src.get(PCR_LOW),
                   src.get(PCR_MEDIUM),
                   src.get(PCR_HIGH),
                   src.get(SMALL_PELTIER_1),
                   src.get(SMALL_PELTIER_2))

class ExperimentConfigs(object):
    def __init__(self, assay_dye, mask_code, pico1_dye, pico2_dye, temperature):
        self._assay_dye     = assay_dye
        self._mask_code     = mask_code
        self._pico1_dye     = pico1_dye
        self._pico2_dye     = pico2_dye
        self._temperature   = temperature

    @property
    def assay_dye(self):
        return self._assay_dye

    @property
    def mask_code(self):
        return self._mask_code

    @property
    def pico1_dye(self):
        return self._pico1_dye

    @property
    def pico2_dye(self):
        return self._pico2_dye

    @property
    def temperature(self):
        return self._temperature

    def __repr__(self):
        return "experiment_configs: %s" % self.as_dict()

    def as_dict(self):
        return {ASSAY_DYE:              self.assay_dye,
                VARIANT_MASK:           self.mask_code,
                PICO1_DYE:              self.pico1_dye,
                PICO2_DYE:              self.pico2_dye,
                TEMPERATURE:            self.temperature.as_dict() if self.temperature else None}

    @classmethod
    def from_dict(cls, src):
        if src is None: return None
        return cls(src.get(ASSAY_DYE),
                   src.get(VARIANT_MASK),
                   src.get(PICO1_DYE),
                   src.get(PICO2_DYE),
                   Temperature.from_dict(src.get(TEMPERATURE)))
