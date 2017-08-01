## Description
GnuBio Flask API.

## Release Notes
 * v0.1
   * Initial release.
 * v0.1.1
   * Forgot probe-design dependency in setup.py.
 * v0.1.2
   * Datetime objects are not json serializable. Therefore, I wrote a method to clean json responses of unserializable items. I also included a test for this method.
 * v0.1.3
   * Forgot to handle 'None' case in new method for serializing responses.
 * v0.1.4
   * Forgot a few instances where reponses needed to be cleaned for serialization.
 * v0.1.5
   * Added test for melting temperatures API.
   * Removed datetime conversion in ProbeExperimentGetFunction - this is now being done automatically by the abstract base class.
   * Fixed header license info in a few files.
 * v0.1.6
   * Removed unnecessary Makefiles.
 * v0.1.7
   * No changes. Bumping version to test out bamboo deployment plan.
 * v0.1.8
   * Status of running instances on other hosts now reported correctly.
 * v0.1.9
   * Incorporate probe-design v0.1.1.
 * v0.2
   * Incorporate probe-design v0.2 which replaces blat with Scott's new absorption method.
   * Fixed bug in Integer and Float parameters - must do a None check, because 0 and 0.0 are valid defaults. Similarly, AbstractParameter must do a None check.
 * v0.2.1
   * Incoporate gbalgorithms v0.3 which added statistics.py with functions that used to reside in genotype_analysis.
 * v0.2.2
   * Incorporate primary-analysis v0.6 which expands the range of offsets used from +/-30 to +/-70 when fitting the dye model.
 * v0.3
   * Fixed bug: remove archive directories with duplicate names (different caps)
   * Incorporate primary-analysis v0.7 which adds identity to its suite of tools.
 * v0.3.1
   * Enable Bioweb API to handle binary TDI images.
 * v0.4
   * Add version lower bounds to setup.py to try and resolve recent version conflicts in build.
 * v0.5
   * Incorporate primary-analysis v0.14 to update pandas and new Dockerfiles in build-automation to try and resolve build issues.
 * v0.6
   * Added offsets parameter to primary analysis process API.
   * Added plots POST, GET, and REMOVE APIs.
 * v0.7
   * Updating version simply to test build automation - no other code changes.
 * v0.7.1
   * Incorporate plotting bugfix in primary-analysis v1.2.1.
 * v0.8
   * Added binary image conversion API.
 * v0.9
   * Added identity APIs.
 * v1.0
   * Updated Identity API to use new secondary-analysis module where the identity functionality has been moved.
   * Alphabetized constants.
   * Added Assay Caller APIs.
 * v1.1
   * Application is no longer provided as a column in a file, but rather as a separate argument to the probe metadata api.
   * Added api to retrieve current applications.
   * Replaced fam/joe sd with signal.
 * v1.2
   * Added tests for identity and assay caller APIs
   * Added code coverage to unittests.
 * v1.3
   * Added image stack API.
   * Increased max file upload size to 2GB.
 * v1.4
   * Bugfix: url now contains archive name with the .tar.gz extension.
 * v1.5
   * Incorporate primary-analysis v2.5 (previous was v2.0)
     * Remove IID peak detection by default but add argument for turning back on
     * Add the default dye profiles configuration
     * Remove the *.peak and *.sum columns from the primary analysis output file
   * Incorporate secondary-analysis v0.7 (previous was v0.1)
     * Miscellaneous improvements to identity
     * Added fiducial pre-filtering
     * Added capability to ignore dyes
   * Add capability to define the dye profile major/minor versions
 * v1.5.1
   * The use_iid boolean should be recorded in the db for each primary analysis job.
   * The default identity training factor should be 1000 based on Nate's experience.
 * v1.6
   * The use of parameter enums were only implemented for string and date parameters. This code now lives in the abstract and should be implemented for all parameters.
 * v1.7
   * Added ability to upload monitor camera image stacks.
   * Added ability to compose replay image stacks from ham and monitor image stacks.
 * v1.8
   * Fixed bug that caused replay images stacks to be improperly created.
 * v1.9
   * Replay image stacks have proper structure.  Monitor camera folders within tar files were renamed.
 * v1.10
   * Tar checking errors are logged.  Bug fix for tar file cleanup.
 * v1.11
   * Added drop tools menu
   * Added drop size tolerance calculator
 * v1.12
   * Update primary and secondary analysis dependencies to their latest versions.
   * Update test due to version discrepancies.
 * v1.13
   * Incorporate secondary analysis (v0.13.1) identity bugfix: Fixed bug with barcode id for zero point clusters being set to None
 * v1.14
   * Added ability for user to get cluster and identity probabilities from bioweb
 * v1.15
   * Added ability for user to get a report from secondary analysis
 * v1.16
   * Logging stack traces when exceptions are caught in API post functions.
   * Fixed bug in archive finding where lstrip was being used incorrectly and could result in cryptic primary analysis failures
 * v1.17
   * Added library design generation tool to the Drop tools menu
 * v1.18
   * Added filtering dyes to secondary analysis
 * v1.19
   * No changes - need to bump version to deploy to new locally hosted Docker Hub.
 * v1.20
   * Identity errors are reported in the results table and text/report/png files are still generated
   * Primary analysis and secondary analysis versions updated
 * v1.21
   * Unit test fix for identity
 * v1.22
   * Unit test fix for assay caller
 * v1.23
   * Constellation identity factory is given picoinjection fiducial dye
 * v1.24
   * Bumped secondary-analysis requirement
 * v1.25
   * Library Generation utility refactored to include joe and fam profile when generating designs
 * v1.26
   * Dye profile database added.
 * v1.27
   * Bug fix.  Dye profile database will send error message if it is unable to retrieve profile, dye stock, or detection data.
 * v1.28
   * Updated secondary analysis version requirement
   * Dye profile database returns additional detection data
 * v1.29
   * Updated secondary-analysis to v0.43.
     * Removed deprecated assay caller arguments.
     * Updated default arguments for identity.
     * Updated tests to reflect these changes.
   * Simplified default settings.
 * v2.0
   * Added Genotyper APIs
 * v2.1
   * Add URLs to genotyper pdf and png results files.
 * v2.2
   * Update secondary analysis to v1.2.1 which contains some identity and assay caller plotting updates.
 * v2.3
   * Updated secondary analysis to 1.7
   * Updated primary analysis to 2.13
   * Library generator switched from constant distance between levels to scaled distance.
   * Updated intensity/concentration ratios to cope with new dye lots
 * v2.4
   * Removed merge resolution check from IdentityPostFunction
 * v2.5
   * Updated secondary-analysis to v1.10
      * Attempt to reduce memory footprint of assay caller.
       * Add individual probe counts to assay caller plots.
      * Added helper method to print probes in an experiment definition.
      * Genotype now handles controls when reading assay caller results from a file.
 * v2.6
   * Update secondary-analysis dependency to v1.12 which handles controls and fixes a bug where constellation identity was making dimension groups of one.
 * v2.7
   * Update secondary-analysis dependency to v1.13 wit bugfix for assay caller in offline analysis - handle negative controls failure.
 * v2.8
   * Full analysis api implemented.
 * v2.9
   * Update secondary analysis from v1.13 to v1.15 which includes:
     * v1.14
       * Fixed errors that occur when generating a identity report if very few clusters are identified
     * v1.15
       * Reduce GridSearchCV hyper-parameters to make assay caller more efficient.
       * Renamed commands submodule to sa_commands, since there is a native commands module that resulting in an import conflict.
       * Added retry capability to assay caller.
       * Added tool for testing offline analysis.
 * v3.0
   * Run info api implemented.
 * v3.1
   * Secondary analysis requirement updated
 * v3.2
   * Secondary analysis requirement updated
 * v3.3
   * Identity training factor set to default max training factor
 * v3.4
   * Full analysis rerun function updated
 * v3.5
   * Full analysis input defaults updated
 * v3.5.1
   * Fixed primary analysis offsets default
 * v3.5.2
   * Added experiment database requirement
 * v3.6
   * Added a module to FullAnalysisAPI for creating unified PDF reports
 * v3.6.1
   * Updated install require, removed output files generated from full analysis unittest
 * v3.6.2
   * Removed install require
 * v3.6.3
   * Updated install require
 * v3.6.4
   * Experiment-database requirement updated
 * v3.6.5
   * Added unittests for full analysis APIs
 * v3.6.6
   * Make unified pdf in full analysis post request
 * v3.7.0
   * Update secondary-analysis from version 1.19 to version 1.22 that contains:
     * v1.20
       * cluster approximate range is calculated using singular value decomposition
       * cluster identity confidence score calculated by considering nearest expectation components
     * v1.21
       * Fixed enum dependency bug and added new fields to VCF output
     * v1.22
       * Ensure a sufficient number of drops pass the negative controls threshold test before declaring the model valid and passing drops on to genotyper
 * v3.7.1
   * Fixed bug in adding full analysis select parameters
 * v3.7.2
   * Let RunInfo API handle empty yaml files
 * v3.8
   * Update secondary-analysis dependency from v1.22 to v1.27
     * v1.23
       * Throw an exception if assay caller fails model validation
     * v1.24
       * Added genome position range to VCF output
     * v1.25
       * Discard drops with confidence below threshold
     * v1.26
       * Added cDNA location to genotyper plot title
     * v1.27
       * Bugfix to include drops below confidence threshold in offline analysis results.
 * v3.8.1
   * Updated secondary-analysis dependency from v1.27 to v1.28
     * v1.28
      * Bugfix in handling new experiment definition files, new unittest added
 * v3.8.2
   * Bugfix in reading incomplete run reports
 * v3.8.3
   * Simplify full analysis job name
 * v3.9
   * Allow analysis of a portion of hotspot panel
   * Update secondary-analysis dependency from v1.28 to v1.37
     * v1.29
       * Treated cDNA and sequence location separately in assay caller plotting
     * v1.31
       * Density scan reachability distance calculation uses one standard deviation
     * v1.32
       * RemoveMin cluster filter value increased
       * RemoveBackground filter removed
     * v1.33
       * Added plate count plot
     * v1.34
       * added first filter for for variant calls
     * v1.35
       * Added mask to variant call in genotyper
     * v1.36
       * Bugfix in bitstring conversion
     * v1.37
       * Fixed bug where zero barcode dye clusters effect identity confidence score
       * Identity confidence score penalizes clusters claiming overclaimed expectation components
       * Cluster filter uses average deviations instead of variance
 * v3.9.1
   * Add experiment definition collection to store variant information
 * v3.10
   * Update secondary-analysis dependency from v1.37 to v1.43
     * v1.38
       * added first filter for for variant calls
       * util version bump
     * v1.39
       * Fixed bug where cluster plot was not saved
       * Added drop filter that removes drops that are on the concatenated region
       * RemoveBackground filter added
       * Cluster filters work on messages only, filter_decomp methods are removed
     * v1.40
       * Update experiment-database and gbutils version
     * v1.41
       * Merge resolution minimum size threshold will not go below min_size global constant
       * Cluster filter messages are more descriptive
       * Valid potential merged renamed to valid populous
     * v1.42
       * vcf position to conform with standard
     * v1.43
       * Fix genotyper unittest
 * v3.10.1
   * Avoid redundancy in reading run reports by adding invalid run reports to database
 * v3.11
   * Profile database constants are obtained from profile-db package
 * v3.11.1
   * Profile database requirement added to setup.py
 * v3.12
   * Library design generator can create predator csv files
 * v3.13
   * Update secondary-analysis to v1.47
     * v1.44
       * Removed random sampling of drops for training decomposition filters in identity
     * v1.45
       * VCF symbol for deletion and insertion
     * v1.46
       * Added picoinjection GMM filter
       * Picoinjection KDE filter improvements
       * Picoinjection filters use training size instead of training factor
       * Identity output plot randomly samples data
     * v1.47
       * identity assigns ids and confidence scores using standard euclidean distance
       * bug fix where resolved merged clusters were not given a cluster id
       * remove nonpico cluster filter removes clusters with greater than 4.0 standard euclidean distance
       * bug fix were dyes used to make cluster plate plots were not sorted in alphabetical order
       * average intensities of levels added to run report
       * bug fix in secondary analysis command line
       * id confidence added to output text file
 * v3.14
   * Let RunInfoAPI handle run_info.yaml generated from ClientUI
   * Update secondary-analysis to v1.51
     * v1.48
       * Restrict identity to using only a single subprocess
     * v1.49
       * Predator plate map plot refactored into separate module
       * Cluster size plot refactored into separate module
       * drops are assigned base on standardized euclidean
     * v1.50
       * Combine alleles in VCF
     * v1.51
       * Bug fix: Cluster is assigned based on standardized euclidean, drop reachability is determined using euclidean
   * Update experiment-database to v0.8.2
     * v0.7
       * Added validator for HotspotExperiment object
     * v0.7.1
       * Minor bugfix on genomic locations
       * Enable checking if variants refer to the same mutation
     * v0.8
       * Added uuid, reference name, chromosome, and genome locations to Variant object
       * Implemented functions for grouping variants based on mutation region and type
     * v0.8.1
       * Added strand to Variant object
     * v0.8.2
       * Minor change in get_variants
   * Update gbutils to v1.5
     * v1.4
       * write real filter information
     * v1.4.1
       * update test
     * v1.4.2
       * update test
     * v1.5
       * Update VCF writer
         * Limit digits of float numbers
         * Convert depth to integer
         * Remove PC and CO fields
 * v3.15
   * Update experiment-database to v0.8.5
   * Update secondary-analysis to v1.53
 * v3.16
   * Updated secondary-analysis from v1.53 to v1.54
     * v1.54
       * User can select type of picoinjection training filter
       * Removed picoinjection training factor
   * Updated profile-db from v0.3 to v0.4
     * v0.4
       * Dylight and Alexa dyes added as valid dyes
   * Identity jobs generate predator plate plots
   * Continuous phase picoinjection option available for identity
   * Removed picoinjection training factor from identity
 * v3.17
   * Updated secondary-analysis from v1.54 to v1.55
     * v1.55
       * Bugfix: avoid combining variant calls if no calls are found
 * v3.18
   * Let RunInfo API only display runs with image stack(s)
   * Remove full analysis job when deleting job on RunInfo page
   * Let RunInfo get function return cartridge information
 * v3.19
   * Update secondary-analysis from v1.55 to v1.56
     * v1.56
       * Change the format of genotyper plot
 * v3.19.1
   * Update secondary-analysis from v1.56 to v1.56.1
     * v1.56.1
       * Bugfix: handle empty cDNA list
 * v3.20
   * Primary analysis and full analysis accept HDF5 files as input
   * Library design generator saturation cap updated for cy7 and pe
   * HDF5 get function added to primary analysis api
   * Plate plot are shown on full analysis webpage
   * Library design generator can make a design from two separate detections
   * Removed unneeded database queries from secondary analysis callable constructor
 * v3.21
   * Switched from tornaodo to gunicorn
   * Full analysis default options are set in __call__ function
   * Full analysis resume workflow parameters are set in __call__ function
   * Bug fix where full analysis would not properly resume HDF5 analysis
   * Removed redundant database calls from ProcessPostFunction
 * v3.22
   * Bug fix where full analysis would not resume nested image stacks
 * v3.23
   * Update experiment-database from v0.8.5 to v0.10.1
     * v0.9
       * Convert DNA sequences to regular string (no Unicode string)
     * v0.10
       * Let HotspotExperiment return sorted list of variants
     * v0.10.1
       * Fixed get_variants unittest
       * Check order of variant list in unittest
   * Update secondary-analysis from v1.56.1 to v1.64.1
     * v1.57
       * Share more details about online analysis in real-time
         * Send positive/negative counts tied to probe uuid from genotyper
         * Publish negative controls in positive population from assay_caller
         * Publish throughput and % identified from identity
       * Additional configuration options to identity for more control
     * v1.58
       * Report variants with no probe count in VCF
     * v1.58.1
       * Bugfix in calling substitute_variant
     * v1.59
       * Update experiment-database to v0.9
       * Add unittest for assay caller plotting
       * Log VCF writing related information in genotyper
     * v1.59.1
       * Typo fix
     * v1.59.2
       * Move stand alone functions to genotyper_utils
       * Move VCF writing codes to _write_vcf function
     * v1.60
       * Update experiment-database form v0.9 to v0.10.1
       * Modified unittests for the new experiment-database
     * v1.61
       * Add flag to enable/disable drop logging from AbstractFilters
     * v1.62
       * Identity expecation matrix uses standard scaler
       * Identity sorts dimensions based on noise, not number of levels
       * Identity uses Kohonen fitting method
       * Removed unused eval_qual argument from Identity
       * Identity generates cluster size plot in execute_identity, not the identity model
       * Identity training size with least errors is selected
     * v1.63
       * handle missing probes in filter
     * v1.64
       * handle combined filters correctly
     * v1.64.1
       * Bug fix, identity expectation matrix checker cast float as integer
       * IDs displayed on expectation matrix plots
 * v3.24
   * Updated secondary-analysis from v1.64.1 to v1.66
     * v1.64.2
       * Bug fix, zero barcode expectation is not standard scaled
     * v1.65
       * Refactor Assay Caller
       * Add Naive Bayes Assay Caller
       * Use Naive Bayes Assay Caller as default
       * Minor bugfix for bad observations in genotyping
     * v1.65.1
       * Bug fix, Naive Bayes assay caller model wasn't packaged correctly
     * v1.66
       * Bug fix, offline genotyper KeyError when processing control barcodes
     * v1.66.1
       * Bug fix, issue with assay caller's negative controls list creation
     * v1.67
       * Add KDE plot to generated assay caller plots.
     * v1.67.1
       * Ensure get_title in assay caller plot generation returns something.
 * v3.25
   * Retrieve expdef from MongoDB
   * Avoid calling expdb when checking expdef param
   * Add ExpDef API to handle get and post requests
 * v3.26
   * Version update
 * v3.27
   * Update secondary-analysis from v1.67 to v1.69.2
     * v1.68
       * Uninjected ratio changed to 1.5
     * v1.69
       * Treat references as single-strand DNA
     * v1.69.1
       * Handle value problem
     * v1.69.2
       * Bug fix, geotyper analysis target_id not defined
 * v3.28
   * Update field names in yaml run reports
 * v3.29
   * ExecutionManager's ProcessPoolExecutor is shutdown when no jobs are running
   * Update secondary-analysis from v1.69.2 to v1.69.3
     * v1.69.3
       * Handle if assay dye intensity is zero.
 * v3.30
   * Fetch single run report using cartridge serial number
 * v3.31
   * Update secondary-analysis from v1.69.3 to v1.72
   * v1.69.4
     * Handle cDNA change of deletions and insertions
   * v1.70
     * Add picoinjection status reporting
   * v1.71
     * Fix unit tests hanging due to permissions on runs server
     * Fix picoinjection status reporting for offline
   * v1.72
     * offline identity uses csv generator instead of pandas dataframe
 * v3.32
   * Updated secondary-analysis from v1.72 to v1.75
     * v1.73
       * Decomposition filter exceptions report name of filter causing errors
       * Correct identity model training size reported in log
     * v1.74.1
       * Improved picoinjection decomp filter output message
       * Added unit test for uninjected ratio
     * v1.75
       * assay caller scatter plot re-integrated
       * add distance metrics to naive bayes scatter plot
   * Primary analysis post function saves HDF5 using numpy savetxt instead of pandas
 * v3.33
   * Update secondary-analysis from v1.75 to v1.76.1
     * v1.76
       * Split genotyper plots into multiple images and output as PDF
       * Store probe/barcode data in dictionary, remove generator
     * v1.76.1
       * Bugfix for failed assay plotting
       * Fixed assay scatter plot axes
   * Modify genotyper post function to expect pdf files instead of png
 * v3.34
   * Update secondary-analysis from v1.76.1 to v1.78
     * v1.77
       * Expose max uninjected ratio for the KDE picoinjection filter
     * v1.78
       * bug fix: identity model was logging wrong training size
       * bug fix: identity report was miscounting the number of drops marked as background noise
   * Let Identity and FullAnalysis take max uninjected ratio as parameter
   * Reduce updating run report runtime
 * v3.35
   * Store analysis output files in date folders
 * v3.35.1
   * Bugfix in getting the latest date of run reports
 * v3.36
   * Add HDF5 files to run reports
 * v3.37
   * Update secondary-analysis from v1.78 to v1.78.3
     * v1.78.1
       * Added assay caller positive/negative population publishing for live plots
     * v1.78.2
       * Handle missing barcode in assay caller plotting
     * v1.78.3
       * Dyes are sorted alphabetically in IdentityModelFitter
       * Picoinjection KDE filter does not randomly sample training data
 * v3.37.1
   * Simplify ExpDef API, merge post function into get function
 * v3.37.2
   * Bugfix in setting result urls
 * v3.37.3
   * Bugfix in setting url path of unified PDF
 * v3.37.4
   * Get date string from result file paths
 * v3.38
   * Updated profile-db from 0.5 to 0.6
     * v0.6
       * added ifluor dyes
       * added profile extract command
       * added conjugate field
       * secondary peak not considered when calculating noise
   * Updated predator from 0.1 to 0.2
     * v0.2
       * predator files track dye lot numbers
 * v3.39
   * Updated primary analysis from version v2.13 to v2.19
     * v2.14
       * Added exception for errors encountered in the identity job while finding a model
     * v2.15
       * Drops command saves compressed file with drop-y position
     * v2.16
       * Raise exception when fail to retrieve experiment definition
     * v2.17
       * Modified saturation data to be an int instead of a bool for more consistent logging
     * v2.18
       * Change DecompositionJob to use a multiprocessing event for pause/restart
     * v2.19
       * Update requirements for new docker image
   * Identity make temporal data plot
   * Updated secondary analysis from v1.78.3 to v1.83
     * v1.79
       * report generation feature added
     * v1.80
       * update requirements for new docker image
     * v1.81
       * Add HDF5 logging to assay caller
     * v1.82
       * Update assay scatter live plot stream data
     * v1.83
       * Identity has a single argument for plots.  This argument is the base path
         for all identity plots.  When set, identity will save all plots to this path.
       * Added dye levels plot to organic identity
       * Added temporal plot to organic identity
       * Identity job will send metrics on a zmq stream.  Metrics include; percent identified
         median model distance, upper and lower quartile distance
 * v3.39.1
   * Version bump so docker can build
 * v3.39.2
   * unit test fix to cope with new drop order in primary analysis
   * gbutils updated to v1.6
 * v3.40
   * Added option to toggle the negative control picoinjection 1 filter
   * Added option to toggle the ignore lowest intensity barcode
   * Updated secondary analysis from v1.83 to v1.87
 * v3.40.1
   * negative control threshold and ignore lowest barcode settings
     are stored in the full analysis document
 * v3.40.2
   * updated secondary analysis to v1.87.3
 * v3.40.3
   * Add more parameters to full analysis sub documents
 * v3.40.4
   * updated profile database to v0.7
   * added atto633 and ifluor610 dyes to library design generator
 * v3.41
   * updated secondary-analysis to version 1.90
 * v3.42
   * library design generator uses minimum summed peak to find ideal library design
 * v3.43
   * updated primary analysis to version 2.20
 * v3.44.0
   * Update experiment-database from 0.10.1 to 0.11.2
     * v0.11
       * Fix logging across modules
       * Make HotspotExperiment validator standalone
     * v0.11.1
       * Update requirements.txt for new docker image
     * v0.11.2
       * Add cDNA_change to Variant data model
   * Update secondary-analysis from 1.87.3 to 1.91.0
     * v1.87.4
       * reverting
     * v1.87.5
       * only log libdamage info
     * v1.88.0
       * Remove masked variants from list to prevent addition to VCF and calls.json
     * v1.89.0
       * automation tools
     * v1.90.0
       * Incoming drops use kdtree for nearest neighbor lookup * IdentifiedDrop stores clusterID, cluster status, and identity confidence.
     * v1.91.0
       * Create target id based either from cDNA change or coding position
       * Add cDNA change to variant call
 * v3.45.0
   * assay caller model argument exposed
   * hdf5 writing supports drop capture time
 * v3.46.0
   * User can filter picoinjeciton dye in identity
   * User can turn picoinjection filtering on and off in full analysis
   * Secondary-analysis updated to v1.92.0
    *  User can specify picoinjection1 dye
   * Experiment-database updated to v0.12
    * Add pico1_dye field to HotspotExperiment object
 * v3.47
   * picoinjection 1 dye is not considered a deviation from default and is not reported in diff params
 * v3.48
   * Update secondary from 1.92.0 to 1.97.2
     * v1.92.0
       * User can specify picoinjection1 dye
     * v1.92.1
       * Updated genotyper progress to be positives only if the flag is set
       * Remove dead code (serialize_calls) from genotype_analysis
     * v1.93.0
       * fixes INF-33 changing the way wt and variants are counted
     * v1.93.1
       * Bug fix where assay caller kde plot could not convert empty strings to floats
     * v1.94.0
       * Identity model metrics and identity throughput metrics are broadcast on
       * identity_status and identity_model_state streams
     * v1.95.0
       * Add positive control subplots to genotyper plotting
       * Bugfix in get target id
       * Update experiment-database from 0.11.2 to 0.13
     * v1.96.0
       * pico1 dye as barcode is turned off by default
       * pico1 dye filtered using threshold filter
     * v1.97.0
       * Identity model retrains when percent id throughput drops
     * v1.97.1
       * Plot positive control barcodes individually
     * v1.97.2
       * Bug fix in assign target id when strand of variation is undefined
 * v3.49
   * For run report refreshing, check HDF5 collection for run reports generated during the past three days
 * v3.49.1
   * Bugfix in updating image stacks of run report documents
 * v3.49.2
   * Change $set to $push operator for updating image stacks
 * v3.49.3
   * Read run reports generated during the past 3 days
 * v3.50.0
   * updated secondary-analysis from 1.97.3 to 1.100.3
     * 1.97.2
       * Bug fix in assign target id when strand of variation is undefined
     * 1.98.0
       * offline identity will continue to search for model after encountering IdentityModelException
       * identity model exception message shows both missing and identity collisions
       * offline identity unrecoverable exceptions in identity model fitting are not masked
     * 1.98.1
       * using numpy array for distance data calculation in offline identity
     * 1.99.0
       * offline identity model retrains when percent identity throughput drops below specified threshold
     * 1.99.1
       * bugfix mb-78  braf mutation probes
     * 1.100.0
       * offline identity writes output file in chunks instead of line by line
     * 1.100.1
        * more bugfix for mb-78 *
     * 1.100.2
        * Retrained assay caller model and added helper script for doing so
     * 1.100.3
       * bug fix, percent retrain log variable not properly renamed in IdentityJob
   * updated primary-analysis from 2.21 to 2.25
     * v2.21
       * In-house dye names changed to lowercase
     * v2.22
       * Decomposition messages contain capture time of drops
     * v2.23
       * Drop messages use sum of error instead of average squared error
     * v2.24
       * Add image recording support for decomp model training
     * v2.25
       * updated gbdrops from 0.9 to 0.12
       * sum method replaced with numpy.sum
 * v3.51.0
   * updated primary-analysis to v2.27
 * v3.52.0
   * Reduce the frequency of updating full analysis jobs with non-default input parameters
 * v3.53.0
   * Add date range parameters to GET run report API, allowing refresh/re-read reports in any date range
 * v3.54.0
   * updated secondary-analysis to version 2.0.0
   * updated primary-analysis to version 2.28
 * v3.55.0
   * Combine GET HDF5 API into GET run report API
 * v3.55.1
   * Solve out-of-sync issue between RunInfoGet and HDFsGet APIs
 * v3.55.2
   * Bugfix in displaying non-default values for full analysis parameters
 * v3.56.0
   * Updated secondary analysis to v2.1.0 which includes:
     * A run report analysis tool that parses run reports files and generates an HTML summary table
     * Improved assay caller plots
 * v3.57.0
   * Update gbutils to v2.0.0 which includes:
     * Wrap text in table cells of VCF PDF
   * Do not add non-default parameter information to database
 * v3.58.0
   * Update to new version of experiment definition fetcher
   * Update gbutils to v2.1.3 which includes:
     * Migrate experiment definition fetcher to gbutils
     * Update parameters for slug window video generation
   * Update secondary-analysis to v2.2.0 which includes:
     * Handle new types of experiment definitions using exp def fetcher in gbutils
 * v3.59.0
   * Add experiment purpose to run report model
   * Add pico1 dye as full analysis input parameter
   * Add list of dyes to experiment definition collection
 * v3.60.0
   * Treat experiment purpose in run report different from experiment definition type
   * Add experiment definition type to ExpDefGET response
   * Fix assay caller mode enum
   * Add pico1 dye to run report model
 * v3.61.0
   * Add pico1 dye parameter
 * v3.62.0
   * Update secondary_analysis to 2.4.2 which includes:
     * bugfix for training kde in offline mode
     * entry point bugfix
 * v3.63.0
   * Libarary design generator refactored
   * Predator script generator is in its own separate api
 * v3.64.0
   * Display select parameters while job is running
 * v3.64.1
   * Archive names can accept special characters
 * v3.64.2
   * predator scripts zip file location changed to results directory
 * v3.65.0
   * epoch time appended to hdf5 file
   * user can specify fixed number of levels for library design generator
   * library design error messages are more descriptive
 * v3.65.1
   * capture epoch time appended to primary analysis file
 * v3.66.0
   * use new experiment definition fetcher in gbutils
   * update gbutils to v2.4.2:
     * v2.2
       * Refactor experiment definition fetcher into a more feature complete tool
     * v2.2.1
       * Add def_updater entry point
     * v2.3
       * Harmonize dependencies, make experiment-database dependency abstract and update to 0.15.
     * v2.4
       * ring buffer can be multi-dimensional
     * v2.4.1
       * entry point bugfix
     * v2.4.2
       * bugfix where attempting to reverse numpy array created wrong size array
 * v3.66.1
   * use both old and new expdb sites for fetching definitions
 * v3.67.0
   * Update archive collection when refreshing run reports
 * v3.68.0
   * Update gbutils to v2.5.0:
     * switch to use exp-def-db site
   * Update secondary-analysis to v3.3.0:
     * v3.1.3
       * identity report includes standard scaled svd for each cluster
     * v3.2.0
       * Add enable/disable capabilities to decomposition filters
     * v3.3.0
       * let experiment definition fetcher point to exp-def-db site
       * use static exp def yaml files for unit tests
 * v3.69.0
   * Update primary and secondary analysis dependencies.
   * Make number of workers configurable.
 * v3.70.0
   * Update primary-analysis to v2.35
     * read_image must convert the image to 32 bit
 * v3.71.0
   * Allow uploading customized HDF5 files
 * v3.71.1
   * Display non-default experiment definition as select parameter
   * Restart entire workflow if a different experiment definition is selected
 * v3.71.2
   * Fix upload HDF5 bug
   * Fix removing outdated experiment definition bug
 * v3.72.0
   * new API for exploratory mode
 * v3.73.0
   * add update run reports cron job
 * v3.74.0
   * revert 3.73.0 changes
 * v3.75.0
   * Update experiment-database to 0.17.2:
     * v0.17.0
       * add barcode to target ID mapping function to experiment definition object
     * v0.17.1
       * add barcodes abstract property to experiment definition object
     * v0.17.2
       * bugfix in barcode_to_label_map
   * Update secondary-analysis to 3.11.1:
     * v3.8.0
       * Add sorting to run report results.
       * Clean up run report results HTML.
       * Fix analyze run reports argparse bug.
     * v3.9.0
       * IdentityJob defaults to organic identity factory if none is specified
     * v3.10.0
       * Move barcode to target ID function to expdb
     * v3.11.0
       * Added saturated drops filter
     * v3.11.1
       * Offline usage of saturated drop filter is backward compatible
 * v3.75.1
   * bugfix in generating exploratory mode PDF report
 * v3.75.2
   * set job name as plot title in exploratory mode
   * update secondary-analysis to 3.12.3:
     * v3.11.2
       * update version of sklearn and use new gmm methods
     * v3.12.0
       * clean up old imports
       * update experiment-database to 0.17.2
     * v3.12.1
       * disable broken test for quantum dots
     * v3.12.2
       * moved plotting
     * v3.12.3
       * missing constant import
   * update gb-algorithms to 0.12.7:
     * v0.12.2
       * PidController now friendly to dynamic integral gain
     * v0.12.3
       * Update requirements for new docker image
     * v0.12.4
       * PidController: Add optional filter pipeline for the derivative term.
     * v0.12.5
       * PidController: Save pre-filtered derivative values so they can be compared to filtered values.
     * v0.12.6
       * Added two new filters--holding spike filter and low pass filter--which are useful for cleaning noisy derivatives.
     * v0.12.7
       * valueerror returns NaN in distance measurement
 * v3.76.0
   * Pull in build-automation update that installs scikit-learn version to fix dependency issue.
 * v3.77.0
   * Improve uploading customized HDF5
 * v3.77.1
   * Disallow uploading datasets with duplicate names
 * v3.78.0
   * Scan baseline HDF5 file to database
   * Update gbutils to v2.5.1:
     * update VCF version number to 4.2
 * v3.79.0
   * identity dev mode argument is exposed
   * secondary analysis updated to version 3.18.3
 * v3.80.0
   * Add dyes scatter plot to assay caller API
 * v3.81.0
   * add new API to retrieve details of single run report
   * let GET full analysis job API take uuids parameter
   * let GET run report API map full analysis jobs
 * v3.81.1
   * bugfix in get run reports JSON
 * v3.82.0
   * update secondary-analysis to 3.20.2:
     * 3.20.0
       * added normalization capability to genotyper
     * 3.20.1
       * added scrubber model
     * 3.20.2
       * changed format of pickle to work with bioweb
     * 3.20.3
       * bugfix with normalizing
 * v3.82.1
   * update secondary-analysis to 3.20.4:
     * 3.20.4
       * bugfix to handle matplotlib overflow error when plotting large data
 * v3.83.0
   * Add notes field to run report model
 * v3.83.1
   * bugfix in generating PDF report failure
 * v3.84.0
   * update secondary-analysis to 3.20.6:
     * 3.20.5:
       * minor cleanup and parameters added
     * 3.20.6:
       * fixed plot axis and tick label issue
 * v3.85.0
   * Upload data from two locations
 * v3.86.0
   * update secondary-analysis to 3.22.0:
     * 3.21.0
       * assay caller command line bug fix where two arguments has the same name
       * Identity uses record array instead of DecomposedDrop/IdentifiedDrop classes
       * LowBarcode filter is faster
       * PrimaryAnalysisData is message generator is faster
     * 3.21.1
       * provide info on model locations and names
     * 3.22.0
       * Limit the number of data points in scatter plot to 1 million
 * v3.87.0
   * expose assay caller submodel parameter
 * v3.88.0
   * Identity can cope with data drift
   * updated secondary analysis to 3.23.0
     * Standard scaling of incoming data is used to cope with data drift
 * v3.88.1
   * Add default value for assay caller model
   * Add enum for assay caller model parameter
 * v3.88.2
   * Only add run reports with device name starting with pilot or beta
 * v3.89.0
   * Add use pico2 filter parameter
 * v3.90.0
   * update secondary-analysis to 3.24.3
     * 3.24.0
       * Identity matrix uses corner first fitting
       * Low fit score clusters included in offline identity report
       * Data drift compensation argument exposed in command line
       * Offline identity output file contains data drift column
     * 3.24.1
       * Assay caller scatter plot now displays low confidence drops in blue rather than calling them all positive.
     * 3.24.2
       * Fixed inconsistent types bug when computing bhattacharyya distance.
       * Added test to run naive bayes classifier.
     * 3.24.3
       * Add results comparison back into assay caller testing.
       * Don't include low confidence assay called drops in genotyping.
 * v3.90.1
   * update secondary-analysis to 3.24.4
     * 3.24.4
       * Bugfix where offline identity would not process chunks with no identified drops.
 * v3.91.0
   * update secondary-analysis to 3.25.1
     * 3.25.0
       * flip genotyping mask code
     * 3.25.1
       * concentration calculation added as util in experimental module
       * concentration calculation added for each barcode in exploratory mode
 * v3.92.0
   * Handle run reports of new format (new barcode)
 * v3.92.1
   * Change identity development mode and drift compensation defaults
   * Rename kit/syringe serial number to master lot
 * v3.93.0
   * Add run report directory to MongoDB collection, and retrieve from assay caller job
 * v3.94.0
   * Add system listener data to dye scatter plots
   * Remove base run report path from report directory in run report records
   * Remove unused imports
 * v3.94.1
   * Bugfix: Need to strip forward slash from relative run report path.
   * Bugfix: Need to provide parser with sys listener directory path
 * v3.94.2
   * Fix pymongo import WriteResult Error
   * Clean up old imports
 * 3.95.0
   * Add new API for adding tags to run reports
 * 3.96.0
   * Add API version to analysis MongoDB document
   * Add parsing run report error traceback to log
   * Bugfix in setting report directory
 * 3.97.0
   * Get run reports, image stacks and HDF5s from a list of disks
   * Rename run report sample_type and sample_name fields
 * 3.98.0
   * Limit the size of HDF5 file that can be processed
 * 3.99.0
   * Delete unfinished analysis jobs before server startup
   * Delete TSV outputs of old jobs
 * 3.99.1
   * Bugfix in deleting TSVs of old jobs
 * 3.99.2
   * Fixed missing logging
 * 3.99.3
   * Remove disk dir of archive and HDF5 paths when adding run reports