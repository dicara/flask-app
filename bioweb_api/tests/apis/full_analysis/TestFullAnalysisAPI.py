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
import json
import os
import unittest

from bioweb_api import app, FA_PROCESS_COLLECTION
from bioweb_api.apis.full_analysis.FullAnalysisUtils import MakeUnifiedPDF

#===============================================================================
# Private Static Variables
#===============================================================================
_FA_JOB = {
            "status" : "succeeded",
            "uuid" : "188d1ed1-9a54-4643-ac5e-560faeb3a731",
            "job_type" : "full_analysis",
            "job_name" : "2016-04-14_1259.50-beta179e9ca932-0",
            "exp_def" : "ABL_24_V1",
            "archive" : "2016-04-14_1259.50-beta17",
            "pa_document" : {
                "status" : "succeeded",
                "uuid" : "a053fb11-4f53-47dc-a6c7-5b7d7e69e32c",
                "config_url" : "http://192.168.33.10/results/8020/a053fb11-4f53-47dc-a6c7-5b7d7e69e32c.cfg",
                "offsets" : 30,
                "url" : "http://192.168.33.10/results/8020/a053fb11-4f53-47dc-a6c7-5b7d7e69e32c",
            },
            "id_document" : {
                "status" : "succeeded",
                "uuid" : "55401115-684f-48cc-afb3-5a4801887bed",
                "url" : "http://192.168.33.10/results/8020/55401115-684f-48cc-afb3-5a4801887bed",
                "ui_threshold" : 4000,
                "report_url" : "http://192.168.33.10/results/8020/55401115-684f-48cc-afb3-5a4801887bed.yaml",
                "plot_url" : "http://192.168.33.10/results/8020/55401115-684f-48cc-afb3-5a4801887bed.png",
                "training_factor" : 800,
                "pf_training_factor" : 100
            },
            "ac_document" : {
                "status" : "succeeded",
                "kde_plot_url" : "http://192.168.33.10/results/8020/4c07f709-9cd1-444e-8eb1-b43f447bd397_kde.png",
                "uuid" : "4c07f709-9cd1-444e-8eb1-b43f447bd397",
                "url" : "http://192.168.33.10/results/8020/4c07f709-9cd1-444e-8eb1-b43f447bd397",
                "scatter_plot_url" : "http://192.168.33.10/results/8020/4c07f709-9cd1-444e-8eb1-b43f447bd397_scatter.png",
                "ctrl_thresh" : 5,
                "training_factor" : 100
            },
            "gt_document" : {
                "status" : "succeeded",
                "png_sum_url" : "http://192.168.33.10/results/8020/e500ad84-8b2d-4978-a58f-b57dda95fd2c_sum.png",
                "uuid" : "e500ad84-8b2d-4978-a58f-b57dda95fd2c",
                "url" : "http://192.168.33.10/results/8020/e500ad84-8b2d-4978-a58f-b57dda95fd2c.vcf",
                "required_drops" : 0,
                "pdf_url" : "http://192.168.33.10/results/8020/e500ad84-8b2d-4978-a58f-b57dda95fd2c.pdf",
                "png_url" : "http://192.168.33.10/results/8020/e500ad84-8b2d-4978-a58f-b57dda95fd2c.png"
            }
        }

_TEST_DIR               = os.path.abspath(os.path.dirname(__file__))
_ID_REPORT_PATH         = os.path.join(_TEST_DIR, 'id_report.yaml')
_AC_SCATTER_PLOT_PATH   = os.path.join(_TEST_DIR, 'ac_scatter.png')
_GT_PNG_PATH            = os.path.join(_TEST_DIR, 'gt.png')
_GT_PDF_PATH            = os.path.join(_TEST_DIR, 'gt.pdf')
_OUTPUT_SA_PATH         = os.path.join(_TEST_DIR, 'sa_combined.pdf')
_OUTPUT_PDF_PATH        = os.path.join(_TEST_DIR, 'unified.pdf')

#=============================================================================
# TestCase
#=============================================================================
class TestFullAnalysisAPI(unittest.TestCase):
    def setUp(self):
        self._client = app.test_client(self)

    def test_make_unified_pdf(self):
        """
        test MakeUnifiedPDF class, create an unified PDF report for full analysis
        job
        """
        make_pdf = MakeUnifiedPDF(_FA_JOB)
        make_pdf._combine_sa(_OUTPUT_SA_PATH,
                             _ID_REPORT_PATH,
                             _AC_SCATTER_PLOT_PATH,
                             _GT_PNG_PATH)
        self.assertTrue(os.path.isfile(_OUTPUT_SA_PATH))

        make_pdf._merge_pdfs(_OUTPUT_PDF_PATH, _OUTPUT_SA_PATH, _GT_PDF_PATH)
        self.assertTrue(os.path.isfile(_OUTPUT_PDF_PATH))

        # os.unlink(_OUTPUT_SA_PATH)
        # os.unlink(_OUTPUT_PDF_PATH)

if __name__ == '__main__':
    unittest.main()
