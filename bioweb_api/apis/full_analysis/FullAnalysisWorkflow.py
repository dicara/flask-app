from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time
import traceback
from uuid import uuid4

from bioweb_api.utilities.logging_utilities import APP_LOGGER
from bioweb_api import FA_PROCESS_COLLECTION, SA_GENOTYPER_COLLECTION, \
    SA_ASSAY_CALLER_COLLECTION, SA_IDENTITY_COLLECTION, PA_PROCESS_COLLECTION, \
    SA_EXPLORATORY_COLLECTION
from bioweb_api.apis.ApiConstants import PICO2_DYE, ASSAY_DYE, SUBMIT_DATESTAMP, \
    MAJOR, MINOR, USE_IID, DYES, DEVICE, ARCHIVE, UUID, JOB_NAME, \
    OFFSETS, NUM_PROBES, ID_TRAINING_FACTOR, DYE_LEVELS, IGNORED_DYES, FILTERED_DYES, \
    UI_THRESHOLD, AC_TRAINING_FACTOR, REQUIRED_DROPS, EXP_DEF, JOB_TYPE_NAME, JOB_TYPE, \
    STATUS, JOB_STATUS, START_DATESTAMP, SUCCEEDED, PA_PROCESS_UUID, CTRL_THRESH, \
    SA_IDENTITY_UUID, SA_ASSAY_CALLER_UUID, SA_GENOTYPER_UUID, URL, DEFAULT_DEV_MODE, \
    CONFIG_URL, ERROR, PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT, GT_DOCUMENT, REPORT_URL, \
    PLOT_URL, SCATTER_PLOT_URL, PDF_URL, PNG_URL, PNG_SUM_URL, DEV_MODE, \
    FINISH_DATESTAMP, TRAINING_FACTOR, VARIANT_MASK, CONTINUOUS_PHASE, PLATE_PLOT_URL, \
    IS_HDF5, KDE_PNG_URL, KDE_PNG_SUM_URL, MAX_UNINJECTED_RATIO, TEMPORAL_PLOT_URL, \
    IGNORE_LOWEST_BARCODE, CTRL_FILTER, AC_METHOD, PICO1_DYE, USE_PICO1_FILTER, \
    HOTSPOT, SEQUENCING, EXPLORATORY, EP_DOCUMENT, SQ_DOCUMENT, SA_EXPLORATORY_UUID, \
    AC_MODEL, DYES_SCATTER_PLOT_URL, DRIFT_COMPENSATE, DEFAULT_DRIFT_COMPENSATE
from bioweb_api.apis.full_analysis.FullAnalysisUtils import is_param_diff, generate_random_str, \
    add_unified_pdf
from bioweb_api.apis.primary_analysis.ProcessPostFunction import PaProcessCallable, PROCESS
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import SaIdentityCallable, IDENTITY
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import SaAssayCallerCallable, ASSAY_CALLER
from bioweb_api.apis.secondary_analysis.GenotyperPostFunction import SaGenotyperCallable, GENOTYPER
from bioweb_api.apis.secondary_analysis.ExploratoryPostFunction import SaExploratoryCallable
from bioweb_api.apis.primary_analysis.ProcessPostFunction import make_process_callback as pa_make_process_callback
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import make_process_callback as id_make_process_callback
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import make_process_callback as ac_make_process_callback
from bioweb_api.apis.secondary_analysis.GenotyperPostFunction import make_process_callback as gt_make_process_callback
from bioweb_api.apis.secondary_analysis.ExploratoryPostFunction import make_process_callback as ep_make_process_callback
from gbutils.exp_def.exp_def_handler import ExpDefHandler


# lookup dictionary for last step in workflow
WORKFLOW_LOOKUP = {HOTSPOT: GENOTYPER, EXPLORATORY: EXPLORATORY, SEQUENCING: SEQUENCING}
# lookup dictionary for last element in document list
DOCUMENT_LOOKUP = {HOTSPOT: GT_DOCUMENT, EXPLORATORY: EP_DOCUMENT, SEQUENCING: SQ_DOCUMENT}

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
            IS_HDF5:            parameters[IS_HDF5],
            EXP_DEF:            parameters[EXP_DEF]
        }

        self.uuid_container = [None]
        self.db_connector.insert(FA_PROCESS_COLLECTION, [self.document])

    def __call__(self):
        self.set_defaults()
        # check if a run needs to be resumed.
        if UUID in self.parameters:
            self.resume_workflow()

        update_query = {STATUS: JOB_STATUS.running,
                        START_DATESTAMP: datetime.today()}

        update = {"$set": update_query}
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query, update)
        if self.workflow:
            self.run_analysis()

    def set_defaults(self):
        """
        There are certain parameters that the user may not have sent
        but that can come from the experiment definition, set them here.

        Set workflow based on experiment type. The first 3 stages in each workflow are
        primary analysis, identity, and assay caller. The 4th stage depends on the
        type of experiment, i.e., genotyper API for hotspot experiment, exploratory API
        for exploratory experiment, and sequencing API for sequencing experiment.
        """
        try:
            exp_def_fetcher = ExpDefHandler()
            experiment = exp_def_fetcher.get_experiment_definition(self.parameters[EXP_DEF])

            self.exp_type = experiment.exp_type
            self.workflow = [PROCESS, IDENTITY, ASSAY_CALLER] + [WORKFLOW_LOOKUP[self.exp_type]]
            self.document_list = [PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT] + \
                                 [DOCUMENT_LOOKUP[self.exp_type]]

            if DYES not in self.parameters or \
               DYE_LEVELS not in self.parameters or \
               NUM_PROBES not in self.parameters or \
               PICO1_DYE not in self.parameters:
                # get dyes and number of levels
                dye_levels = defaultdict(int)
                for barcode in experiment.barcodes:
                    for dye_name, lvl in barcode.dye_levels.items():
                        dye_levels[dye_name] = max(dye_levels[dye_name], int(lvl+1))
                if DYES not in self.parameters:
                    self.parameters[DYES] = dye_levels.keys()
                if DYE_LEVELS not in self.parameters:
                    self.parameters[DYE_LEVELS] = dye_levels.items()
                if NUM_PROBES not in self.parameters:
                    self.parameters[NUM_PROBES] = len(experiment.barcodes)
                if PICO1_DYE not in self.parameters:
                    self.parameters[PICO1_DYE] = None
        except:
            APP_LOGGER.exception(traceback.format_exc())

        # set parameters for anything user might not have set
        if FILTERED_DYES not in self.parameters:
            self.parameters[FILTERED_DYES] = list()

        if IGNORED_DYES not in self.parameters:
            self.parameters[IGNORED_DYES] = list()

        if CONTINUOUS_PHASE not in self.parameters:
            self.parameters[CONTINUOUS_PHASE] = False

        if DEV_MODE not in self.parameters:
            self.parameters[DEV_MODE] = DEFAULT_DEV_MODE

        if DRIFT_COMPENSATE not in self.parameters:
            self.parameters[DRIFT_COMPENSATE] = DEFAULT_DRIFT_COMPENSATE

    def resume_workflow(self):
        """
        User may be trying to resume an old workflow were something failed.  Look
        for the subjob it failed on and resume from there. Update the document with
        the succeeded subjobs and resume the workflow from the failed subjobs.
        """
        # find the full analysis job
        previous_fa_job_document = self.db_connector.find_one(FA_PROCESS_COLLECTION, UUID, self.parameters[UUID])

        # if no previous job is found or experiment definition of previous job is
        # different from the current one, start from beginning
        if previous_fa_job_document is None or previous_fa_job_document[EXP_DEF] != self.parameters[EXP_DEF]:
            return

        # find the job it failed on
        failed_subjob = None
        last_successful_subjob_uuid = None
        for subjob_name in self.document_list:
            if subjob_name not in previous_fa_job_document or \
               previous_fa_job_document[subjob_name].get(STATUS, None) != SUCCEEDED or \
               is_param_diff(previous_fa_job_document[subjob_name], subjob_name, self.parameters):
                failed_subjob = subjob_name
                break
            else:
                last_successful_subjob_uuid = previous_fa_job_document[subjob_name][UUID]

        # append last successful uuid to uuid manager
        if last_successful_subjob_uuid is not None:
            self.uuid_container.append(last_successful_subjob_uuid)


        if failed_subjob is None:
            self.workflow = []
            succeeded_subjobs = self.document_list
        else:
            self.workflow = self.workflow[self.document_list.index(failed_subjob):]
            succeeded_subjobs = self.document_list[:self.document_list.index(failed_subjob)]

        update_query = dict()
        for subjob_name in succeeded_subjobs:
            update_query[subjob_name] = previous_fa_job_document[subjob_name]

        if update_query:
            update = {"$set": update_query}
            self.db_connector.update(FA_PROCESS_COLLECTION, self.query, update)

    def primary_analysis_job(self, _):
        """
        Create and run a primary analysis job.

        @param _:   Placeholder, isn't used it's here because all jobs run in this
                    callable must have a uuid from the previous job. A primary analysis
                    job is the only exception because it doesn't need a uuid to start.
        @return:    String, uuid of job, String, status of job
        """
        dyes = self.parameters[DYES] + [self.parameters[ASSAY_DYE], self.parameters[PICO2_DYE]]
        if self.parameters[PICO1_DYE] is not None and self.parameters[PICO1_DYE] not in dyes:
            dyes.append(self.parameters[PICO1_DYE])

        job_name = self.parameters[JOB_NAME] + generate_random_str(5)
        # create a callable and a callback
        callable = PaProcessCallable(archive=self.parameters[ARCHIVE],
                                    is_hdf5=self.parameters[IS_HDF5],
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
                                    use_pico1_filter = self.parameters[USE_PICO1_FILTER],
                                    pico1_dye=self.parameters[PICO1_DYE],
                                    pico2_dye=self.parameters[PICO2_DYE],
                                    dye_levels=self.parameters[DYE_LEVELS],
                                    ignored_dyes=self.parameters[IGNORED_DYES],
                                    filtered_dyes=self.parameters[FILTERED_DYES],
                                    ui_threshold=self.parameters[UI_THRESHOLD],
                                    max_uninj_ratio=self.parameters[MAX_UNINJECTED_RATIO],
                                    db_connector=self.db_connector,
                                    job_name=job_name,
                                    use_pico_thresh=self.parameters[CONTINUOUS_PHASE],
                                    ignore_lowest_barcode=self.parameters[IGNORE_LOWEST_BARCODE],
                                    dev_mode=self.parameters[DEV_MODE],
                                    drift_compensate=self.parameters[DRIFT_COMPENSATE])
        callback = id_make_process_callback(uuid=callable.uuid,
                                            outfile_path=callable.outfile_path,
                                            plot_path=callable.plot_path,
                                            report_path=callable.report_path,
                                            plate_plot_path=callable.plate_plot_path,
                                            temporal_plot_path=callable.temporal_plot_path,
                                            db_connector=self.db_connector)

        # enter identity uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {ID_DOCUMENT: {START_DATESTAMP: datetime.today(),
                                                         SA_IDENTITY_UUID: callable.uuid,
                                                         TRAINING_FACTOR: self.parameters[ID_TRAINING_FACTOR],
                                                         UI_THRESHOLD: self.parameters[UI_THRESHOLD],
                                                         IGNORE_LOWEST_BARCODE: self.parameters[IGNORE_LOWEST_BARCODE],
                                                         PICO1_DYE: self.parameters[PICO1_DYE],
                                                         MAX_UNINJECTED_RATIO: self.parameters[MAX_UNINJECTED_RATIO],
                                                         USE_PICO1_FILTER: self.parameters[USE_PICO1_FILTER],
                                                         DEV_MODE: self.parameters[DEV_MODE],
                                                         DRIFT_COMPENSATE: self.parameters[DRIFT_COMPENSATE]}}})

        # run identity job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # update full analysis entry with results from identity
        result = self.db_connector.find_one(SA_IDENTITY_COLLECTION, UUID, callable.uuid)
        keys = [UUID, URL, REPORT_URL, PLOT_URL, STATUS, ERROR, START_DATESTAMP,
                FINISH_DATESTAMP, TRAINING_FACTOR, UI_THRESHOLD, MAX_UNINJECTED_RATIO,
                PLATE_PLOT_URL, TEMPORAL_PLOT_URL, IGNORE_LOWEST_BARCODE, PICO1_DYE,
                USE_PICO1_FILTER, DEV_MODE, DRIFT_COMPENSATE]
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
        ac_model = None
        if AC_MODEL in self.parameters:
            ac_model = self.parameters[AC_MODEL]

        # create a callable and a callback
        callable = SaAssayCallerCallable(identity_uuid=identity_uuid,
                                         exp_def_name=self.parameters[EXP_DEF],
                                         training_factor=self.parameters[AC_TRAINING_FACTOR],
                                         ctrl_thresh=self.parameters[CTRL_THRESH],
                                         db_connector=self.db_connector,
                                         job_name=job_name,
                                         ctrl_filter=self.parameters[CTRL_FILTER],
                                         ac_method=self.parameters[AC_METHOD],
                                         ac_model=ac_model)
        callback = ac_make_process_callback(uuid=callable.uuid,
                                            outfile_path=callable.outfile_path,
                                            scatter_plot_path=callable.scatter_plot_path,
                                            dyes_scatter_plot_path=callable.dyes_plot_path,
                                            db_connector=self.db_connector)

        # enter assay caller uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {AC_DOCUMENT: {START_DATESTAMP: datetime.today(),
                                                         SA_ASSAY_CALLER_UUID: callable.uuid,
                                                         TRAINING_FACTOR: self.parameters[AC_TRAINING_FACTOR],
                                                         CTRL_THRESH: self.parameters[CTRL_THRESH],
                                                         CTRL_FILTER: self.parameters[CTRL_FILTER],
                                                         AC_METHOD: self.parameters[AC_METHOD],
                                                         AC_MODEL: ac_model}}})

        # run assay caller job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # update full analysis entry with results from assay caller
        result = self.db_connector.find_one(SA_ASSAY_CALLER_COLLECTION, UUID, callable.uuid)
        keys = [UUID, URL, SCATTER_PLOT_URL, STATUS, ERROR, START_DATESTAMP,
                FINISH_DATESTAMP, TRAINING_FACTOR, CTRL_THRESH, CTRL_FILTER,
                AC_METHOD, DYES_SCATTER_PLOT_URL, AC_MODEL]
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
                                            db_connector=self.db_connector,
                                            cur_job_name=job_name)

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
        keys = [UUID, URL, PDF_URL, PNG_URL, PNG_SUM_URL, KDE_PNG_URL,
            KDE_PNG_SUM_URL, STATUS, ERROR, START_DATESTAMP, FINISH_DATESTAMP,
            REQUIRED_DROPS, VARIANT_MASK]
        document = {key: result[key] for key in keys if key in result}
        update = {"$set": {GT_DOCUMENT: document}}
        self.db_connector.update(FA_PROCESS_COLLECTION, {UUID: self.uuid}, update)

        # return genotyper status and uuid
        return callable.uuid, result[STATUS], 'genotyper'

    def exploratory_job(self, assay_caller_uuid):
        """
        Create and run an exploratory job.

        @param assay_caller_uuid:   String indicating assay caller uuid which
                                    will be used as an input for genotyper.
        @return:                    String, uuid of job, String, status of job
        """
        job_name = self.parameters[JOB_NAME] + generate_random_str(5)
        # create a callable and a callback
        callable = SaExploratoryCallable(assay_caller_uuid=assay_caller_uuid,
                                         exp_def_name=self.parameters[EXP_DEF],
                                         required_drops=self.parameters[REQUIRED_DROPS],
                                         db_connector=self.db_connector,
                                         job_name=job_name)
        callback = ep_make_process_callback(uuid=callable.uuid,
                                            outfile_path=callable.tsv_path,
                                            db_connector=self.db_connector)

        # enter genotyper uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {EP_DOCUMENT: {START_DATESTAMP: datetime.today(),
                                                         SA_EXPLORATORY_UUID: callable.uuid,
                                                         REQUIRED_DROPS: self.parameters[REQUIRED_DROPS]}}})

        # run genotyper job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # update full analysis entry with results from genotyper
        result = self.db_connector.find_one(SA_EXPLORATORY_COLLECTION, UUID, callable.uuid)
        keys = [UUID, URL, PNG_URL, PNG_SUM_URL, KDE_PNG_URL, KDE_PNG_SUM_URL, STATUS,
            ERROR, START_DATESTAMP, FINISH_DATESTAMP]
        document = {key: result[key] for key in keys if key in result}
        update = {"$set": {EP_DOCUMENT: document}}
        self.db_connector.update(FA_PROCESS_COLLECTION, {UUID: self.uuid}, update)

        # return genotyper status and uuid
        return callable.uuid, result[STATUS], 'exploratory'

    def run_analysis(self):
        """
        Initialize a list of jobs that will be run in order
        """
        job_map = {PROCESS:         self.primary_analysis_job,
                   IDENTITY:        self.identity_job,
                   ASSAY_CALLER:    self.assay_caller_job,
                   GENOTYPER:       self.genotyper_job,
                   EXPLORATORY:     self.exploratory_job}
        # run jobs in the order specified by self.workflow
        while self.workflow:
            job = job_map[self.workflow.pop(0)]
            job_uuid, status, name = job(self.uuid_container[-1])
            if status != SUCCEEDED:
                raise Exception('failed at %s' % name)

            self.uuid_container.append(job_uuid)

        # add unified pdf
        fa_job = self.db_connector.find_one(FA_PROCESS_COLLECTION, UUID, self.uuid)
        last_doc = DOCUMENT_LOOKUP[self.exp_type]

        while STATUS not in fa_job[last_doc] or fa_job[last_doc][STATUS] == JOB_STATUS.running:
            time.sleep(10)
            fa_job = self.db_connector.find_one(FA_PROCESS_COLLECTION, UUID, self.uuid)
        add_unified_pdf(fa_job, [PA_DOCUMENT, ID_DOCUMENT, AC_DOCUMENT, last_doc])
