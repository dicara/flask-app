import itertools

import numpy


# the minimum and maximum number of dyes
MIN_NDYES  = 1
MAX_NDYES  = 5

# the minimum number of levels per barcode dye, must be at least two
MIN_NLEVELS = 2

# intensity ranges for each level
INTENSITY_RANGES = {2: (3000, 20000), 3: (3000, 30000), 4: (2000, 40000)}

# based on plastic chip data, 60 mW laser power, Gain 0
BARCODE_DYES = {
    'pe-cy7': {'max_nlvls': 3, 'intensity_ugml': 1000.0},
    'cy5.5':  {'max_nlvls': 4, 'intensity_ugml': 3066.7},
    '633':    {'max_nlvls': 3, 'intensity_ugml': 2000.0},
    '594':    {'max_nlvls': 4, 'intensity_ugml': 4166.7},
    'pe':     {'max_nlvls': 2, 'intensity_ugml': 7133.3},
}

# Define a preferred order from the dyes that you would prefer to have the
# least levels and those that you would prefer to have the most levels.
# In this case 594 is at the end indicating that it is preferred to have
# the most levels (if needed).
PREFERED_ORDER = ['pe', 'pe-cy7', '633', 'cy5.5', '594']


def get_dyes():
    return BARCODE_DYES.keys()


def validate_dyes(dyes):
    """
    Validate that the dyes the user is requesting

    @param dyes:    A list of strings specifying dye names
    """
    if not dyes:
        raise Exception('No dyes were entered.')

    if len(set(dyes)) != len(dyes):
        raise Exception('Duplicate dye entries found.')

    if not (MIN_NDYES <= len(dyes) <= MAX_NDYES):
        raise Exception('The number of dyes must be between %d and %d.' %
                        (MIN_NDYES, MAX_NDYES))

    for dye in dyes:
        if dye not in BARCODE_DYES:
            raise Exception('%s is not a valid dye.' % str(dye))


def get_levels(nbarcodes, dyes):
    """
    Get the number of levels for each dye based on the number of
    barcodes and dyes that the user requested.  This function used a
    brute force search of all possible combinations of levels.

    @param nbarcodes:   Integer specifying number of barcodes
    @param dyes:        A list of strings specifying dye names
    @return:            A list of integers specifying the number of
                        levels of each dye, order corresponds to
                        the order of the dyes entered by the user.
    """
    validate_dyes(dyes)

    # change the order based on preferred order
    sorted_dyes = [dye for dye in PREFERED_ORDER if dye in dyes]

    available_levels = [range(MIN_NLEVELS, BARCODE_DYES[dye]['max_nlvls'] + 1) for dye in sorted_dyes]

    combinations = numpy.array(list(itertools.product(*available_levels)))

    avail_nbarcodes = numpy.product(combinations, axis=1)
    diffs = avail_nbarcodes - nbarcodes

    valid_idxs = numpy.where(diffs == 0)[0]
    if valid_idxs.size <= 0:
        raise Exception('Library cannot be made using specified inputs')
    design_idx = numpy.amin(valid_idxs)

    best_design = combinations[design_idx]
    input_order = [sorted_dyes.index(dye) for dye in dyes]

    return best_design[input_order]


def get_design(nbarcodes, dyes):
    """
    Create a design based on the dyes and requested number of barcodes

    @param nbarcodes:   Integer specifying number of barcodes
    @param dyes:        A list of strings specifying dye names
    @return:            A tuple containing the design (a list of dictionaries
                        containing information on each dye in the design), and
                        the input dyes and levels for each dye.
    """
    dyes.sort()
    levels = get_levels(nbarcodes, dyes)

    design = list()
    for dye, nlvls in zip(dyes, levels):
        min, max = INTENSITY_RANGES[nlvls]
        int_range = numpy.linspace(min, max, nlvls)
        ug_ml = int_range / BARCODE_DYES[dye]['intensity_ugml']
        design.append({'name': dye, 'levels': ', '.join([str(round(lvl, 2)) for lvl in ug_ml])})

    return design, dyes, map(int, levels)


def get_csv_str(dyes, levels):
    """
    Generate the contents of a csv file.

    @param dyes:    A list of strings specifying dye names.
    @param levels:  A array of integers representing the number of levels
                    of each dye.
    @return:        A csv string.
    """
    delimiter = ','
    rows = list()
    for row in itertools.product(*[range(l) for l in levels]):
        rows.append(delimiter.join(map(str, row)))
    header = delimiter.join(dyes)
    rows.insert(0, header)

    return '\n'.join(rows)


if __name__ == '__main__':
    # inputs
    nbarcodes = 24
    dyes = ['cy5.5', '594', '633']

    # create design
    design, dyes, levels = get_design(nbarcodes, dyes)
    print design, dyes, levels

    # create barcodes
    from DropSizeIntensityConverter import make_centroids

    levels = get_levels(nbarcodes, dyes)
    intensity_ranges = [INTENSITY_RANGES[lvl] for lvl in levels]

    cents = make_centroids(levels, intensity_ranges)

    for i, dye in enumerate(dyes):
        cents[:, i] /= BARCODE_DYES[dye]['intensity_ugml']

    print numpy.round(cents, 1)