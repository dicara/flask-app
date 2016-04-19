import datetime
import os
import unittest

from bioweb_api import RUN_REPORT_COLLECTION
from bioweb_api.apis.run_info.constants import CARTRIDGE_SN, CHIP_SN, CHIP_REVISION, \
    DATETIME, DEVICE_NAME, EXIT_NOTES, EXP_DEF_NAME, REAGENT_INFO, RUN_ID, \
    RUN_DESCRIPTION, RUN_REPORT_PATH, USER, RUN_REPORT_TXTFILE, IMAGE_STACKS
from bioweb_api.apis.run_info.RunInfoUtils import read_report_file, \
        get_run_reports, update_run_reports

class TestRunReportAPI(unittest.TestCase):
    def test_read_report_file_txt(self):
        """
        test read_report_file, read a run_info.txt file and return a dictionary
        """
        report_file = '/home/vagrant/test/run_info.txt'
        datetime_obj = datetime.datetime.today()
        report_doc = read_report_file(report_file, datetime_obj)

        self.assertIn(CARTRIDGE_SN, report_doc)
        self.assertIn(RUN_DESCRIPTION, report_doc)
        self.assertIn(DEVICE_NAME, report_doc)
        self.assertEqual(report_doc[RUN_ID], 'id1459882049')
        self.assertEqual(report_doc[USER], ['thung', 'erahut'])
        self.assertEqual(report_doc[EXP_DEF_NAME], 'ABL_24_V1')

    def test_read_report_file_yaml(self):
        """
        test read_report_file, read a run_info.yaml file and return a dictionary
        """
        report_file = '/home/vagrant/test/run_info.yaml'
        datetime_obj = datetime.datetime.today()
        report_doc = read_report_file(report_file, datetime_obj)

        self.assertIn(CARTRIDGE_SN, report_doc)
        self.assertIn(CHIP_SN, report_doc)
        self.assertIn(DEVICE_NAME, report_doc)
        self.assertIn(EXP_DEF_NAME, report_doc)
        self.assertEqual(report_doc[CARTRIDGE_SN], 'S0029859')
        self.assertEqual(report_doc[REAGENT_INFO], 'abl24')
        self.assertEqual(report_doc[RUN_DESCRIPTION], 'software')

    def test_update_get_run_reports(self):
        """
        test update_run_reports and get_run_reports
        update and retrieve reports from RUN_REPORT_COLLECTION
        """
        update_run_reports()
        reports, column_names, _ = get_run_reports()

        self.assertTrue(len(reports) > 0)


if __name__ == '__main__':
    unittest.main()
