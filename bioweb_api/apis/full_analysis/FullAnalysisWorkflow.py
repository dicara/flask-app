from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from bioweb_api import FA_PROCESS_COLLECTION, SA_GENOTYPER_COLLECTION, \
    SA_ASSAY_CALLER_COLLECTION, SA_IDENTITY_COLLECTION, PA_PROCESS_COLLECTION
from bioweb_api.apis.ApiConstants import FIDUCIAL_DYE, ASSAY_DYE, SUBMIT_DATESTAMP, \
    MAJOR, MINOR, USE_IID, DYES, DEVICE, ARCHIVE, UUID, JOB_NAME, PF_TRAINING_FACTOR, \
    OFFSETS, NUM_PROBES, ID_TRAINING_FACTOR, DYE_LEVELS, IGNORED_DYES, FILTERED_DYES, \
    UI_THRESHOLD, AC_TRAINING_FACTOR, REQUIRED_DROPS, EXP_DEF, JOB_TYPE_NAME, JOB_TYPE, \
    STATUS, JOB_STATUS, START_DATESTAMP, SUCCEEDED, PA_PROCESS_UUID, CTRL_THRESH, \
    SA_IDENTITY_UUID, SA_ASSAY_CALLER_UUID, SA_GENOTYPER_UUID

from bioweb_api.apis.primary_analysis.ProcessPostFunction import PaProcessCallable
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import SaIdentityCallable
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import SaAssayCallerCallable
from bioweb_api.apis.secondary_analysis.GenotyperPostFunction import SaGenotyperCallable
from bioweb_api.apis.primary_analysis.ProcessPostFunction import make_process_callback as pa_make_process_callback
from bioweb_api.apis.secondary_analysis.IdentityPostFunction import make_process_callback as id_make_process_callback
from bioweb_api.apis.secondary_analysis.AssayCallerPostFunction import make_process_callback as ac_make_process_callback
from bioweb_api.apis.secondary_analysis.GenotyperPostFunction import make_process_callback as gt_make_process_callback



class FullAnalysisWorkFlowCallable(object):
    def __init__(self, uuid, parameters, db_connector):
        """
        @param uuid:            String, uuid of full analysis job.
        @param parameters:      Dictionary containing parameters for all arguments
                                for the full analysis job.
        @param db_connector:    A DbConnector object.
        """
        self.uuid = uuid
        self.parameters = parameters
        self.db_connector = db_connector
        self.query = {UUID: self.uuid}
        self.document = {
            UUID: self.uuid,
            STATUS: JOB_STATUS.submitted,
            JOB_NAME: parameters[JOB_NAME],
            JOB_TYPE_NAME: JOB_TYPE.full_analysis,
            SUBMIT_DATESTAMP: datetime.today()
        }

        if parameters[JOB_NAME] in self.db_connector.distinct(FA_PROCESS_COLLECTION, JOB_NAME):
            raise Exception('Job name %s already exists in full analysis collection' % parameters[JOB_NAME])

        self.db_connector.insert(FA_PROCESS_COLLECTION, [self.document])

    def __call__(self):
        update = {"$set": {STATUS: JOB_STATUS.running,
                           START_DATESTAMP: datetime.today()}}
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query, update)

        if UUID in self.parameters:
            self.resume_analysis()
        else:
            self.start_new_analysis()

    def primary_analysis_job(self, _):
        """
        Create and run a primary analysis job.

        @param _:   Placeholder, isn't used it's here because all jobs run in this
                    callable must have a uuid from the previous job. A primary analysis
                    job is the only exception because it doesn't need a uuid to start.
        @return:    String, uuid of job, String, status of job
        """
        dyes = self.parameters[DYES] + [self.parameters[ASSAY_DYE], self.parameters[FIDUCIAL_DYE]]
        # create a callable and a callback
        callable = PaProcessCallable(archive=self.parameters[ARCHIVE],
                                    dyes=dyes,
                                    device=self.parameters[DEVICE],
                                    major=self.parameters[MAJOR],
                                    minor=self.parameters[MINOR],
                                    offset=self.parameters[OFFSETS],
                                    use_iid=self.parameters[USE_IID],
                                    job_name=self.parameters[JOB_NAME],
                                    db_connector=self.db_connector)
        callback = pa_make_process_callback(uuid=callable.uuid,
                                            outfile_path=callable.outfile_path,
                                            config_path=callable.config_path,
                                            db_connector=self.db_connector)

        # enter primary analysis uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {PA_PROCESS_UUID: callable.uuid}})

        # run primary analysis job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # return primary analysis status and uuid
        status = self.db_connector.find_one(PA_PROCESS_COLLECTION, UUID, callable.uuid)[STATUS]
        return callable.uuid, status, 'primary_analysis'

    def identity_job(self, primary_analysis_uuid):
        """
        Create and run a identity job.

        @param primary_analysis_uuid:   String indicating primary analysis uuid which
                                        will be used as an input for identity.
        @return:                        String, uuid of job, String, status of job
        """
        # create a callable and a callback
        callable = SaIdentityCallable(primary_analysis_uuid=primary_analysis_uuid,
                                    num_probes=self.parameters[NUM_PROBES],
                                    training_factor=self.parameters[ID_TRAINING_FACTOR],
                                    assay_dye=self.parameters[ASSAY_DYE],
                                    fiducial_dye=self.parameters[FIDUCIAL_DYE],
                                    dye_levels=self.parameters[DYE_LEVELS],
                                    ignored_dyes=self.parameters[IGNORED_DYES],
                                    filtered_dyes=self.parameters[FILTERED_DYES],
                                    prefilter_tf=self.parameters[PF_TRAINING_FACTOR],
                                    ui_threshold=self.parameters[UI_THRESHOLD],
                                    db_connector=self.db_connector,
                                    job_name=self.parameters[JOB_NAME])
        callback = id_make_process_callback(uuid=callable.uuid,
                                            outfile_path=callable.outfile_path,
                                            plot_path=callable.plot_path,
                                            report_path=callable.report_path,
                                            db_connector=self.db_connector)

        # enter identity uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {SA_IDENTITY_UUID: callable.uuid}})

        # run identity job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # return identity status and uuid
        status = self.db_connector.find_one(SA_IDENTITY_COLLECTION, UUID, callable.uuid)[STATUS]
        return callable.uuid, status, 'identity'

    def assay_caller_job(self, identity_uuid):
        """
        Create and run a assay caller job.

        @param identity_uuid:   String indicating identity uuid which
                                will be used as an input for assay caller.
        @return:                String, uuid of job, String, status of job
        """
        # create a callable and a callback
        callable = SaAssayCallerCallable(identity_uuid=identity_uuid,
                                        exp_def_name=self.parameters[EXP_DEF],
                                        num_probes=self.parameters[NUM_PROBES],
                                        training_factor=self.parameters[AC_TRAINING_FACTOR],
                                        assay_dye=self.parameters[ASSAY_DYE],
                                        fiducial_dye=self.parameters[FIDUCIAL_DYE],
                                        ctrl_thresh=self.parameters[CTRL_THRESH],
                                        db_connector=self.db_connector,
                                        job_name=self.parameters[JOB_NAME])
        callback = ac_make_process_callback(uuid=callable.uuid,
                                            outfile_path=callable.outfile_path,
                                            kde_plot_path=callable.kde_plot_path,
                                            scatter_plot_path=callable.scatter_plot_path,
                                            db_connector=self.db_connector)

        # enter assay caller uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {SA_ASSAY_CALLER_UUID: callable.uuid}})

        # run assay caller job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # return assay caller status and uuid
        status = self.db_connector.find_one(SA_ASSAY_CALLER_COLLECTION, UUID, callable.uuid)[STATUS]
        return callable.uuid, status, 'assay_caller'

    def genotyper_job(self, assay_caller_uuid):
        """
        Create and run a genotyper job.

        @param assay_caller_uuid:   String indicating assay caller uuid which
                                    will be used as an input for genotyper.
        @return:                    String, uuid of job, String, status of job
        """
        # create a callable and a callback
        callable = SaGenotyperCallable(assay_caller_uuid=assay_caller_uuid,
                                        exp_def_name=self.parameters[EXP_DEF],
                                        required_drops=self.parameters[REQUIRED_DROPS],
                                        db_connector=self.db_connector,
                                        job_name=self.parameters[JOB_NAME])
        callback = gt_make_process_callback(uuid=callable.uuid,
                                            exp_def_name=self.parameters[EXP_DEF],
                                            ac_result_path=callable.ac_result_path,
                                            ignored_dyes=callable.ignored_dyes,
                                            outfile_path=callable.outfile_path,
                                            db_connector=self.db_connector)

        # enter genotyper uuid into full analysis database entry
        self.db_connector.update(FA_PROCESS_COLLECTION, self.query,
                                 {"$set": {SA_GENOTYPER_UUID: callable.uuid}})

        # run genotyper job
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callable)
            future.add_done_callback(callback)

        # return genotyper status and uuid
        status = self.db_connector.find_one(SA_GENOTYPER_COLLECTION, UUID, callable.uuid)[STATUS]
        return callable.uuid, status, 'genotyper'

    def start_new_analysis(self):
        """
        Initialize a list of jobs that will be run in order
        """
        uuid_container = [None]
        # run jobs in this order
        jobs = [self.primary_analysis_job,
                self.identity_job,
                self.assay_caller_job,
                self.genotyper_job]

        while jobs:
            job = jobs.pop(0)
            job_uuid, status, name = job(uuid_container[-1])
            if status != SUCCEEDED:
                raise Exception('failed at %s' % name)

            uuid_container.append(job_uuid)

    def resume_analysis(self):
        # will implement in next version
        pass