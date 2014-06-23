'''
Copyright 2014 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Scott Powers, Dan DiCara
@date:   Jun 23, 2014
'''

__author__ = 'spowers'

#=============================================================================
# Imports
#=============================================================================
import sys
import settings
import os
import logging

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from multiprocessing.pool import Pool

from src.analyses.probe_validation.probe_util import get_targets, global_probe_counts_refgenome
from src.analyses.melting_temperature.idtClient import CachedIDTClient

#===============================================================================
# Main
#=============================================================================
def main(argv=None):
    
    '''Command line options.'''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name        = os.path.basename(sys.argv[0])
    program_description = "Check the validity of a set of probes."

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_description, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('--fasta', '-f',  required=True, help='input fasta file containing all of the targets')
        parser.add_argument('--probes', '-p', required=True, help='input list of probes in plain text')
        parser.add_argument('--absorb', '-a', action="store_true", help="check for absorbed probes")
        parser.add_argument('--out', '-o', required=True, help='name of the results file')
        parser.add_argument('--num', '-n', default=3, type=int, help='minimum number of probes for a target')

        args = parser.parse_args()
        
        targets_file   = args.fasta
        probes_file    = args.probes
        absorb         = args.absorb
        out_file       = args.out
        min_num_probes = args.num
        
        logging_level = logging.WARNING
        logging.basicConfig(stream=sys.stderr, format='%(asctime)s::%(levelname)s  %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging_level)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
    
    validate(targets_file, probes_file, absorb, out_file, min_num_probes)
        
def validate(targets_file, probes_file, absorb, out_file, min_num_probes):
    targets, wild_types = get_targets(targets_file)
    probes = list()

    with open(probes_file, 'r') as fd:
        probes.extend(fd.read().upper().strip('\n').split('\n'))

    if not absorb:
        loc = global_probe_counts_refgenome(targets, probes)
        print len(loc.keys())
        p = Pool()
        checker = get_checker([t.seq for t in targets], loc)

        results = map(checker, probes)

        with open(out_file, 'w') as fd:
            fd.write('\n'.join(results))
    else:
        for probe in probes:
            found_in = list()
            for target in targets:
                if target.seq.count(probe) or target.seq.reverse_complement().count(probe):
                    found_in.append(target.name)

            print "{0} found in: {1}".format(probe, ''.join(found_in))

def get_checker(targets, locs):
    idtClient = CachedIDTClient()

    def check_validity(probe):
        probe = probe.upper()
        errors = list()
        locations = locs[probe]
        if not locations:
            errors.append("No Matches")
        if not settings.PROBES['min_length'] <= len(probe):
            errors.append("Too Short")
        elif not len(probe) <= settings.PROBES['max_length']:
            errors.append("Too Long")
        info = idtClient.get_info(probe)
        if float(info['tm']) < settings.PROBES['min_tm']:
            errors.append("Tm too low")
        elif float(info['tm']) > settings.PROBES['max_tm']:
            errors.append('Tm too high')
        if float(info['compPercent']) > settings.PROBES['max_comp_percent']:
            errors.append('Too much of the sequence forms a self dimer')
        if probe in settings.QUENCHER or probe in settings.QUENCHER.reverse_complement():
            errors.append("In Quencher")
        if probe in settings.RB3 or probe in settings.RB3.reverse_complement():
            errors.append("In RB3")

        return '{0}\t{1}\t{2}\t{3}'.format(probe, ', '.join(errors), locations, ', '.join(locs[probe]))

    return check_validity

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
#     sys.exit(main())
    targets_fasta = "../../tests/analyses/probe_validation/amplicons.fasta"
    probes_fasta  = "../../tests/analyses/probe_validation/probes.fasta"
    
    validate(targets_fasta, probes_fasta, False, "results", 3)