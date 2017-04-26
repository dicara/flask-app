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
@date:   May 11th, 2016
'''

#=============================================================================
# Imports
#=============================================================================
from datetime import datetime
import os
import time
import unittest

from bioweb_api import app, FA_PROCESS_COLLECTION, HOSTNAME, PORT
from bioweb_api.DbConnector import DbConnector
from bioweb_api.tests.test_utils import post_data, get_data, \
    delete_data, add_url_argument

from bioweb_api.apis.ApiConstants import UUID, STATUS, JOB_TYPE_NAME, JOB_NAME, \
    EXP_DEF, ARCHIVE, PA_DOCUMENT, CONFIG_URL, OFFSETS, URL, ID_DOCUMENT, \
    UI_THRESHOLD, REPORT_URL, PLOT_URL, TRAINING_FACTOR, \
    AC_DOCUMENT, SCATTER_PLOT_URL, CTRL_THRESH, GT_DOCUMENT, \
    PNG_SUM_URL, REQUIRED_DROPS, PDF_URL, PNG_URL, SUBMIT_DATESTAMP, \
    START_DATESTAMP, FINISH_DATESTAMP, AC_TRAINING_FACTOR, PA_DATA_SOURCE, \
    ERROR, KDE_PNG_URL, KDE_PNG_SUM_URL, MAX_UNINJECTED_RATIO, EP_DOCUMENT, \
    UNIFIED_PDF, UNIFIED_PDF_URL

from bioweb_api.apis.full_analysis.FullAnalysisPostFunction import FULL_ANALYSIS
from bioweb_api.apis.full_analysis.FullAnalysisUtils import MakeUnifiedPDF

#=============================================================================
# Setup Logging
#=============================================================================
import tornado.options
tornado.options.parse_command_line()

#===============================================================================
# Private Static Variables
#===============================================================================
_FA_JOB = {
            STATUS : "succeeded",
            JOB_TYPE_NAME : "full_analysis",
            JOB_NAME : "2016-04-14_1259.50-beta179e9ca932-0",
            EXP_DEF : "ABL_24_V1",
            ARCHIVE : "2016-04-14_1259.50-beta17",
            SUBMIT_DATESTAMP: datetime.today(),
            START_DATESTAMP: datetime.today(),
            FINISH_DATESTAMP: datetime.today(),
        }

_PRIMARY_ANALYSIS_URL     = "/api/v1/PrimaryAnalysis"
_TEST_DIR                 = os.path.abspath(os.path.dirname(__file__))
_DB_CONNECTOR             = DbConnector.Instance()
_FULL_ANALYSIS_URL        = os.path.join("/api/v1/FullAnalysis", FULL_ANALYSIS)
_ARCHIVES_URL             = os.path.join(_PRIMARY_ANALYSIS_URL, 'Archives')
_HDF5S_URL                = os.path.join(_PRIMARY_ANALYSIS_URL, 'HDF5s')
_FA_HOTSPOT_JOBNAME       = "test_full_analysis_job"
_FA_EXPLORATORY_JOBNAME   = "test_exploratory_full_analysis_job"
_ARCHIVE_NAME             = "2016-08-17_1602.41-pilot5"
_EXP_DEF_HOTSPOT_NAME     = "Beta_24b_p1_V6"
_EXP_DEF_EXPLORATORY_NAME = "Exploratory_bioweb_test"
_OFFSETS                  = 30
_UI_THRESHOLD             = 4000
_MAX_UI_RATIO             = 1.5
_AC_TRAINING_FACTOR       = 100
_CTRL_THRESH              = 5
_REQUIRED_DROPS           = 0

_ID_REPORT_PATH           = os.path.join(_TEST_DIR, 'e21e96e1-5a7a-4a03-84bc-1c2ff1d213d9.yaml')
_GT_PNG_PATH              = os.path.join(_TEST_DIR, 'b05801d0-0f75-4c64-8df4-b2e6151a9277_scatter.png')
_GT_PNG_IND_PATH          = os.path.join(_TEST_DIR, 'beta_24_scatter_ind.pdf')
_GT_KDE_PATH              = os.path.join(_TEST_DIR, 'b05801d0-0f75-4c64-8df4-b2e6151a9277_kde.png')
_GT_KDE_IND_PATH          = os.path.join(_TEST_DIR, 'beta_24_kde_ind.pdf')
_GT_PDF_PATH              = os.path.join(_TEST_DIR, 'b05801d0-0f75-4c64-8df4-b2e6151a9277.pdf')
_OUTPUT_SA_PATH           = os.path.join(_TEST_DIR, 'sa_combined.pdf')
_OUTPUT_PDF_PATH          = os.path.join(_TEST_DIR, 'unified.pdf')

#=============================================================================
# TestCase
#=============================================================================
class TestFullAnalysisAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._fa_uuid = "eff5f811-c069-46bd-968d-eda61028dbc5"
        cls._fa_record = _FA_JOB
        cls._fa_record[UUID] = cls._fa_uuid

        cls._pa_uuid = "7837de22-9b54-463b-8491-9b7cef9fbd72"
        pa_record = {
            STATUS : "succeeded",
            UUID : cls._pa_uuid,
            CONFIG_URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._pa_uuid + ".cfg"),
            OFFSETS : 30,
            URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._pa_uuid),
            START_DATESTAMP: datetime.today(),
            FINISH_DATESTAMP: datetime.today(),
        }
        cls._fa_record[PA_DOCUMENT] = pa_record

        cls._id_uuid = "e21e96e1-5a7a-4a03-84bc-1c2ff1d213d9"
        id_record = {
            STATUS : "succeeded",
            UUID : cls._id_uuid,
            URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._id_uuid),
            UI_THRESHOLD : 4000,
            REPORT_URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._id_uuid + ".yaml"),
            PLOT_URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._id_uuid + ".png"),
            TRAINING_FACTOR : 800,
            START_DATESTAMP: datetime.today(),
            FINISH_DATESTAMP: datetime.today(),
        }
        cls._fa_record[ID_DOCUMENT] = id_record

        cls._ac_uuid = "4d78456c-c1ca-4113-a501-afe7fbeee86d"
        ac_record = {
            STATUS : "succeeded",
            UUID : cls._ac_uuid,
            URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._ac_uuid),
            SCATTER_PLOT_URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._ac_uuid + "_scatter.png"),
            CTRL_THRESH : 5,
            TRAINING_FACTOR : 100,
            START_DATESTAMP: datetime.today(),
            FINISH_DATESTAMP: datetime.today(),
        }
        cls._fa_record[AC_DOCUMENT] = ac_record

        cls._gt_uuid = "b05801d0-0f75-4c64-8df4-b2e6151a9277"
        gt_record = {
            STATUS : "succeeded",
            UUID : cls._gt_uuid,
            URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._gt_uuid + ".vcf"),
            REQUIRED_DROPS : 0,
            PDF_URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._gt_uuid + ".pdf"),
            PNG_URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._gt_uuid + "_scatter_ind.png"),
            PNG_SUM_URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._gt_uuid + "_scatter.png"),
            KDE_PNG_URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._gt_uuid + "_kde_ind.png"),
            KDE_PNG_SUM_URL : os.path.join("http://" + HOSTNAME, "results", str(PORT), cls._gt_uuid + "_kde.png"),
            START_DATESTAMP: datetime.today(),
            FINISH_DATESTAMP: datetime.today(),
        }
        cls._fa_record[GT_DOCUMENT] = gt_record

        _DB_CONNECTOR.insert(FA_PROCESS_COLLECTION, [cls._fa_record])

    @classmethod
    def tearDownClass(cls):
        _DB_CONNECTOR.remove(FA_PROCESS_COLLECTION,
                             {UUID: {'$in': [cls._fa_uuid]}})

    def setUp(self):
        self._client = app.test_client(self)

    def test_results_exist(self):
        """
        This tests that setUp properly inserts the full analysis result in
        the database and that the result files exist.
        """
        response = _DB_CONNECTOR.find_one(FA_PROCESS_COLLECTION, UUID,
                                          self._fa_uuid)

        msg = "No entries in the DB with UUID = %s" % self._fa_uuid
        self.assertTrue(response, msg)

        pa_result = os.path.join(_TEST_DIR, os.path.basename(response[PA_DOCUMENT][URL]))
        msg = "Primary analysis result file cannot be found: %s" % pa_result
        self.assertTrue(os.path.isfile(pa_result), msg)

        pa_config = os.path.join(_TEST_DIR, os.path.basename(response[PA_DOCUMENT][CONFIG_URL]))
        msg = "Primary analysis config file cannot be found: %s" % pa_config
        self.assertTrue(os.path.isfile(pa_config), msg)

        id_result = os.path.join(_TEST_DIR, os.path.basename(response[ID_DOCUMENT][URL]))
        msg = "Identity result file cannot be found: %s" % id_result
        self.assertTrue(os.path.isfile(id_result), msg)

        id_report = os.path.join(_TEST_DIR, os.path.basename(response[ID_DOCUMENT][REPORT_URL]))
        msg = "Identity report file cannot be found: %s" % id_report
        self.assertTrue(os.path.isfile(id_report), msg)

        id_plot = os.path.join(_TEST_DIR, os.path.basename(response[ID_DOCUMENT][PLOT_URL]))
        msg = "Identity plot file cannot be found: %s" % id_plot
        self.assertTrue(os.path.isfile(id_plot), msg)

        ac_result = os.path.join(_TEST_DIR, os.path.basename(response[AC_DOCUMENT][URL]))
        msg = "Assay caller result file cannot be found: %s" % ac_result
        self.assertTrue(os.path.isfile(ac_result), msg)

        ac_scatter = os.path.join(_TEST_DIR, os.path.basename(response[AC_DOCUMENT][SCATTER_PLOT_URL]))
        msg = "Assay caller scatter plot file cannot be found: %s" % ac_scatter
        self.assertTrue(os.path.isfile(ac_scatter), msg)

        gt_result = os.path.join(_TEST_DIR, os.path.basename(response[GT_DOCUMENT][URL]))
        msg = "Genotyper result file cannot be found: %s" % gt_result
        self.assertTrue(os.path.isfile(gt_result), msg)

        gt_png = os.path.join(_TEST_DIR, os.path.basename(response[GT_DOCUMENT][PNG_URL]))
        msg = "Genotyper PNG file cannot be found: %s" % gt_png
        self.assertTrue(os.path.isfile(gt_png), msg)

        gt_png_sum = os.path.join(_TEST_DIR, os.path.basename(response[GT_DOCUMENT][PNG_SUM_URL]))
        msg = "Genotyper PNG sum file cannot be found: %s" % gt_png_sum
        self.assertTrue(os.path.isfile(gt_png_sum), msg)

        gt_kde = os.path.join(_TEST_DIR, os.path.basename(response[GT_DOCUMENT][PNG_URL]))
        msg = "Genotyper PNG file cannot be found: %s" % gt_kde
        self.assertTrue(os.path.isfile(gt_kde), msg)

        gt_kde_sum = os.path.join(_TEST_DIR, os.path.basename(response[GT_DOCUMENT][PNG_SUM_URL]))
        msg = "Genotyper PNG sum file cannot be found: %s" % gt_kde_sum
        self.assertTrue(os.path.isfile(gt_kde_sum), msg)

        gt_pdf = os.path.join(_TEST_DIR, os.path.basename(response[GT_DOCUMENT][PDF_URL]))
        msg = "Genotyper PDF file cannot be found: %s" % gt_pdf
        self.assertTrue(os.path.isfile(gt_pdf), msg)

    def test_full_analysis(self):
        """
        Test the POST, GET and DELETE full analysis APIs
        """
        # run these to ensure that the instance of mongo database used by
        # bamboo is updated with the latest image stacks and HDF5 archives
        get_data(self, _ARCHIVES_URL + '?refresh=true&format=json', 200)
        get_data(self, _HDF5S_URL + '?refresh=true&format=json', 200)

        # Construct url
        url = _FULL_ANALYSIS_URL
        url = add_url_argument(url, PA_DATA_SOURCE, _ARCHIVE_NAME, True)
        url = add_url_argument(url, JOB_NAME, _FA_HOTSPOT_JOBNAME)
        url = add_url_argument(url, EXP_DEF, _EXP_DEF_HOTSPOT_NAME)
        url = add_url_argument(url, OFFSETS, _OFFSETS)
        url = add_url_argument(url, UI_THRESHOLD, _UI_THRESHOLD)
        url = add_url_argument(url, MAX_UNINJECTED_RATIO, _MAX_UI_RATIO)
        url = add_url_argument(url, AC_TRAINING_FACTOR, _AC_TRAINING_FACTOR)
        url = add_url_argument(url, CTRL_THRESH, _CTRL_THRESH)
        url = add_url_argument(url, REQUIRED_DROPS, _REQUIRED_DROPS)

        # Submit full analysis job
        response    = post_data(self, url, 200)
        fa_uuid     = response[FULL_ANALYSIS][0][UUID]

        # Test that submitting two jobs with the same name fails and returns
        # the appropriate error code.
        post_data(self, url, 403)

        running = True
        while running:
            time.sleep(10)
            response = get_data(self, _FULL_ANALYSIS_URL, 200)
            for job in response[FULL_ANALYSIS]:
                if fa_uuid == job[UUID]:
                    job_details = job
                    running     = job_details[STATUS] == 'running'

        msg = "%s doesn't exist in job_details." % PA_DOCUMENT
        self.assertTrue(PA_DOCUMENT in job_details, msg)
        if ERROR in job_details[PA_DOCUMENT]:
            self.assertTrue(False, job_details[PA_DOCUMENT][ERROR])

        msg = "%s doesn't exist in job_details." % ID_DOCUMENT
        self.assertTrue(ID_DOCUMENT in job_details, msg)
        if ERROR in job_details[ID_DOCUMENT]:
            self.assertTrue(False, job_details[ID_DOCUMENT][ERROR])

        msg = "%s doesn't exist in job_details." % AC_DOCUMENT
        self.assertTrue(AC_DOCUMENT in job_details, msg)
        if ERROR in job_details[AC_DOCUMENT]:
            self.assertTrue(False, job_details[AC_DOCUMENT][ERROR])

        msg = "%s doesn't exist in job_details." % GT_DOCUMENT
        self.assertTrue(GT_DOCUMENT in job_details, msg)
        if ERROR in job_details[GT_DOCUMENT]:
            self.assertTrue(False, job_details[GT_DOCUMENT][ERROR])

        msg = "%s doesn't exist in job_details." % UNIFIED_PDF
        self.assertTrue(UNIFIED_PDF in job_details, msg)

        msg = "%s doesn't exist in job_details." % UNIFIED_PDF_URL
        self.assertTrue(UNIFIED_PDF_URL in job_details, msg)

        if ERROR in job_details:
            self.assertTrue(False, job_details[ERROR])

        # Delete full analysis job
        delete_url = add_url_argument(_FULL_ANALYSIS_URL, UUID, fa_uuid, True)
        delete_data(self, delete_url, 200)

        # Ensure job no longer exists in the database
        response = get_data(self, _FULL_ANALYSIS_URL, 200)
        for job in response[FULL_ANALYSIS]:
            msg = "Full analysis job %s still exists in database." % fa_uuid
            self.assertNotEqual(fa_uuid, job[UUID], msg)

    def test_make_unified_pdf(self):
        """
        test MakeUnifiedPDF class, create an unified PDF report for full analysis
        job
        """
        make_pdf = MakeUnifiedPDF(_FA_JOB)
        make_pdf._combine_sa(_OUTPUT_SA_PATH,
                             _ID_REPORT_PATH,
                             _GT_PNG_IND_PATH,
                             _GT_PNG_PATH,
                             _GT_KDE_IND_PATH,
                             _GT_KDE_PATH,
                             )
        self.assertTrue(os.path.isfile(_OUTPUT_SA_PATH))

        make_pdf._merge_pdfs(_OUTPUT_PDF_PATH, _OUTPUT_SA_PATH, _GT_PDF_PATH)
        self.assertTrue(os.path.isfile(_OUTPUT_PDF_PATH))

        os.unlink(_OUTPUT_SA_PATH)
        os.unlink(_OUTPUT_PDF_PATH)

    def test_full_analysis_exploratory(self):
        """
        Test the POST and DELETE full analysis API with exploratory experiment definition.
        """
        # Construct url
        url = _FULL_ANALYSIS_URL
        url = add_url_argument(url, PA_DATA_SOURCE, _ARCHIVE_NAME, True)
        url = add_url_argument(url, JOB_NAME, _FA_EXPLORATORY_JOBNAME)
        url = add_url_argument(url, EXP_DEF, _EXP_DEF_EXPLORATORY_NAME)
        url = add_url_argument(url, OFFSETS, _OFFSETS)
        url = add_url_argument(url, UI_THRESHOLD, _UI_THRESHOLD)
        url = add_url_argument(url, MAX_UNINJECTED_RATIO, _MAX_UI_RATIO)
        url = add_url_argument(url, AC_TRAINING_FACTOR, _AC_TRAINING_FACTOR)
        url = add_url_argument(url, CTRL_THRESH, _CTRL_THRESH)
        url = add_url_argument(url, REQUIRED_DROPS, _REQUIRED_DROPS)

        # Submit full analysis job
        response    = post_data(self, url, 200)
        fa_uuid     = response[FULL_ANALYSIS][0][UUID]

        # Test that submitting two jobs with the same name fails and returns
        # the appropriate error code.
        post_data(self, url, 403)

        running = True
        while running:
            time.sleep(10)
            response = get_data(self, _FULL_ANALYSIS_URL, 200)
            for job in response[FULL_ANALYSIS]:
                if fa_uuid == job[UUID]:
                    job_details = job
                    running     = job_details[STATUS] == 'running'

        msg = "%s doesn't exist in job_details." % PA_DOCUMENT
        self.assertTrue(PA_DOCUMENT in job_details, msg)
        if ERROR in job_details[PA_DOCUMENT]:
            self.assertTrue(False, job_details[PA_DOCUMENT][ERROR])

        msg = "%s doesn't exist in job_details." % ID_DOCUMENT
        self.assertTrue(ID_DOCUMENT in job_details, msg)
        if ERROR in job_details[ID_DOCUMENT]:
            self.assertTrue(False, job_details[ID_DOCUMENT][ERROR])

        msg = "%s doesn't exist in job_details." % AC_DOCUMENT
        self.assertTrue(AC_DOCUMENT in job_details, msg)
        if ERROR in job_details[AC_DOCUMENT]:
            self.assertTrue(False, job_details[AC_DOCUMENT][ERROR])

        msg = "%s doesn't exist in job_details." % EP_DOCUMENT
        self.assertTrue(EP_DOCUMENT in job_details, msg)
        if ERROR in job_details[EP_DOCUMENT]:
            self.assertTrue(False, job_details[EP_DOCUMENT][ERROR])

        msg = "%s doesn't exist in job_details." % UNIFIED_PDF
        self.assertTrue(UNIFIED_PDF in job_details, msg)

        msg = "%s doesn't exist in job_details." % UNIFIED_PDF_URL
        self.assertTrue(UNIFIED_PDF_URL in job_details, msg)

        if ERROR in job_details:
            self.assertTrue(False, job_details[ERROR])

        # Delete full analysis job
        delete_url = add_url_argument(_FULL_ANALYSIS_URL, UUID, fa_uuid, True)
        delete_data(self, delete_url, 200)

        # Ensure job no longer exists in the database
        response = get_data(self, _FULL_ANALYSIS_URL, 200)
        for job in response[FULL_ANALYSIS]:
            msg = "Full analysis job %s still exists in database." % fa_uuid
            self.assertNotEqual(fa_uuid, job[UUID], msg)

if __name__ == '__main__':
    unittest.main()
