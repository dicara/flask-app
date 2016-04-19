import os

from bioweb_api import ARCHIVES_PATH

# constants ending with _TXT are field names in run_info.txt
CARTRIDGE_SN                = 'cart_serial_number'
CARTRIDGE_SN_TXT            = 'Cartridge Serial Number'
CHIP_SN                     = 'chip_serial_number'
CHIP_SN_TXT                 = 'Chip Serial Number'
CHIP_REVISION               = 'chip_rev'
CHIP_REVISION_TXT           = 'Chip Revision'
DATE                        = 'date'
DATETIME                    = 'datetime'
DEVICE_NAME                 = 'device_name'
DEVICE_NAME_TXT             = 'Device Name'
EXIT_NOTES                  = 'exit_notes'
EXIT_NOTES_TXT              = 'Exit Notes'
EXP_DEF_NAME                = 'exp_def'
EXP_DEF_NAME_TXT            = 'Experiment Definition'
FILE_TYPE                   = 'file_type'
IMAGE_STACKS                = 'image_stacks'
REAGENT_INFO                = 'reagent_info'
REAGENT_INFO_TXT            = 'Reagent Info'
RUN_ID                      = 'run_id'
RUN_ID_TXT                  = 'Run ID'
RUN_DESCRIPTION             = 'starting_notes'
RUN_DESCRIPTION_TXT         = 'Run Description'
RUN_REPORT_TXTFILE          = 'run_info.txt'
RUN_REPORT_YAMLFILE         = 'run_info.yaml'
RUN_REPORT_PATH             = os.path.join(ARCHIVES_PATH, 'run_reports')
TDI_STACKS                  = 'tdi_stacks'
TDI_STACKS_TXT              = 'TDI Stacks'
USER                        = 'user_list'
USER_TXT                    = 'User List'
