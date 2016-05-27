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