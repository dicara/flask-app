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
@date:   April 25th, 2016
'''

#=============================================================================
# Imports
#=============================================================================
import os
from random import choice
import shutil
from string import ascii_letters
import traceback

from PyPDF2 import PdfFileMerger
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import utils

from bioweb_api import TMP_PATH, FA_PROCESS_COLLECTION, EXP_DEF_COLLECTION, \
    RUN_REPORT_COLLECTION
from bioweb_api.DbConnector import DbConnector
from bioweb_api.utilities.io_utilities import safe_make_dirs, get_results_folder, \
    get_results_url
from bioweb_api.apis.ApiConstants import ID, UUID, STATUS, PA_DOCUMENT, ID_DOCUMENT, \
     AC_DOCUMENT, GT_DOCUMENT, OFFSETS, ID_TRAINING_FACTOR, UI_THRESHOLD, AC_TRAINING_FACTOR, \
     CTRL_THRESH, REQUIRED_DROPS, DIFF_PARAMS, TRAINING_FACTOR, UNIFIED_PDF, UNIFIED_PDF_URL, \
     SUCCEEDED, REPORT_URL, PNG_URL, PNG_SUM_URL, KDE_PNG_URL, KDE_PNG_SUM_URL, \
     PDF_URL, VARIANTS, NAME, MAX_UNINJECTED_RATIO, CTRL_FILTER, IGNORE_LOWEST_BARCODE, \
     AC_MODEL, PICO1_DYE, USE_PICO1_FILTER, EP_DOCUMENT, ARCHIVE, DEV_MODE, DEFAULT_DEV_MODE, \
     IMAGE_STACKS, EXP_DEF
from primary_analysis.dye_model import DEFAULT_OFFSETS
from secondary_analysis.constants import ID_TRAINING_FACTOR as DEFAULT_ID_TRAINING_FACTOR
from secondary_analysis.constants import AC_TRAINING_FACTOR as DEFAULT_AC_TRAINING_FACTOR
from secondary_analysis.constants import UNINJECTED_THRESHOLD as DEFAULT_UNINJECTED_THRESHOLD
from secondary_analysis.constants import UNINJECTED_RATIO as DEFAULT_UNINJECTED_RATIO
from secondary_analysis.constants import AC_CTRL_THRESHOLD as DEFAULT_AC_CTRL_THRESHOLD
from secondary_analysis.constants import AC_MODEL_NAIVE_BAYES as DEFAULT_AC_MODEL
from gbutils.vcf_pdf_writer import PDFWriter, FONT_NAME_STD, FONT_SIZE
from bioweb_api.utilities.logging_utilities import APP_LOGGER


#=============================================================================
# Local static variables
#=============================================================================
PARAM_MAP = {OFFSETS:               PA_DOCUMENT,
             ID_TRAINING_FACTOR:    ID_DOCUMENT,
             UI_THRESHOLD:          ID_DOCUMENT,
             MAX_UNINJECTED_RATIO:  ID_DOCUMENT,
             USE_PICO1_FILTER:      ID_DOCUMENT,
             PICO1_DYE:             ID_DOCUMENT,
             AC_TRAINING_FACTOR:    AC_DOCUMENT,
             CTRL_THRESH:           AC_DOCUMENT,
             REQUIRED_DROPS:        GT_DOCUMENT,
             CTRL_FILTER:           AC_DOCUMENT,
             AC_MODEL:              AC_DOCUMENT,
             IGNORE_LOWEST_BARCODE: ID_DOCUMENT,
             DEV_MODE:              ID_DOCUMENT}

DEFAULTS = {OFFSETS:            abs(DEFAULT_OFFSETS[0]),
            ID_TRAINING_FACTOR: DEFAULT_ID_TRAINING_FACTOR,
            UI_THRESHOLD:       DEFAULT_UNINJECTED_THRESHOLD,
            MAX_UNINJECTED_RATIO: DEFAULT_UNINJECTED_RATIO,
            USE_PICO1_FILTER:   True,
            PICO1_DYE:          "pe-cy7",
            AC_TRAINING_FACTOR: DEFAULT_AC_TRAINING_FACTOR,
            CTRL_THRESH:        DEFAULT_AC_CTRL_THRESHOLD,
            REQUIRED_DROPS:     0,
            CTRL_FILTER:        False,
            AC_MODEL:           DEFAULT_AC_MODEL,
            IGNORE_LOWEST_BARCODE: True,
            DEV_MODE:           DEFAULT_DEV_MODE}

_DB_CONNECTOR = DbConnector.Instance()

#=============================================================================
# Functions and Classes
#=============================================================================
def convert_param_name(param):
    return TRAINING_FACTOR if param in [ID_TRAINING_FACTOR, AC_TRAINING_FACTOR] \
            else param

def update_fa_docs(jobs):
    """
    Update full analysis jobs upon get request
    1. Identity parameters in full analysis jobs that are different from default values
    2. Add unified PDF
    """
    if not jobs: return []
    for job in jobs:
        if ID in job:
            del job[ID]

        add_diff_params(job)
    return jobs

def add_diff_params(fa_job):
    diff_params = dict()

    # check if a non-default experiment definition is used.
    run_report = _DB_CONNECTOR.find_one(RUN_REPORT_COLLECTION, IMAGE_STACKS,
                                        fa_job[ARCHIVE])
    if run_report is not None and run_report[EXP_DEF] != fa_job[EXP_DEF]:
        diff_params[EXP_DEF] = fa_job[EXP_DEF]

    for param, doc_name in PARAM_MAP.items():
        if doc_name not in fa_job: continue
        param_name = convert_param_name(param)
        if param_name in fa_job[doc_name]:
            val = fa_job[doc_name][param_name]
            if val != DEFAULTS[param]:
                diff_params[param] = val

    fa_job[DIFF_PARAMS] = diff_params

def add_unified_pdf(fa_job, document_list):
    if UNIFIED_PDF_URL in fa_job and fa_job[UNIFIED_PDF_URL] \
            or any(indiv_doc not in fa_job or STATUS not in fa_job[indiv_doc]
                   or fa_job[indiv_doc][STATUS] != SUCCEEDED
                   for indiv_doc in document_list):
        return False

    make_pdf = MakeUnifiedPDF(fa_job)
    make_pdf.save()

    fa_uuid = fa_job[UUID]
    results_folder = get_results_folder()
    fa_pdf_path = os.path.join(results_folder, fa_uuid + '.pdf')
    if not os.path.isfile(fa_pdf_path):
        raise Exception("Failed in making the unified pdf report.")
    else:
        pdf_url = get_results_url(fa_pdf_path)

        fa_job[UNIFIED_PDF]      = fa_pdf_path
        fa_job[UNIFIED_PDF_URL]  = pdf_url
        update = { '$set' : {
                              UNIFIED_PDF: fa_pdf_path,
                              UNIFIED_PDF_URL: pdf_url,
                            }
                 }
        _DB_CONNECTOR.update(FA_PROCESS_COLLECTION, {UUID: fa_uuid}, update)
        return True

def is_param_diff(fa_job, doc_name, parameters):
    """
    Check whether the input parameters are different from defaults

    @param fa_job:              A full analysis job document
    @param doc_name:            Document type of a job document, e.g., PA_DOCUMENT
    @param parameters:          New input parameters
    """
    for param in PARAM_MAP:
        if param in parameters:
            if PARAM_MAP[param] != doc_name: continue
            param_name = convert_param_name(param)
            if param_name in fa_job and parameters[param] != fa_job[param_name]:
                return True
    return False

generate_random_str = lambda length : ''.join(choice(ascii_letters) for _ in xrange(length))

def get_variants(exp_def_name):
    """
    Return a list of variants in the experiment definition file.
    """
    APP_LOGGER.info("Retrieving list of variants from %s" % (exp_def_name,))

    exp_def_doc = _DB_CONNECTOR.find_one(EXP_DEF_COLLECTION,
                                         NAME,
                                         exp_def_name)
    if exp_def_doc is not None:
        APP_LOGGER.info("Experiment definition %s found in EXP_DEF_COLLECTION."
                        % (exp_def_name,))
        return exp_def_doc[VARIANTS]

    APP_LOGGER.debug("Failed to find experiment definition %s from EXP_DEF_COLLECTION."
                     % (exp_def_name,))
    return []


class MakeUnifiedPDF(PDFWriter):
    """
    Make an unified pdf report of a succeeded full analysis job
    """
    def __init__(self, fa_job):
        self.uuid                = fa_job[UUID]
        id_report_url            = fa_job[ID_DOCUMENT][REPORT_URL]

        doc = GT_DOCUMENT
        if GT_DOCUMENT in fa_job:
            vcf_pdf_url          = fa_job[GT_DOCUMENT][PDF_URL]
        elif EP_DOCUMENT in fa_job:
            doc                  = EP_DOCUMENT
            vcf_pdf_url          = None
        else:
            raise Exception("Genotyper or exploratory document is missing from full analysis document, %s."
                            % fa_job)
        png_url                  = fa_job[doc][PNG_URL]
        png_sum_url              = fa_job[doc][PNG_SUM_URL]
        kde_url                  = fa_job[doc][KDE_PNG_URL]
        kde_sum_url              = fa_job[doc][KDE_PNG_SUM_URL]

        results_folder           = get_results_folder()
        self.id_report_path      = os.path.join(results_folder, os.path.basename(id_report_url))
        self.png_path            = os.path.join(results_folder, os.path.basename(png_url))
        self.png_sum_path        = os.path.join(results_folder, os.path.basename(png_sum_url))
        self.kde_path            = os.path.join(results_folder, os.path.basename(kde_url))
        self.kde_sum_path        = os.path.join(results_folder, os.path.basename(kde_sum_url))

        self.vcf_pdf_path        = None
        if vcf_pdf_url is not None:
            self.vcf_pdf_path    = os.path.join(results_folder, os.path.basename(vcf_pdf_url))

        self.fa_pdf_path         = os.path.join(results_folder, self.uuid + '.pdf')
        self.tmp_path            = os.path.join(TMP_PATH, self.uuid)
        self.tmp_sa_path         = os.path.join(self.tmp_path, 'sa_combined.pdf')
        self.tmp_pdf_path        = os.path.join(self.tmp_path, 'fa_unified.pdf')

    def save(self):
        try:
            safe_make_dirs(self.tmp_path)

            combine_sa = self._combine_sa(self.tmp_sa_path,
                                          self.id_report_path,
                                          self.png_path,
                                          self.png_sum_path,
                                          self.kde_path,
                                          self.kde_sum_path)
            if not combine_sa:
                raise Exception("Failed to combine secondary analysis results.")

            if not os.path.isfile(self.tmp_sa_path):
                raise Exception("Failed to find temporary combined secondary analysis file")

            self._merge_pdfs(self.tmp_pdf_path, self.vcf_pdf_path, self.tmp_sa_path)

            if not os.path.isfile(self.tmp_pdf_path):
                raise Exception("Failed to merge PDF files.")

            shutil.copy(self.tmp_pdf_path, self.fa_pdf_path)
        finally:
            shutil.rmtree(self.tmp_path, ignore_errors=True)

    def _combine_sa(self, output_path, id_report_path, gt_png_path,
            gt_png_sum_path, gt_kde_path, gt_kde_sum_path):
        """
        Combine Identity report, Assay Caller scatter plot, and Genotyper PNG

        @param id_report_path:          pathname of identity report
        @param gt_png_path:             pathname of genotyper scatter PNG
        @param gt_png_sum_path:         pathname of genotyper scatter sum PNG
        @param gt_kde_path:             pathname of genotyper KDE PNG
        @param gt_kde_sum_path:         pathname of genotyper KDE sum PNG
        """
        try:
            path = output_path + '_png_id'
            doc = SimpleDocTemplate(path, pagesize=landscape(letter))
            story = list()

            story.append(self.get_image(gt_png_sum_path))
            story.append(PageBreak())

            story.append(self.get_image(gt_kde_sum_path))
            story.append(PageBreak())

            styles = getSampleStyleSheet()
            id_title = Paragraph('Identity Report', styles['h2'])
            story.append(id_title)
            story.append(Spacer(1, 0.2*inch))

            with open(id_report_path, 'r') as id_report:
                lines = id_report.readlines()
                for line in lines:
                    styles = getSampleStyleSheet()
                    left_indent = (len(line) - len(line.lstrip())) * 5
                    styles.add(ParagraphStyle(name='custom_style',
                                              fontName=FONT_NAME_STD,
                                              fontSize=FONT_SIZE,
                                              leftIndent=left_indent))
                    p = Paragraph(line, styles['custom_style'])
                    story.append(p)
                story.append(PageBreak())

            doc.build(story, onFirstPage=self.standard_page,
                      onLaterPages=self.standard_page)

            self._merge_pdfs(output_path, gt_png_path, gt_kde_path, path)

            os.unlink(path)
            return True
        except:
            APP_LOGGER.exception(traceback.format_exc())
            return False

    @staticmethod
    def _merge_pdfs(output_path, *args):
        """
        Merge multiple PDF files into one file
        """
        merger = PdfFileMerger()
        for path in args:
            if path is not None:
                merger.append(path)
        merger.write(output_path)

    @staticmethod
    def get_image(path, max_width=8*inch, max_height=6.08*inch):
        """
        Resize a image and return an reportlab.platypus.Image object
        """
        img = utils.ImageReader(path)
        iw, ih = img.getSize()
        aspect = ih / float(iw)
        if iw >= ih and (max_width * aspect) < max_height:
            return Image(path,
                         width=max_width,
                         height=(max_width * aspect))
        else:
            return Image(path,
                         width=(max_height / aspect),
                         height=max_height)
