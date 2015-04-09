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