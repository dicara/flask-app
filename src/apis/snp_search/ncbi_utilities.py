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


class SNPSummary(namedtuple("SNPSummary", "search_name rs chr position ref alt validated")):
    def matches_range(self, chromosome, start, stop):
        return str(chromosome) == self.chr and start <= int(self.position) <= stop #

    def to_dict(self):
        return {'search_name': self.search_name,
                'rs': self.rs,
                'chromosome': self.chr,
                'loc': self.position,
                'ref': self.ref,
                'alt': self.alt,
                'validated': self.validated}


def snps_in_interval(search_name, chromosome, start, stop):
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
        validated = snp['VALIDATED']
        SNPs.append(SNPSummary(search_name, 'rs'+snp['SNP_ID'].__str__(), chromosome, location, match.group(1), match.group(2), validated))
    return SNPs


def snps_in_interval_multiple(snp_search_names, chromosome_num, start_pos, stop_pos):
    SNPs = list()
    for search_name, chr_num, chr_start, chr_stop in zip(snp_search_names, chromosome_num, start_pos, stop_pos):
        SNPs.extend(snps_in_interval(search_name, chr_num, chr_start, chr_stop))
    # remove duplicates
    uniq_snps = [dict(item) for item in set(tuple(snp.to_dict().items()) for snp in SNPs)]
    uniq_snps.sort(key=lambda snp: int(snp['loc']))
    uniq_snps.sort(key=lambda snp: int(snp['chromosome']))
    uniq_snps.sort(key=lambda snp: snp['search_name'])
    return uniq_snps

