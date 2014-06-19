from Bio.Seq import Seq

__author__ = 'spowers'

REDIS_CONFIG = {'REDIS_HOST': 'localhost', 'REDIS_PORT': 6379, 'REDIS_DB': 0}

PROBES = {'min_length': 6, 'max_length': 14, 'min_tm': 25.0, 'max_tm': 45.0, 'target_tm': 35.0, 'max_comp_percent': 1}

QUENCHER = Seq('AGATGCAGCAATAACATGTG')
RB3 = Seq("TAAATAAATTAATATATAGA")

ref_genome_loc = "/home/spowers/Documents/reference data/genome.fa"
blat_location = '/home/spowers/Public/blat/blat'