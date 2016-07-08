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
from collections import OrderedDict
import os
from random import choice
import shutil
from string import ascii_letters

from PyPDF2 import PdfFileMerger
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import utils

from bioweb_api import RESULTS_PATH, TMP_PATH, FA_PROCESS_COLLECTION, HOSTNAME, \
     PORT, EXP_DEF_COLLECTION
from bioweb_api.DbConnector import DbConnector
from bioweb_api.utilities.io_utilities import safe_make_dirs
from bioweb_api.apis.ApiConstants import ID, UUID, STATUS, PA_DOCUMENT, ID_DOCUMENT, \
     AC_DOCUMENT, GT_DOCUMENT, OFFSETS, ID_TRAINING_FACTOR, \
     UI_THRESHOLD, AC_TRAINING_FACTOR, CTRL_THRESH, \
     REQUIRED_DROPS, DIFF_PARAMS, TRAINING_FACTOR, UNIFIED_PDF, UNIFIED_PDF_URL, \
     SUCCEEDED, REPORT_URL, SCATTER_PLOT_URL, PNG_URL, URL, PDF_URL, VARIANTS
from primary_analysis.dye_model import DEFAULT_OFFSETS
from primary_analysis.experiment.experiment_definitions import ExperimentDefinitions
from secondary_analysis.constants import ID_TRAINING_FACTOR_MAX as DEFAULT_ID_TRAINING_FACTOR
from secondary_analysis.constants import AC_TRAINING_FACTOR as DEFAULT_AC_TRAINING_FACTOR
from secondary_analysis.constants import UNINJECTED_THRESHOLD as DEFAULT_UNINJECTED_THRESHOLD
from secondary_analysis.constants import AC_CTRL_THRESHOLD as DEFAULT_AC_CTRL_THRESHOLD
from gbutils.vcf_pdf_writer import PDFWriter, FONT_NAME_STD, FONT_SIZE
from expdb.defs import HotspotExperiment
from bioweb_api.utilities.logging_utilities import APP_LOGGER


#=============================================================================
# Local static variables
#=============================================================================
PARAM_MAP = {OFFSETS:               PA_DOCUMENT,
             ID_TRAINING_FACTOR:    ID_DOCUMENT,
             UI_THRESHOLD:          ID_DOCUMENT,
             AC_TRAINING_FACTOR:    AC_DOCUMENT,
             CTRL_THRESH:           AC_DOCUMENT,
             REQUIRED_DROPS:        GT_DOCUMENT}

DEFAULTS = {OFFSETS:            abs(DEFAULT_OFFSETS[0]),
            ID_TRAINING_FACTOR: DEFAULT_ID_TRAINING_FACTOR,
            UI_THRESHOLD:       DEFAULT_UNINJECTED_THRESHOLD,
            AC_TRAINING_FACTOR: DEFAULT_AC_TRAINING_FACTOR,
            CTRL_THRESH:        DEFAULT_AC_CTRL_THRESHOLD,
            REQUIRED_DROPS:     0}

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
        update_single_job(job)
    return jobs

def update_single_job(fa_job):
    fa_uuid = fa_job[UUID]
    fa_job = _DB_CONNECTOR.find_one(FA_PROCESS_COLLECTION, UUID, fa_uuid)
    if not fa_job:
        raise Exception("Job with uuid %s is not found." % fa_uuid)

    add_diff_params(fa_job)

def add_diff_params(fa_job):
    diff_params = dict()
    for param, doc_name in PARAM_MAP.items():
        if doc_name not in fa_job: continue
        param_name = convert_param_name(param)
        if param_name in fa_job[doc_name]:
            val = fa_job[doc_name][param_name]
            if val != DEFAULTS[param]:
                diff_params[param] = val
    fa_job[DIFF_PARAMS] = diff_params
    update = { '$set': {DIFF_PARAMS: diff_params} }
    _DB_CONNECTOR.update(FA_PROCESS_COLLECTION, {UUID: fa_job[UUID]}, update)
    return True

def add_unified_pdf(fa_job):
    if UNIFIED_PDF_URL in fa_job and fa_job[UNIFIED_PDF_URL] \
            or any(indiv_doc not in fa_job or STATUS not in fa_job[indiv_doc]
                   or fa_job[indiv_doc][STATUS] != SUCCEEDED
                   for indiv_doc in set(PARAM_MAP.values())):
        return False

    make_pdf = MakeUnifiedPDF(fa_job)
    make_pdf.save()

    fa_uuid = fa_job[UUID]
    fa_pdf_path = os.path.join(RESULTS_PATH, fa_uuid + '.pdf')
    if not os.path.isfile(fa_pdf_path):
        raise Exception("Failed in making the unified pdf report.")
    else:
        pdf_url = 'http://%s/results/%s/%s' % (HOSTNAME, PORT,
                                               os.path.basename(fa_pdf_path))
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
    APP_LOGGER.info("Retrieving list of variants from %s" % exp_def_name)

    exp_def_fetcher = ExperimentDefinitions()
    exp_def_uuid = exp_def_fetcher.get_experiment_uuid(exp_def_name)

    exp_def_doc = _DB_CONNECTOR.find_one(EXP_DEF_COLLECTION, UUID, exp_def_uuid)
    if exp_def_doc is not None:
        return exp_def_doc[VARIANTS]

    exp_def = exp_def_fetcher.get_experiment_defintion(exp_def_uuid)
    experiment = HotspotExperiment.from_dict(exp_def)

    variant_strings = list()
    for variant in experiment.variants:
        loc = variant.coding_pos if variant.coding_pos is not None else variant.location
        variant_strings.append('{0} {1}{2}>{3}'.format(variant.reference,
                                                       loc,
                                                       variant.expected,
                                                       variant.variation))
    doc = {UUID: exp_def_uuid, VARIANTS: variant_strings}
    _DB_CONNECTOR.insert(EXP_DEF_COLLECTION, [doc])
    return variant_strings

class MakeUnifiedPDF(PDFWriter):
    """
    Make an unified pdf report of a succeeded full analysis job
    """
    def __init__(self, fa_job):
        self.uuid                = fa_job[UUID]
        id_report_url            = fa_job[ID_DOCUMENT][REPORT_URL]
        ac_scatter_plot_url      = fa_job[AC_DOCUMENT][SCATTER_PLOT_URL]
        gt_png_url               = fa_job[GT_DOCUMENT][PNG_URL]
        gt_pdf_url               = fa_job[GT_DOCUMENT][PDF_URL]

        self.id_report_path      = os.path.join(RESULTS_PATH, os.path.basename(id_report_url))
        self.ac_scatter_plot_path= os.path.join(RESULTS_PATH, os.path.basename(ac_scatter_plot_url))
        self.gt_png_path         = os.path.join(RESULTS_PATH, os.path.basename(gt_png_url))
        self.gt_pdf_path         = os.path.join(RESULTS_PATH, os.path.basename(gt_pdf_url))

        self.fa_pdf_path         = os.path.join(RESULTS_PATH, self.uuid + '.pdf')
        self.tmp_path            = os.path.join(TMP_PATH, self.uuid)
        self.tmp_sa_path         = os.path.join(self.tmp_path, 'sa_combined.pdf')
        self.tmp_pdf_path        = os.path.join(self.tmp_path, 'fa_unified.pdf')

    def save(self):
        try:
            safe_make_dirs(self.tmp_path)

            combine_sa = self._combine_sa(self.tmp_sa_path,
                                          self.id_report_path,
                                          self.ac_scatter_plot_path,
                                          self.gt_png_path)
            if not combine_sa:
                raise Exception("Failed to combine secondary analysis results.")

            if not os.path.isfile(self.tmp_sa_path):
                raise Exception("Failed to find temporary combined secondary analysis file")

            self._merge_pdfs(self.tmp_pdf_path, self.gt_pdf_path, self.tmp_sa_path)

            if not os.path.isfile(self.tmp_pdf_path):
                raise Exception("Failed to merge PDF files.")

            shutil.copy(self.tmp_pdf_path, self.fa_pdf_path)
        finally:
            shutil.rmtree(self.tmp_path, ignore_errors=True)

    def _combine_sa(self, output_path, id_report_path, ac_scatter_plot_path,
                    gt_png_path):
        """
        Combine Identity report, Assay Caller scatter plot, and Genotyper PNG

        @param id_report_path:          pathname of identity report
        @param ac_scatter_plot_path:    pathname of assay caller scatter plot
        @param gt_png_path:             pathname of genotyper PNG
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=landscape(letter))
            story = list()

            story.append(self.get_image(gt_png_path, width=8*inch))
            story.append(PageBreak())

            story.append(self.get_image(ac_scatter_plot_path, width=8*inch))
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
            return True
        except:
            return False

    @staticmethod
    def _merge_pdfs(output_path, *args):
        """
        Merge multiple PDF files into one file
        """
        merger = PdfFileMerger()
        for path in args:
            merger.append(path)
        merger.write(output_path)

    @staticmethod
    def get_image(path, width=3*inch):
        """
        Resize a image and return an reportlab.platypus.Image object
        """
        img = utils.ImageReader(path)
        iw, ih = img.getSize()
        aspect = ih / float(iw)
        return Image(path, width=width, height=(width * aspect))
