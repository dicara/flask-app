from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time
from uuid import uuid4

from bioweb_api import FA_PROCESS_COLLECTION, SA_GENOTYPER_COLLECTION, \
    SA_ASSAY_CALLER_COLLECTION, SA_IDENTITY_COLLECTION, PA_PROCESS_COLLECTION
from bioweb_api.apis.ApiConstants import FIDUCIAL_DYE, ASSAY_DYE, SUBMIT_DATESTAMP, \
    MAJOR, MINOR, USE_IID, DYES, DEVICE, ARCHIVE, UUID, JOB_NAME, \
    OFFSETS, NUM_PROBES, ID_TRAINING_FACTOR, DYE_LEVELS, IGNORED_DYES, FILTERED_DYES, \
    UI_THRESHOLD, AC_TRAINING_FACTOR, REQUIRED_DROPS, EXP_DEF, JOB_TYPE_NAME, JOB_TYPE, \
    STATUS, JOB_STATUS, START_DATESTAMP, SUCCEEDED, PA_PROCESS_UUID, CTRL_THRESH, \
    SA_IDENTITY_UUID, SA_ASSAY_CALLER_UUID, SA_GENOTYPER_UUID, URL, \
    CONFIG_URL, ERROR, PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT, GT_DOCUMENT, REPORT_URL, \
    PLOT_URL, KDE_PLOT_URL, SCATTER_PLOT_URL, PDF_URL, PNG_URL, PNG_SUM_URL, \
    FINISH_DATESTAMP, TRAINING_FACTOR, VARIANT_MASK, CONTINUOUS_PHASE, PLATE_PLOT_URL, \
    HDF5_DATASET_NAME
from bioweb_api.apis.full_analysis.FullAnalysisUtils import is_param_diff, generate_random_str, \
    add_unified_pdf

from bioweb_api.apis.primary_analysis.ProcessPostFunction import PaProcessCallable, PROCESS
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import SaIdentityCallable, IDENTITY
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import SaAssayCallerCallable, ASSAY_CALLER
from bioweb_api.apis.secondary_analysis.GenotyperPostFunction import SaGenotyperCallable, GENOTYPER
from bioweb_api.apis.primary_analysis.ProcessPostFunction import make_process_callback as pa_make_process_callback
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import make_process_callback as id_make_process_callback
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import make_process_callback as ac_make_process_callback
from bioweb_api.apis.secondary_analysis.GenotyperPostFunction import make_process_callback as gt_make_process_callback

DOCUMENT_LIST = [PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT, GT_DOCUMENT]

def populate_document(curr_job, prev_job, exist_docs=[]):
    """
    Add uuid and existing steps of previous job document to current document
    @param curr_job:            Dictionary of current job
    @param prev_job:            Dictionary of previous job
    @param exist_docs:          list of names of existing job documents, e.g., PA_DOCUMENT
    """
    if not exist_docs: return curr_job
    for doc_name in exist_docs:
        curr_job[doc_name] = prev_job[doc_name]
    return curr_job

class FullAnalysisWorkFlowCallable(object):
    def __init__(self, parameters, db_connector):
        """
        @param parameters:      Dictionary containing parameters for all arguments
                                for the full analysis job.
        @param db_connector:    A DbConnector object.
        """
        self.uuid = str(uuid4())
        self.parameters = parameters
        self.db_connector = db_connector
        self.query = {UUID: self.uuid}
        self.document = {
            UUID:               self.uuid,
            STATUS:             JOB_STATUS.submitted,
            JOB_NAME:           parameters[JOB_NAME],
            JOB_TYPE_NAME:      JOB_TYPE.full_analysis,
            SUBMIT_DATESTAMP:   datetime.today(),
            ARCHIVE:            parameters[ARCHIVE],
            HDF5_DATASET_NAME:  parameters[HDF5_DATASET_NAME],
            EXP_DEF:            parameters[EXP_DEF]
        }

        if parameters[JOB_NAME] in self.db_connector.distinct(FA_PROCESS_COLLECTION, JOB_NAME):
            raise Exception('Job name %s already exists in full analysis collection' % parameters[JOB_NAME])

        self.uuid_container = [None]
        self.workflow = [PROCESS, IDENTITY, ASSAY_CALLER, GENOTYPER]

        # if this job is a re-run, do a truncated workflow
        if UUID in parameters:
            prev_job = self.db_connector.find_one(FA_PROCESS_COLLECTION, UUID, parameters[UUID])
            i = 0
            while i < len(DOCUMENT_LIST):
                doc_name = DOCUMENT_LIST[i]
                if doc_name not in prev_job or STATUS not in prev_job[doc_name] \
                    or prev_job[doc_name][STATUS] != SUCCEEDED \
                    or is_param_diff(prev_job[doc_name], doc_name, parameters):
                    if i > 0:  # if passed primary analysis
                        last_succ_job = prev_job[DOCUMENT_LIST[i-1]] # last succeeded job
                        self.uuid_container.append(last_succ_job[UUID])

                    exist_docs = DOCUMENT_LIST[:i] if i > 0 else []
                    self.workflow = self.workflow[i:]
                    break
                i += 1
            if i == len(DOCUMENT_LIST):
                exist_docs = DOCUMENT_LIST
                self.workflow = []

            self.document = populate_document(self.document, prev_job, exist_docs)

        self.db_connector.insert(FA_PROCESS_COLLECTION, [self.document])

    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,
                           START_DATESTAMP: datetime.today()}}
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query, update)
        if self.workflow: self.run_analysis()

    def primary_analysis_job(self, _):
        """
        Create and run a primary analysis job.

        @param _:   Placeholder, isn't used it's here because all jobs run in this
                    callable must have a uuid from the previous job. A primary analysis
                    job is the only exception because it doesn't need a uuid to start.
        @return:    String, uuid of job, String, status of job
        """
        dyes = self.parameters[DYES] + [self.parameters[ASSAY_DYE], self.parameters[FIDUCIAL_DYE]]
        job_name = self.parameters[JOB_NAME] + generate_random_str(5)
        # create a callable and a callback
        callable = PaProcessCallable(archive=self.parameters[ARCHIVE],
                                    hdf5_dataset_name=self.parameters[HDF5_DATASET_NAME],
                                    dyes=dyes,
                                    device=self.parameters[DEVICE],
                                    major=self.parameters[MAJOR],
                                    minor=self.parameters[MINOR],
                                    offset=self.parameters[OFFSETS],
                                    use_iid=self.parameters[USE_IID],
                                    job_name=job_name,
                                    db_connector=self.db_connector)
        callback = pa_make_process_callback(uuid=callable.uuid,
                                            outfile_path=callable.outfile_path,
                                            config_path=callable.config_path,
                                            db_connector=self.db_connector)

        # enter primary analysis uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {PA_DOCUMENT: {START_DATESTAMP: datetime.today(),
                                                         PA_PROCESS_UUID: callable.uuid,
                                                         OFFSETS: self.parameters[OFFSETS]}}})

        # run primary analysis job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # update full analysis entry with results from primary analysis
        result = self.db_connector.find_one(PA_PROCESS_COLLECTION, UUID, callable.uuid)
        keys = [UUID, URL, CONFIG_URL, STATUS, ERROR, START_DATESTAMP, FINISH_DATESTAMP,
                MAJOR, MINOR, OFFSETS]
        document = {key: result[key] for key in keys if key in result}
        update = {"$set": {PA_DOCUMENT: document}}
        self.db_connector.update(FA_PROCESS_COLLECTION, {UUID: self.uuid}, update)

        # return primary analysis status and uuid
        return callable.uuid, result[STATUS], 'primary_analysis'

    def identity_job(self, primary_analysis_uuid):
        """
        Create and run a identity job.

        @param primary_analysis_uuid:   String indicating primary analysis uuid which
                                        will be used as an input for identity.
        @return:                        String, uuid of job, String, status of job
        """
        job_name = self.parameters[JOB_NAME] + generate_random_str(5)
        # create a callable and a callback
        callable = SaIdentityCallable(primary_analysis_uuid=primary_analysis_uuid,
                                    num_probes=self.parameters[NUM_PROBES],
                                    training_factor=self.parameters[ID_TRAINING_FACTOR],
                                    assay_dye=self.parameters[ASSAY_DYE],
                                    fiducial_dye=self.parameters[FIDUCIAL_DYE],
                                    dye_levels=self.parameters[DYE_LEVELS],
                                    ignored_dyes=self.parameters[IGNORED_DYES],
                                    filtered_dyes=self.parameters[FILTERED_DYES],
                                    ui_threshold=self.parameters[UI_THRESHOLD],
                                    db_connector=self.db_connector,
                                    job_name=job_name,
                                    use_pico_thresh=self.parameters[CONTINUOUS_PHASE])
        callback = id_make_process_callback(uuid=callable.uuid,
                                            outfile_path=callable.outfile_path,
                                            plot_path=callable.plot_path,
                                            report_path=callable.report_path,
                                            plate_plot_path=callable.plate_plot_path,
                                            db_connector=self.db_connector)

        # enter identity uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {ID_DOCUMENT: {START_DATESTAMP: datetime.today(),
                                                         SA_IDENTITY_UUID: callable.uuid,
                                                         TRAINING_FACTOR: self.parameters[ID_TRAINING_FACTOR],
                                                         UI_THRESHOLD: self.parameters[UI_THRESHOLD]}}})

        # run identity job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # update full analysis entry with results from identity
        result = self.db_connector.find_one(SA_IDENTITY_COLLECTION, UUID, callable.uuid)
        keys = [UUID, URL, REPORT_URL, PLOT_URL, STATUS, ERROR, START_DATESTAMP,
                FINISH_DATESTAMP, TRAINING_FACTOR, UI_THRESHOLD, PLATE_PLOT_URL]
        document = {key: result[key] for key in keys if key in result}
        update = {"$set": {ID_DOCUMENT: document}}
        self.db_connector.update(FA_PROCESS_COLLECTION, {UUID: self.uuid}, update)

        # return identity status and uuid
        return callable.uuid, result[STATUS], 'identity'

    def assay_caller_job(self, identity_uuid):
        """
        Create and run a assay caller job.

        @param identity_uuid:   String indicating identity uuid which
                                will be used as an input for assay caller.
        @return:                String, uuid of job, String, status of job
        """
        job_name = self.parameters[JOB_NAME] + generate_random_str(5)
        # create a callable and a callback
        callable = SaAssayCallerCallable(identity_uuid=identity_uuid,
                                        exp_def_name=self.parameters[EXP_DEF],
                                        num_probes=self.parameters[NUM_PROBES],
                                        training_factor=self.parameters[AC_TRAINING_FACTOR],
                                        assay_dye=self.parameters[ASSAY_DYE],
                                        fiducial_dye=self.parameters[FIDUCIAL_DYE],
                                        ctrl_thresh=self.parameters[CTRL_THRESH],
                                        db_connector=self.db_connector,
                                        job_name=job_name)
        callback = ac_make_process_callback(uuid=callable.uuid,
                                            outfile_path=callable.outfile_path,
                                            kde_plot_path=callable.kde_plot_path,
                                            scatter_plot_path=callable.scatter_plot_path,
                                            db_connector=self.db_connector)

        # enter assay caller uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {AC_DOCUMENT: {START_DATESTAMP: datetime.today(),
                                                         SA_ASSAY_CALLER_UUID: callable.uuid,
                                                         TRAINING_FACTOR: self.parameters[AC_TRAINING_FACTOR],
                                                         CTRL_THRESH: self.parameters[CTRL_THRESH]}}})

        # run assay caller job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # update full analysis entry with results from assay caller
        result = self.db_connector.find_one(SA_ASSAY_CALLER_COLLECTION, UUID, callable.uuid)
        keys = [UUID, URL, KDE_PLOT_URL, SCATTER_PLOT_URL, STATUS, ERROR, START_DATESTAMP,
                FINISH_DATESTAMP, TRAINING_FACTOR, CTRL_THRESH]
        document = {key: result[key] for key in keys if key in result}
        update = {"$set": {AC_DOCUMENT: document}}
        self.db_connector.update(FA_PROCESS_COLLECTION, {UUID: self.uuid}, update)

        # return assay caller status and uuid
        return callable.uuid, result[STATUS], 'assay_caller'

    def genotyper_job(self, assay_caller_uuid):
        """
        Create and run a genotyper job.

        @param assay_caller_uuid:   String indicating assay caller uuid which
                                    will be used as an input for genotyper.
        @return:                    String, uuid of job, String, status of job
        """
        job_name = self.parameters[JOB_NAME] + generate_random_str(5)
        mask_code = self.parameters[VARIANT_MASK] if VARIANT_MASK in self.parameters else None
        # create a callable and a callback
        callable = SaGenotyperCallable(assay_caller_uuid=assay_caller_uuid,
                                        exp_def_name=self.parameters[EXP_DEF],
                                        required_drops=self.parameters[REQUIRED_DROPS],
                                        db_connector=self.db_connector,
                                        job_name=job_name,
                                        mask_code=mask_code,
                                        combine_alleles=True)
        callback = gt_make_process_callback(uuid=callable.uuid,
                                            exp_def_name=self.parameters[EXP_DEF],
                                            ac_result_path=callable.ac_result_path,
                                            ignored_dyes=callable.ignored_dyes,
                                            outfile_path=callable.outfile_path,
                                            db_connector=self.db_connector)

        # enter genotyper uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {GT_DOCUMENT: {START_DATESTAMP: datetime.today(),
                                                         SA_GENOTYPER_UUID: callable.uuid,
                                                         REQUIRED_DROPS: self.parameters[REQUIRED_DROPS]}}})

        # run genotyper job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # update full analysis entry with results from genotyper
        result = self.db_connector.find_one(SA_GENOTYPER_COLLECTION, UUID, callable.uuid)
        keys = [UUID, URL, PDF_URL, PNG_URL, PNG_SUM_URL, STATUS, ERROR, START_DATESTAMP,
                FINISH_DATESTAMP, REQUIRED_DROPS]
        document = {key: result[key] for key in keys if key in result}
        update = {"$set": {GT_DOCUMENT: document}}
        self.db_connector.update(FA_PROCESS_COLLECTION, {UUID: self.uuid}, update)

        # return genotyper status and uuid
        return callable.uuid, result[STATUS], 'genotyper'

    def run_analysis(self):
        """
        Initialize a list of jobs that will be run in order
        """
        job_map = {PROCESS:         self.primary_analysis_job,
                   IDENTITY:        self.identity_job,
                   ASSAY_CALLER:    self.assay_caller_job,
                   GENOTYPER:       self.genotyper_job}
        # run jobs in the order specified by self.workflow
        while self.workflow:
            job = job_map[self.workflow.pop(0)]
            job_uuid, status, name = job(self.uuid_container[-1])
            if status != SUCCEEDED:
                raise Exception('failed at %s' % name)

            self.uuid_container.append(job_uuid)

        # add unified pdf
        fa_job = self.db_connector.find_one(FA_PROCESS_COLLECTION, UUID, self.uuid)
        while STATUS not in fa_job[GT_DOCUMENT] or fa_job[GT_DOCUMENT][STATUS] == JOB_STATUS.running:
            time.sleep(10)
            fa_job = self.db_connector.find_one(FA_PROCESS_COLLECTION, UUID, self.uuid)
        add_unified_pdf(fa_job)
