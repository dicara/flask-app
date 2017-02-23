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

from enum import Enum

from bioweb_api.apis.ApiConstants import UUID
from bioweb_api.DbConnector import DbConnector
from bioweb_api.apis.run_info.model.gnubio_part import Cartridge, Kit, Syringe
from bioweb_api.apis.run_info.constants import CARTRIDGE_SN_TXT, CHIP_SN_TXT, \
    CHIP_REVISION_TXT, DATETIME, DEVICE_NAME_TXT, EXIT_NOTES_TXT, \
    EXP_DEF_NAME_TXT, REAGENT_INFO_TXT, RUN_ID_TXT, RUN_DESCRIPTION_TXT, \
    TDI_STACKS_TXT, USER_TXT, CARTRIDGE_SN, CHIP_SN, CHIP_REVISION, \
    DEVICE_NAME, EXIT_NOTES, EXP_DEF_NAME, REAGENT_INFO, RUN_ID, RUN_DESCRIPTION, \
    TDI_STACKS, USER, IMAGE_STACKS, FILE_TYPE, UTAG, FA_UUID_MAP, CARTRIDGE_BC, \
    EXP_DEF_UUID, KIT_BC, MCP_MODE, SAMPLE_NAME, SAMPLE_TYPE, SYRINGE_BC, FAIL_REASON, \
    EXPERIMENT_PURPOSE

#=============================================================================
# Classes
#=============================================================================

class RunReportWebUI(object):
    def __init__(self, datetime, utag, run_id, cartridge_sn, chip_sn, run_description,
                 user_list, reagent_info, chip_rev, exp_def_name, device_name,
                 exit_notes, tdi_stacks, exp_purpose):
        self._uuid              = str(uuid4())
        self._datetime          = datetime
        self._utag              = utag
        self._run_id            = run_id
        self._cartridge_sn      = cartridge_sn
        self._chip_sn           = chip_sn
        self._run_description   = run_description
        self._user_list         = user_list
        self._reagent_info      = reagent_info
        self._chip_rev          = chip_rev
        self._exp_def_name      = exp_def_name
        self._device_name       = device_name
        self._exit_notes        = exit_notes
        self._tdi_stacks        = tdi_stacks
        self._exp_purpose       = exp_purpose

        self.verify()

        self._image_stack_names = []
        if self._tdi_stacks is not None and len(self._tdi_stacks) > 0:
            self._image_stack_names = [path.split('/')[-1]
                                        for path in self._tdi_stacks]
        self._fa_uuid_map = dict() # initiate a dict to store archive name, full analysis uuids as key, value

    @classmethod
    def from_dict(cls, **kwargs):
        if kwargs.get(FILE_TYPE) == 'txt':
            return cls(kwargs.get(DATETIME),
                       kwargs.get(UTAG),
                       kwargs.get(RUN_ID_TXT),
                       kwargs.get(CARTRIDGE_SN_TXT),
                       kwargs.get(CHIP_SN_TXT),
                       kwargs.get(RUN_DESCRIPTION_TXT),
                       kwargs.get(USER_TXT),
                       kwargs.get(REAGENT_INFO_TXT),
                       kwargs.get(CHIP_REVISION_TXT),
                       kwargs.get(EXP_DEF_NAME_TXT),
                       kwargs.get(DEVICE_NAME_TXT),
                       kwargs.get(EXIT_NOTES_TXT),
                       kwargs.get(TDI_STACKS_TXT),
                       kwargs.get(EXPERIMENT_PURPOSE))
        elif kwargs.get(FILE_TYPE) == 'yaml':
            return cls(kwargs.get(DATETIME),
                       kwargs.get(UTAG),
                       kwargs.get(RUN_ID),
                       kwargs.get(CARTRIDGE_SN),
                       kwargs.get(CHIP_SN),
                       kwargs.get(RUN_DESCRIPTION),
                       kwargs.get(USER),
                       kwargs.get(REAGENT_INFO),
                       kwargs.get(CHIP_REVISION),
                       kwargs.get(EXP_DEF_NAME),
                       kwargs.get(DEVICE_NAME),
                       kwargs.get(EXIT_NOTES),
                       kwargs.get(TDI_STACKS),
                       kwargs.get(EXPERIMENT_PURPOSE))
        else:
            raise Exception("Unknown type of log file.")

    def __eq__(self, o):
        return self._uuid == o._uuid

    def __repr__(self):
        return "Run report: %s" % self.as_dict()

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
        if self._run_id is not None and not isinstance(self._run_id, str):
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

    def as_dict(self):
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
                UTAG:               self._utag,
                EXPERIMENT_PURPOSE: self._exp_purpose,
        }

class RunReportClientUI(object):
    def __init__(self, datetime, utag, cartridge_bc, chip_rev, device_name,
                 fail_reason, exp_def_name, exp_def_uuid, kit_bc, mcp_mode,
                 run_id, sample_name, sample_type, syringe_bc, tdi_stacks,
                 exp_purpose):
        self._uuid                  = str(uuid4())
        self._datetime              = datetime
        self._utag                  = utag

        self._cartridge_bc          = cartridge_bc
        self._chip_rev              = chip_rev
        self._device_name           = device_name
        self._fail_reason           = fail_reason
        self._exp_def_name          = exp_def_name
        self._exp_def_uuid          = exp_def_uuid
        self._kit_bc                = kit_bc
        self._mcp_mode              = mcp_mode
        self._run_id                = run_id
        self._sample_name           = sample_name
        self._sample_type           = sample_type
        self._syringe_bc            = syringe_bc
        self._tdi_stacks            = tdi_stacks
        self._exp_purpose           = exp_purpose

        self._image_stack_names     = []
        if self._tdi_stacks is not None and len(self._tdi_stacks) > 0:
            self._image_stack_names = [path.split('/')[-1]
                                        for path in self._tdi_stacks]
        self._fa_uuid_map = dict() # initiate a dict to store archive name, full analysis uuids as key, value

    def __eq__(self, o):
        return self._uuid == o._uuid

    def __repr__(self):
        return "Run report: %s" % self.as_dict()

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(kwargs.get(DATETIME),
                   kwargs.get(UTAG),
                   Cartridge.from_dict(kwargs.get(CARTRIDGE_BC)),
                   kwargs.get(CHIP_REVISION),
                   kwargs.get(DEVICE_NAME),
                   kwargs.get(FAIL_REASON),
                   kwargs.get(EXP_DEF_NAME),
                   kwargs.get(EXP_DEF_UUID),
                   Kit.from_dict(kwargs.get(KIT_BC)),
                   kwargs.get(MCP_MODE),
                   kwargs.get(RUN_ID),
                   kwargs.get(SAMPLE_NAME),
                   kwargs.get(SAMPLE_TYPE),
                   Syringe.from_dict(kwargs.get(SYRINGE_BC)),
                   kwargs.get(TDI_STACKS),
                   kwargs.get(EXPERIMENT_PURPOSE))

    def as_dict(self):
        return {
                    UUID:               self._uuid,
                    DATETIME:           self._datetime,
                    UTAG:               self._utag,
                    CARTRIDGE_BC:       self._cartridge_bc.as_dict(),
                    CHIP_REVISION:      self._chip_rev,
                    DEVICE_NAME:        self._device_name,
                    FAIL_REASON:        self._fail_reason,
                    EXP_DEF_NAME:       self._exp_def_name,
                    EXP_DEF_UUID:       self._exp_def_uuid,
                    KIT_BC:             self._kit_bc.as_dict(),
                    MCP_MODE:           self._mcp_mode,
                    RUN_ID:             self._run_id,
                    SAMPLE_NAME:        self._sample_name,
                    SAMPLE_TYPE:        self._sample_type,
                    SYRINGE_BC:         self._syringe_bc.as_dict(),
                    TDI_STACKS:         self._tdi_stacks,
                    IMAGE_STACKS:       self._image_stack_names,
                    EXPERIMENT_PURPOSE: self._exp_purpose,
               }
