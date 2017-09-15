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
import sys
import os
import logging
import requests
import time
import yaml

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

#===============================================================================
# Global Variables
#===============================================================================
DEBUG = 0
TESTRUN = 0
PROFILE = 0

DEFAULT_URL = 'http://bioweb:8010/api/v1/'

#===============================================================================
# Main
#===============================================================================
def download_file(url, file_path):
    r = requests.get(url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    logging.basicConfig(stream=sys.stdout, format='%(asctime)s::%(levelname)s  %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name        = os.path.basename(sys.argv[0])
    program_version     = "v%s" % __version__
    program_description = "Script to pull results from BioWeb based on cartridge serial number."

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_description, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version)
        parser.add_argument('-u', '--url',  type=str, default=DEFAULT_URL, help='Location of BioWeb [default: %(default)s].')
        parser.add_argument('-p', '--path', type=str, default=os.getcwd(), help='Path to store downloaded files [default: %(default)s].')
        parser.add_argument('-a', '--assay_caller', action='store_true', help='Download assay caller result files [default: %(default)s].')
        parser.add_argument('cart_sn', help='Cartridge serial number')

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose

        if verbose > 0:
            print("Verbose mode on")

        r = requests.get(os.path.join(args.url, 'RunInfo/run_report?cart_serial=%s&format=json' % args.cart_sn))
        if r.status_code != 200:
            raise Exception("Error locating results for cartridge %s" % args.cart_sn)

        image_stacks = [i for i in r.json()['run_report'][0]['image_stacks'] if 'lr' in i]
        if len(image_stacks) < 1:
            raise Exception("No data collections found for %s" % args.cart_sn)

        r = requests.get(os.path.join(args.url, 'FullAnalysis/FullAnalysis?format=json'))
        if r.status_code != 200:
            raise Exception("Error retrieving full analsysis results.")

        id_results = {}
        ac_results = {}
        for result in r.json()['FullAnalysis']:
            archive = result['archive']
            if archive in image_stacks:
                if 'id_document' in result and 'report_url' in result['id_document']:
                    id_results[archive] = result['id_document']['report_url']
                if 'ac_document' in result and 'url' in result['ac_document']:
                    ac_results[archive] = result['ac_document']['url']

        id_sn_results = {}
        for archive, id_result in id_results.iteritems():
            r = requests.get(id_result)
            if r.status_code != 200:
                logging.error("Failure to retrieve identitiy result %s" % id_result)
            else:
                report = yaml.load(r.text)
                id_sn_results[archive] = report['MODEL_METRICS'][0]['INFO']['Signal to Noise']

        if args.assay_caller:
            for archive, ac_result in ac_results.iteritems():
                file_path = os.path.join(args.path, "%s_assay_caller.tsv" % archive)
                download_file(ac_result, file_path)

        for archive, id_sn in id_sn_results.iteritems():
            print "%s: %s" % (archive, id_sn)

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

    t = time.time()
    logging.info("Runtime: %s minutes", ((time.time()-t)/60.0))

def get_name_groupings(probe_names):
    """ Get a dictionary of wild-type : variant name(s) groupings
    @return dict of { wild type : [variants], ... }
    """
    group_mapping = {}
    groups = set([w.split('-')[0] for w in probe_names if '-' in w])
    grouped_names = set()

    for group in groups:
        wts = [w for w in probe_names if group in w and "_wt" in w]
        if len(wts) > 0:
            variants = [v for v in probe_names if group in v and "_var" in v]
            group_mapping[wts[0]] = variants
            grouped_names = grouped_names.union(wts)
            grouped_names = grouped_names.union(variants)

    ungrouped = sorted(set(probe_names) - grouped_names)
    if len(ungrouped) > 0:
        group_mapping[ungrouped[0]] = ungrouped[1:]

    return group_mapping

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    if DEBUG:
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
    probes = [
             'KRAS|2|R-c.34G>A',
             'NRAS|2|F-c.34G>A',
             'NRAS|3|F-c.181C>A',
             'BRAF|15|F-c.1798_1799GT>AA_var',
             'KRAS|2|R-c.34G>C',
             'NRAS|2|F-c.34G>T',
             'NRAS|3|F-c.182A>G',
             'BRAF|15|F-c.1799T>A',
             'KRAS|2|R-c.34G>T',
             'NRAS|2|F-c.35G>A',
             'NRAS|3|F-c.182A>T',
             'BRAF|15|F_wt',
             'KRAS|2|R-c.35G>A',
             'NRAS|2|F-c.37G>C',
             'WT(NRAS|3|F)',
             'KRAS|2|R-c.35G>C',
             'NRAS|2|F-c.38G>A',
             'KRAS|2|R-c.35G>T',
             'WT(NRAS|2|F)',
             'KRAS|2|R-c.38G>A',
             'WT(KRAS|2|R)',
             'Neg-1',
             'Neg-2',
             'Neg-3',
            ]

    groups = get_name_groupings(probes)
    for group, names in groups.iteritems():
        print "%d\t%s: %s" % (len(names) + 1, group, names)
#     sys.exit(main())