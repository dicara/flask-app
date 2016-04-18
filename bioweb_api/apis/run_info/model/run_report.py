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
@date:   Apr 11, 2016
'''

#=============================================================================
# Imports
#=============================================================================
import datetime
from uuid import uuid4

from bioweb_api.apis.ApiConstants import UUID
from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.run_info.constants import CARTRIDGE_SN_TXT, CHIP_SN_TXT, \
    CHIP_REVISION_TXT, DATETIME, DEVICE_NAME_TXT, EXIT_NOTES_TXT, \
    EXP_DEF_NAME_TXT, REAGENT_INFO_TXT, RUN_ID_TXT, RUN_DESCRIPTION_TXT, \
    TDI_STACKS_TXT, USER_TXT, CARTRIDGE_SN, CHIP_SN, CHIP_REVISION, \
    DEVICE_NAME, EXIT_NOTES, EXP_DEF_NAME, REAGENT_INFO, RUN_ID, RUN_DESCRIPTION, \
    TDI_STACKS, USER, IMAGE_STACKS, FILE_TYPE

class RunReport(object):
    def __init__(self, **kwargs):
        self._uuid                  = str(uuid4())
        self._datetime              = kwargs.get(DATETIME)

        if kwargs.get(FILE_TYPE) == 'txt':
            self._run_id                = kwargs.get(RUN_ID_TXT) # RUN_ID_TXT cannot be None
            self._cartridge_sn          = kwargs.get(CARTRIDGE_SN_TXT)
            self._chip_sn               = kwargs.get(CHIP_SN_TXT)
            self._run_description       = kwargs.get(RUN_DESCRIPTION_TXT)
            self._user_list             = kwargs.get(USER_TXT)
            self._reagent_info          = kwargs.get(REAGENT_INFO_TXT)
            self._chip_rev              = kwargs.get(CHIP_REVISION_TXT)
            self._exp_def_name          = kwargs.get(EXP_DEF_NAME_TXT)
            self._device_name           = kwargs.get(DEVICE_NAME_TXT)
            self._exit_notes            = kwargs.get(EXIT_NOTES_TXT)
            self._tdi_stacks            = kwargs.get(TDI_STACKS_TXT)
        elif kwargs.get(FILE_TYPE) == 'yaml':
            self._run_id                = kwargs.get(RUN_ID)
            self._cartridge_sn          = kwargs.get(CARTRIDGE_SN)
            self._chip_sn               = kwargs.get(CHIP_SN)
            self._run_description       = kwargs.get(RUN_DESCRIPTION)
            self._user_list             = kwargs.get(USER)
            self._reagent_info          = kwargs.get(REAGENT_INFO)
            self._chip_rev              = kwargs.get(CHIP_REVISION)
            self._exp_def_name          = kwargs.get(EXP_DEF_NAME)
            self._device_name           = kwargs.get(DEVICE_NAME)
            self._exit_notes            = kwargs.get(EXIT_NOTES)
            self._tdi_stacks            = kwargs.get(TDI_STACKS)
        else:
            raise Exception("Unknown type of log file.")

        self.verify()

        self._image_stack_names     = None
        if self._tdi_stacks is not None and len(self._tdi_stacks) > 0:
            self._image_stack_names = [path.split('/')[-1]
                                        for path in self._tdi_stacks]

    def verify(self):
        self._verify_run_id()
        self._verify_cartridge_sn()
        self._verify_chip_sn()
        self._verify_datetime()
        self._verify_run_description()
        self._verify_user_list()
        self._verify_reagent_info()
        self._verify_chip_rev()
        self._verify_exp_def_name()
        self._verify_device_name()
        self._verify_exit_notes()
        self._verify_tdi_stacks()

    def _verify_run_id(self):
        if not isinstance(self._run_id, str):
            raise Exception("Run ID is not a string.")

    def _verify_cartridge_sn(self):
        if self._cartridge_sn is not None and not isinstance(self._cartridge_sn, str):
            raise Exception("Cartridge serial number is not a string.")

    def _verify_chip_sn(self):
        if self._chip_sn is not None and not isinstance(self._chip_sn, str):
            raise Exception("Chip serial number is not a string.")

    def _verify_datetime(self):
        if self._datetime is not None and not isinstance(self._datetime,
                                                        datetime.datetime):
            raise Exception("Date is not a Datetime object.")

    def _verify_run_description(self):
        if self._run_description is not None and not isinstance(self._run_description, str):
            raise Exception("Run description is not a string.")

    def _verify_user_list(self):
        if self._user_list is not None and not isinstance(self._user_list, list):
            raise Exception("User list is not a Python list.")

    def _verify_reagent_info(self):
        if self._reagent_info is not None and not isinstance(self._reagent_info, str):
            raise Exception("Reagent information is not a string.")

    def _verify_chip_rev(self):
        if self._chip_rev is not None and not isinstance(self._chip_rev, str):
            raise Exception("Chip revision is not a string.")

    def _verify_exp_def_name(self):
        if self._exp_def_name is not None and not isinstance(self._exp_def_name, str):
            raise Exception("Experiment definition is not a string.")

    def _verify_device_name(self):
        if self._device_name is not None and not isinstance(self._device_name, str):
            raise Exception("Device name is not a string.")

    def _verify_exit_notes(self):
        if self._exit_notes is not None and not isinstance(self._exit_notes, str):
            raise Exception("Exit notes is not a string.")

    def _verify_tdi_stacks(self):
        if self._tdi_stacks is not None and not isinstance(self._tdi_stacks, list):
            raise Exception("TDI Stacks is not a list.")

    @property
    def to_dict(self):
        return {
                UUID:               self._uuid,
                RUN_ID:             self._run_id,
                CARTRIDGE_SN:       self._cartridge_sn,
                CHIP_SN:            self._chip_sn,
                DATETIME:           self._datetime,
                RUN_DESCRIPTION:    self._run_description,
                USER:               self._user_list,
                REAGENT_INFO:       self._reagent_info,
                CHIP_REVISION:      self._chip_rev,
                EXP_DEF_NAME:       self._exp_def_name,
                DEVICE_NAME:        self._device_name,
                EXIT_NOTES:         self._exit_notes,
                TDI_STACKS:         self._tdi_stacks,
                IMAGE_STACKS:       self._image_stack_names,
        }
