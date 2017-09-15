#!/usr/bin/env python
# encoding: utf-8

#===============================================================================
# License
#===============================================================================
'''
Copyright 2017 Bio-Rad Laboratories, Inc.

@author: Dan DiCara
@date:  2017-04-20
'''

#===============================================================================
# Version
#===============================================================================
__version__ = "0.0.1"

#===============================================================================
# Imports
#===============================================================================
import logging
import os
import pandas as pd
import requests
import sys
import time

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from primary_analysis.pa_utils import sniff_delimiter

#===============================================================================
# Global Variables
#===============================================================================
DEBUG = 0
TESTRUN = 0
PROFILE = 0

DEFAULT_URL = 'http://bioweb:8010/api/v1/'
FULL_ANALYSIS = 'FullAnalysis'
RUN_REPORT = 'run_report'

IDENTITY = 'identity'
IDENTITY_BINARY = 'identity_binary'
IDENTITY_AVG = 'identity_avg'
NON_IDENTITY_AVG = 'non_identity_avg'
IMG_EPOCH = 'img_epoch'
IMG_DATETIME = 'img_datetime'
IMGFILE = 'imgfile'

log = logging.getLogger(__name__)

#===============================================================================
# Main
#===============================================================================
def download_file(url, file_path):
    chunk_size = 1024*1024 # 1 MB
    r = requests.get(url, stream=True)
    total_length = r.headers.get('content-length')
    total_length = 0 if total_length is None else int(total_length)
    total_length_mb = total_length/chunk_size

    if total_length > 0: # no content length Header
        log.info("Downloading %d MB" % (total_length/chunk_size))

    with open(file_path, 'wb') as f:
        dl = 0
        t = time.time()
        for chunk in r.iter_content(chunk_size=chunk_size): 
            dl += chunk_size
            debug = "Downloaded %d MB" % (dl/chunk_size)
            if dl < total_length:
                debug += " out of %d MB, %d%% done" % (total_length_mb, 
                    int(100.0*dl/total_length))
            debug += " (%.1f MB/s)" % (1.0/(time.time()-t))
            t = time.time()
            log.debug(debug)
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    log.info("Download finished")

def parse_analysis(analysis_path):
    """
    Read primary analysis result file into a pandas Dataframe.

    @param analysis_path: Path to analysis.txt file.
    """
    if not os.path.isfile(analysis_path):
        raise Exception("Analysis file doesn't exist: %s", analysis_path)
    delimiter  = sniff_delimiter(analysis_path)
    return pd.read_table(analysis_path, sep=delimiter)

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    t = time.time()
    logging.basicConfig(stream=sys.stdout, 
        format='%(asctime)s::%(levelname)s  %(message)s', 
        datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name        = os.path.basename(sys.argv[0])
    program_version     = "v%s" % __version__
    program_description = '''
    Script to pull identity results from BioWeb based on a file containing 
    cartridge serial numbers and data set names. After pulling results, 
    percentage of identified and un-identified drops is computed as a function 
    of time for each data set and output to a file.
    '''

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_description, 
            formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", 
            help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', 
            version=program_version)
        parser.add_argument('-u', '--url',  type=str, default=DEFAULT_URL, 
            help='Location of BioWeb [default: %(default)s].')
        parser.add_argument('-p', '--path', type=str, default=os.getcwd(), 
            help='Path to store downloaded files [default: %(default)s].')
        parser.add_argument('-w', '--overwrite', action='store_true', 
            help='Overwrite existing files [default: %(default)s].')
        parser.add_argument('input_path', 
            help='Path to file containing cartridge S/N and dataset names')

        # Process arguments
        args = parser.parse_args()

        log.setLevel(logging.DEBUG if args.verbose else logging.WARNING)

        if not os.path.exists(args.input_path):
            log.error("Invalid input path: %s" % args.input_path)

        sep = sniff_delimiter(args.input_path)
        log.debug("Reading input file...")
        collections = {}
        with open(args.input_path, 'r') as f:
            for line in f:
                fields = line.rstrip().split(sep)
                if len(fields) == 2:
                    collections[fields[1]] = fields[0]

        full_analysis_json = None
        result_paths = {}
        for data_set_name, cart_sn in collections.iteritems():
            log.info("Downloading %s..." % ': '.join([cart_sn, data_set_name]))
            r = requests.get(os.path.join(args.url, 'RunInfo/run_report?cart_serial=%s&format=json' % cart_sn))
            if r.status_code != 200:
                log.error("Error locating results for %s - skipping" % cart_sn)
                continue

            r_json = r.json()
            if RUN_REPORT not in r_json or len(r_json[RUN_REPORT]) < 1:
                log.error("No results found for cartridge S/N: %s" % cart_sn)
                continue

            if data_set_name not in r.json()[RUN_REPORT][0]['image_stacks']:
                log.error("Error locating data set %s - skipping" % data_set_name)
                continue

            if full_analysis_json is None:
                far = requests.get(os.path.join(args.url, 'FullAnalysis/FullAnalysis?format=json'))
                if far.status_code != 200:
                    raise Exception("Error retrieving full analysis results.")

                full_analysis_json = far.json()
                if FULL_ANALYSIS not in full_analysis_json or len(full_analysis_json[FULL_ANALYSIS]) < 1:
                    raise Exception("No full analysis results available.")
                full_analysis_json = full_analysis_json[FULL_ANALYSIS]
# 
            id_results = {}
            for result in full_analysis_json:
                archive = result['archive']
                if archive == data_set_name:
                    if 'id_document' in result and 'report_url' in result['id_document']:
                        id_results[archive] = result['id_document']['url']
# 
            for archive, id_result in id_results.iteritems():
                file_path = os.path.join(args.path, "%s_identity.tsv" % archive)
                if os.path.exists(file_path) and not args.overwrite:
                    log.info("Skipping existing identity file: %s" % file_path)
                    result_paths[archive] = file_path
                    continue
                log.info("Retrieving identity result: %s" % id_result)
                r = requests.get(id_result)
                if r.status_code != 200:
                    log.error("Failed to retrieve identity result %s" % id_result)
                else:
                    try:
                        log.info("Downloading %s..." % id_results)
                        download_file(id_result, file_path)
                        result_paths[archive] = file_path
                    except:
                        log.error("Failed to download identity results %s" % id_result)

        for archive, res_path in result_paths.iteritems():
            log.info("Processing %s..." % archive)
            out_path = os.path.splitext(res_path)[0] + '_temporal.csv'
            out_path = os.path.join(args.path, out_path)

            if os.path.exists(out_path) and not args.overwrite:
                log.info("Skipping existing identity temporal file: %s" % \
                    out_path)
                continue

            try:
                analysis_df = parse_analysis(res_path)
            except:
                log.error("Failed to parse %s - skipping" % res_path)
                continue
 
            if IMG_EPOCH not in analysis_df:
                if IMGFILE not in analysis_df:
                    log.error("Neither image epoch nor filename in analysis file: %s" % res_path)
                    continue
                log.info("Image epoch not in DataFrame - generating...")
                # Expected IMGFILE entries are of the form 1493737043388.bin and will be
                # converted to the form 1493737043.388
                analysis_df[IMG_EPOCH] = analysis_df[IMGFILE].apply(lambda x: float('.'.join([x[:-7], x[10:13]])))
            img_datetime = pd.DatetimeIndex(pd.to_datetime(analysis_df[IMG_EPOCH], unit='s'))

            analysis_df[IMG_DATETIME] = img_datetime

            if IDENTITY not in analysis_df:
                log.error("Identity column missing from file: %s" % res_path)

            analysis_df[IDENTITY_BINARY] = analysis_df[IDENTITY].apply(lambda x: 0 if pd.isnull(x) else 1)
            window = 5000
            analysis_df[IDENTITY_AVG] = analysis_df[IDENTITY_BINARY].rolling(window=window, center=False).mean()*100.0
            analysis_df[NON_IDENTITY_AVG] = 100.0 - analysis_df[IDENTITY_AVG]
            analysis_df = analysis_df[window:]

            columns_to_save = [IMG_DATETIME, IDENTITY_AVG, NON_IDENTITY_AVG]
            analysis_df[columns_to_save].to_csv(out_path, sep='\t', index=False)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    logging.info("Runtime: %s minutes", ((time.time()-t)/60.0))

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    if DEBUG:
#         sys.argv.append('input_data.csv')
#         sys.argv.append('-u', )
#         sys.argv.append('http://bioweb:8010/api/v1/')
        sys.argv.append("-h")
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'api_caller_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)

    sys.exit(main())