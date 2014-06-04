"""idtClient provides a client class to connect to the IDT SOAP service for doing primer analysis.
"""
from collections import namedtuple
from redis import StrictRedis
from suds.client import Client

import sys

__author__ = 'Scott Powers'
URL = "http://www.idtdna.com/AnalyzerService/AnalyzerService.asmx?wsdl"


class OligoTemp(namedtuple('oligoTemp', 'min max tm')):
    pass


class DimerResult(namedtuple('dimerResult', 'self_dimer deltaG compPercent')):
    pass


class IDTClient(object):
    def __init__(self, seq_type='DNA'):
        self.client = Client(URL)
        self.seq_type = seq_type

    def get_melting_temp(self, sequence, oligo=2, na=40, mg=2, dntp=0.2):
        """Get the melting temperature for sequence.
          \param oligo is the concentration of the oligo in uM
        """
        result = self.client.service.Analyze(sequence.upper(), self.seq_type, oligo, na, mg, dntp)
        #log this.... result
        if not result['Errors']:
            return OligoTemp(result['MinMeltTemp'], result['MaxMeltTemp'], result['MeltTemp'])
        else:
            return OligoTemp(-1, -1, -1)

    def self_dimer_check(self, sequence):
        """Check the oligo to see if there is a self dimer issue"""
        result = self.client.service.SelfDimer(sequence)
        return DimerResult(result['IsComplementPair'], result['MaxDeltaG'], result['ComplementarityPercent'])

    def hetero_dimer_check(self, sequence1, sequence2):
        raise NotImplemented


class CachedIDTClient(IDTClient):
    def __init__(self, REDIS_HOST='localhost', REDIS_PORT=6379, REDIS_DB=0):
        super(CachedIDTClient, self).__init__()
        self.r = StrictRedis(REDIS_HOST, REDIS_PORT, REDIS_DB)

    def get_info(self, sequence, oligo=2, na=40, mg=2, dntp=0.2):
        if not self.r.exists(sequence):
            tm = super(CachedIDTClient, self).get_melting_temp(sequence, oligo, na, mg, dntp)
            dimer = super(CachedIDTClient, self).self_dimer_check(sequence)
            info = {'tm': tm.tm, 'dimer': dimer.self_dimer, 'compPercent': dimer.compPercent}
            self.r.hmset(sequence, info)
        else:
            info = self.r.hgetall(sequence)
        return info
    
def main(argv=None):
    '''Command line options.'''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
        
    fasta_path = "full.fasta_reduced"
    fasta_path = "full.fasta"
    idt_client = IDTClient()
    
    with open(fasta_path) as f:
        
        for line in f:
            stripped_line = line.strip()
            if stripped_line:
                if stripped_line.startswith(">"):
                    name = line.strip()
                else:
                    sequence = line.strip()
                    print "%s: %s - %s" % (name, sequence, idt_client.get_melting_temp(sequence))
        
if __name__ == '__main__':
    sys.exit(main())


