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
import os
import logging

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from src.analyses.probe_validation.probe_util import get_targets, global_probe_counts_refgenome

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
        parser.add_argument('--out', '-o', required=True, help='name of the results file')

        args = parser.parse_args()
        
        targets_file   = args.fasta
        probes_file    = args.probes
        out_file       = args.out
        
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
    
    execute_absorption(targets_file, probes_file, out_file)

def execute_absorption(targets_file, probes_file, out_file):
    results = compute_absorption(targets_file, probes_file)
    write_results(results, out_file)        

def compute_absorption(targets_file, probes_file):
    
    targets, wild_types = get_targets(targets_file)
    
    probes = get_probes(probes_file)

    logging.info("====================================================================")
    logging.info("TARGETS")
    logging.info("====================================================================")
    logging.info(targets)
    logging.info(len(targets))
    logging.info("====================================================================")
    logging.info("WILD TYPES")
    logging.info("====================================================================")
    logging.info(wild_types)
    logging.info("====================================================================")
    logging.info("PROBES")
    logging.info("====================================================================")
    logging.info(probes)
    logging.info(len(probes))
    
    #TODO: What about wild types?
     
    return global_probe_counts_refgenome(targets, probes)

def write_results(results, out_file):
    with open(out_file, 'w') as f:
        print >>f, "Probe\tAbsorbed\tLocations"
        for probe_name, info in results.iteritems():
            locations = ",".join(["%s: %s" % (amp,loc) for amp,loc in info.iteritems() if amp != "absorbed"])
            print >>f, "%s\t%s\t%s" % (probe_name, info["absorbed"], locations)
        
def get_probes(probes_file):
    """
    Extract probes from probes file, ensuring that the file format is valid.
    
    @param probes_file: FASTA formatted probes file
    @return: dictionary containing probe name & sequence key value pairs
    @raise exception: If probes file isn't formatted correctly
    """
    probes     = dict()
    probe_name = None
    with open(probes_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(">"):
                if probe_name:
                    raise Exception("Invalid probes file.")
                probe_name = line.strip().lstrip(">")
            elif probe_name:
                probes[probe_name] = line.strip()
                probe_name = None
            else:
                raise Exception("Invalid probes file.")
    return probes

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
#     sys.exit(main())
#     targets_fasta = "../../tests/analyses/probe_validation/amplicons.fasta"
#     probes_fasta  = "../../tests/analyses/probe_validation/probes.fasta"
    targets_fasta = "../../tests/analyses/probe_validation/amplicons_red.fasta"
    probes_fasta  = "../../tests/analyses/probe_validation/probes_red.fasta"
    
    from src.execution_engine.ExecutionManager import ExecutionManager
    em = ExecutionManager.Instance()
    from uuid import uuid4
    uuid = str(uuid4())
    em.add_job(uuid, compute_absorption, targets_fasta, probes_fasta)
    import time
    secs = 0
    while em.job_running(uuid):
        time.sleep(5)
        secs += 5
        print secs
    
#     results = compute_absorption(targets_fasta, probes_fasta)
    results = em.job_result(uuid)
    out_file = "results.txt"
    with open(out_file, 'w') as f:
        print >>f, "Probe\tAbsorbed\tLocations"
        for probe_name, info in results.iteritems():
            locations = ",".join(["%s: %s" % (amp,loc) for amp,loc in info.iteritems() if amp != "absorbed"])
            print >>f, "%s\t%s\t%s" % (probe_name, info["absorbed"], locations)
