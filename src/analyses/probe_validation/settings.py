import os
from Bio.Seq import Seq
from src import REFS_PATH, USER_HOME_DIR

__author__ = 'spowers'

REDIS_CONFIG = {'REDIS_HOST': 'localhost', 'REDIS_PORT': 6379, 'REDIS_DB': 0}

PROBES = {'min_length': 6, 'max_length': 14, 'min_tm': 25.0, 'max_tm': 45.0, 'target_tm': 35.0, 'max_comp_percent': 1}

QUENCHER = Seq('AGATGCAGCAATAACATGTG')
RB3 = Seq("TAAATAAATTAATATATAGA")

ref_genome_loc = os.path.join(REFS_PATH, "genome.fa")
if not os.path.isfile(ref_genome_loc):
    raise Exception("Invalid reference genome: %s" % ref_genome_loc)

# Probably need to put this in a better place
blat_location = os.path.join(USER_HOME_DIR, "bin", "blat")
if not os.path.isfile(blat_location):
    raise Exception("Invalid blat location: %s" % blat_location)