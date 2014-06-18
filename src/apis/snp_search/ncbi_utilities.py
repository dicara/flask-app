from collections import namedtuple
import re
from Bio import Entrez

Entrez.email = 'spowers@gnubio.com'
__author__ = 'spowers'


def chromosome_for_ref_assembly(name):
    match = re.search('gi\|(\d*)\|', name)
    refnum = match.group(1)
    try:
        handle = Entrez.efetch(db="nucleotide", id=refnum)
        result = handle.read()
    except:
        result = ''
    match = re.search('chromosome ([^\s|^,]+)', result)
    return match.group(1) if match else '-'


class SNPSummary(namedtuple("SNPSummary", "rs chr position ref alt")):
    def matches_range(self, chromosome, start, stop):
        return str(chromosome) == self.chr and start <= int(self.position) <= stop #

    def to_dict(self):
        return {'rs': self.rs, 'chromosome': self.chr, 'loc': self.position, 'ref': self.ref, 'alt': self.alt}


def snps_in_interval(chromosome, start, stop):
    query = "%s:%s[Base Position] AND %s[CHR] AND Homo sapiens[ORGN] AND by cluster [VALI]" % (start, stop, chromosome)
    handle = Entrez.esearch(db='snp', term=query)
    search_results = Entrez.read(handle)
    id_list = ','.join(search_results['IdList'])
    if id_list:
        handle = Entrez.esummary(db='snp', id=id_list)
        results = Entrez.read(handle)  # list of dicts
    else:
        results = list()
    SNPs = list()
    for snp in results:
        match = re.search('(.+):(\d*)', snp['CHRPOS'])
        chromosome = match.group(1)
        location = match.group(2)
        match = re.search('\[([^/]*)/([^\]]*)\]', snp['DOCSUM'])
        SNPs.append(SNPSummary('rs'+snp['SNP_ID'].__str__(), chromosome, location, match.group(1), match.group(2)))
    return SNPs