import logging
from copy import deepcopy
from collections import defaultdict
from Bio import SeqIO
from Bio.Seq import reverse_complement
from redis import StrictRedis
from src.analyses.probe_validation.probe_containers import ProbeSet, AmpliconSet, Amplicon, get_tm_checker
from src.analyses.probe_validation import  settings

__author__ = 'spowers'


def probes_for_amplicon(wild_type, variants, probes):
    """
    Find all of the probes that are valuable for distinguishing wild types and variants.
    :param wild_type: A Sequence object containing the sequence for the wildtype.
    :param variants: A list of Sequence objects with all of the variant sequences of interest.
    :param probes: A list of valid probes.
    :return: (wt probes, [variant probes]) A tuple with the probes unique to the wildtype, as well as those unique to\
    each variant.
    """
    # First pass finds all probes that match each sequence.
    wt_probes = ProbeSet(wild_type, set([p for p in probes if wild_type.seq.count(p) > 0]),
                         set([p for p in probes if wild_type.seq.reverse_complement().count(p) > 0]))
    wt_unique_probes = deepcopy(wt_probes)
    variant_probes = list()
    for variant in variants:
        vp = ProbeSet(variant, set([p for p in probes if variant.seq.count(p) > 0]),
                      set([p for p in probes if variant.seq.reverse_complement().count(p) > 0]))
        wt_unique_probes.forward = wt_unique_probes.forward - vp.forward - vp.reverse
        wt_unique_probes.reverse = wt_unique_probes.reverse - vp.forward - vp.reverse
        vp.forward = (vp.forward - wt_probes.forward) - wt_probes.reverse
        vp.reverse = (vp.reverse - wt_probes.forward) - wt_probes.reverse
        variant_probes.append(vp)

    return AmpliconSet(wild_type.name, wt_unique_probes, variant_probes)


def get_sort_probes(probe_counts):
    """

    :param probe_counts: a dictionary of probes and the number of times they are found in the panel.
    :return: a sorting function.
    """

    def sort_probes(amp):
        """
        :param amp_sets: the group of probes for a Wildtype and variants in a ProbeSet named tuple.
        :param probe_counts: A dictionary containing the the global counts for probes.
        :return: a new version of probe_set that is sorted.
        """

        fn = _get_utility_fn(probe_counts, StrictRedis(settings.REDIS_CONFIG['REDIS_HOST'],
                                                       settings.REDIS_CONFIG['REDIS_PORT'],
                                                       settings.REDIS_CONFIG['REDIS_DB']))
        amp.wildtype.sort(fn)
        amp.wildtype.filter_probes()
        for v in amp.mutants:
            v.sort(fn)
            v.filter_probes()
        return amp

    return sort_probes


def aggregate_probe_sets(probe_sets):
    """
    :param probe_sets: An iterable of AmpliconSets to aggregate.
    :return:
    """
    all_probes = list()

    for probe_set in probe_sets:
        all_probes.extend(probe_set.aggregate())
    return all_probes


def global_probe_counts(sequences, probes):
    """ Get the global counts for all probes under consideration.  Count matches on both the sequence and its reverse
    complement.  This is then used as part of the overall ranking of probes.
    :param sequences: A list of Sequence objects to be considered in the panel.
    :param probes: A list of the probe sequences under consideration.
    :return: A dictionary containing the global counts of each probe.
    """
    results = defaultdict(int)
    for sequence in sequences:
        for probe in probes:
            results[probe] += sequence.count(probe)
            results[probe] += sequence.reverse_complement().count(probe)
    return results


def global_probe_counts_refgenome(amplicons, probes):
    """
    Determine where each probe matches within each provided amplicon. Populate
    a dictionary keyed by each probe name. Each value is a list of location 
    info dictionaries that contain the AmpliconID and genomic location where
    the probe matched the target sequence. Futhermore, a boolean flag indicating 
    absorption (probe matches >1 genomic location) is populated for each probe.
    
    :param amplicons: List of Biopython SeqRecord objects, one for each target amplicon
    :param probes: Dictionary of probe name to sequence key value pairs
    :return: Dictionary of probe name to array of location info key value pairs
    """
    results = defaultdict(dict)
    for amplicon in amplicons:
        for probe_name, seq in probes.iteritems():
            locations = amplicon.seq.relative_to_genomic(amplicon.seq.findall(seq))
            if locations:
                results[probe_name][amplicon.id] = locations
    absorption = dict()
    for probe_name, amplicons in results.iteritems():
        genomic_locations = set()
        for amplicon_id, locations in amplicons.iteritems():
            logging.info(amplicon_id)
            for location in locations:
                logging.info(location)
                genomic_locations.add(location)
        if len(genomic_locations) > 1:
            absorption[probe_name] = True
        else:
            absorption[probe_name] = False
            
    for probe_name, absorbed in absorption.iteritems():
        results[probe_name]["absorbed"] = absorbed
    return results


def global_counts_with_names(sequences, probes):
    results = defaultdict(list)
    for sequence in sequences:
        for probe in probes:
            if sequence.seq.upper().count(probe) or sequence.seq.upper().reverse_complement().count(probe):
                results[probe].append(sequence.name)
    return results


def _get_utility_fn(probe_counts, r, coefficients=(1, 0.05, 0.1, 0.1)):
    """ Generate a utility function to sort the probes.
    :param probe_counts: a dictionary of global probe counts for all probes of interest.
    :param r: a connection to redis
    :param coefficients: Coefficients used in the utility function
    :return: A utility function closure.
    """
    assert (len(coefficients) == 4)

    def utility_fn(probe):
        """lower score corresponds to better ranking.
        :param probe: A probe whose utility value you wish to obtain.
        :return: the probes utility score.
        """
        tm = get_tm_checker()
        _ = tm(probe)
        return coefficients[0] * (probe_counts[probe]) + coefficients[1] * (
            abs(settings.PROBES['target_tm'] - float(r.hget(probe, 'tm')))) + \
               coefficients[2] * (len(probe) - settings.PROBES['min_length']) + coefficients[3] * float(
            r.hget(probe, 'compPercent'))

    return utility_fn


def retrieve_probes():
    """
    :return: A list of probes from redis that are not found in either the quencher sequence or RB3 sequence.
    """
    r = StrictRedis(settings.REDIS_CONFIG['REDIS_HOST'], settings.REDIS_CONFIG['REDIS_PORT'],
                    settings.REDIS_CONFIG['REDIS_DB'])
    probes = r.keys('*')
    probes = filter(lambda s: (settings.QUENCHER.count(s) + settings.RB3.count(s) == 0), probes)
    probes = filter(
        lambda s: (settings.QUENCHER.reverse_complement().count(s) + settings.RB3.reverse_complement().count(s) == 0),
        probes)
    return probes


def chop_sequence(seq, min=settings.PROBES['min_length'], max=settings.PROBES['max_length']):
    """
    :param seq: A sequence to chop into probes
    :param min: The minimum length for a probes
    :param max: The maximum length for probes
    :return: A set containing all of the probes that will match the sequence.
    """
    locations = list()
    probes = list()
    l = len(seq)
    for x in xrange(0, l - min + 1):
        for y in xrange(min, max + 1):
            if x + y <= l:
                locations.append((x, x + y))

    pa = probes.append
    for location in locations:
        s = seq[location[0]: location[1]]
        rc = reverse_complement(s)
        if s not in settings.QUENCHER and s not in settings.RB3 and rc not in settings.QUENCHER and rc not in settings.RB3:
            pa(s)
            pa(rc)

    return list(set(probes))


def unique_sequences(sequences):
    """ == does not work on sequence objects, they need to be converted to strings and then compared according to the
    documentation.
    :param sequences: a list of sequence objects
    :return: a list of unique sequence objects
    """

    def count_seq(t):
        count = 0
        for s in sequences:
            if str(s) == str(t):
                count += 1
        return count

    unique = list()
    while sequences:
        s = sequences.pop()
        if not count_seq(s):
            unique.append(s)
    return unique


def pick_probes(probeset, num=4, max_distance=6, min_distance=1):
    """ Select a subset of the probes found for a mutation that have the end of the mutation between min_distance and
    max_distance from the 3' end.

    :param probeset: ProbeSet object to select forward and reverse probes for.
    :param num: The number of selections to make for both sets of primers
    :param max_distance: The maximum distance from the 3' end of the probe for the mutation to be covered.
    :param min_distance: The minimum distance from the 3' end of the probe for the mutation.
    :return: A ProbeSet object containing the selected probes.
    """
    def select(f, probes, max):
        selected = list()
        locations = list()
        for probe in probes:
            l = f(probe) + len(probe) - max

            if  max_distance >= l >= min_distance:
                #and ((l not in locations and not any(probe in s for s in selected) and not any(
                            #s in probe for s in selected)) or num == -1):
                selected.append(probe)
                locations.append(l)
            if len(selected) == num:
                break
        return selected

    f_max, r_max = probeset.max_start()
    f = probeset.sequence.seq.find
    forward = select(f, probeset.forward, f_max)
    f = probeset.sequence.seq.reverse_complement().find
    reverse = select(f, probeset.reverse, r_max)

    return ProbeSet(probeset.sequence, forward, reverse, f_max, r_max)


def get_targets(in_filename):
    """
    :param in_filename: name of a FASTA file to process.
    :return: a list of targets, and also a list of wildtype sequences.
    """
    targets = [s for s in SeqIO.parse(in_filename, 'fasta')]
    for target in targets:
        #convert from Seq to Amplicon
        target.__setattr__('seq', Amplicon(str(target.seq)))

    wild_types = [s for s in targets if '_WT' in s.name]  # wildtype is denoted by _WT at the end of the name.
    for wt in wild_types:
        #convert from Seq to Amplicon
        wt.__setattr__('seq', Amplicon(str(wt.seq)))
    return targets, wild_types