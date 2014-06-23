import argparse
from multiprocessing.pool import Pool
from src.analyses.probe_validation.probe_util import get_targets, global_probe_counts_refgenome
import settings
from src.analyses.melting_temperature.idtClient import CachedIDTClient
__author__ = 'spowers'


def parse_cli_arguments():
    parser = argparse.ArgumentParser(add_help="Check the validity of a set of probes.")
    parser.add_argument('--fasta', '-f',  required=True, help='input fasta file containing all of the targets')
    parser.add_argument('--probes', '-p', required=True, help='input list of probes in plain text')
    parser.add_argument('--absorb', '-a', action="store_true", help="check for absorbed probes")
    parser.add_argument('--out', '-o', help='name of the results file')
    parser.add_argument('--num', '-n', default=3, type=int, help='minimum number of probes for a target')
    return parser.parse_args()


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

def main():
    pass

if __name__ == "__main__":
    args = parse_cli_arguments()
    targets, wild_types = get_targets(args.fasta)
    probes = list()

    with open(args.probes, 'r') as fd:
        probes.extend(fd.read().upper().strip('\n').split('\n'))

    if not args.absorb:
        loc = global_probe_counts_refgenome(targets, probes)
        print len(loc.keys())
        p = Pool()
        checker = get_checker([t.seq for t in targets], loc)

        results = map(checker, probes)

        with open(args.out, 'w') as fd:
            fd.write('\n'.join(results))
    else:
        for probe in probes:
            found_in = list()
            for target in targets:
                if target.seq.count(probe) or target.seq.reverse_complement().count(probe):
                    found_in.append(target.name)

            print "{0} found in: {1}".format(probe, ''.join(found_in))

