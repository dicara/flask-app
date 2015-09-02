import itertools

from matplotlib import pyplot as plt
import numpy

from primary_analysis.dye_datastore import Datastore

# the minimum and maximum number of dyes
MIN_NDYES  = 1
MAX_NDYES  = 5
INTENSITY_CAP = 65535
MAX_INTEN = {
    'pe-cy7': 30000,
    'cy5.5':  INTENSITY_CAP,
    '633':    INTENSITY_CAP,
    '594':    INTENSITY_CAP,
    'pe':     30000,
}
MIN_INTEN = 3000
# the minimum number of levels per barcode dye, must be at least two
MIN_NLEVELS = 2

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



def plot_profiles(scalers, dyes, dye_profiles, nlvls):
    """
    A function to generate a visualization of the candidate profiles
    and what their recomposition would look like.

    @param scalers:         A list of integers used to scale each dye
    @param dyes:            A list of dye names, order corresponds to scalers order
    @param dye_profiles:    A list of dye profiles, order corresponds to scalers order
    @param nlvls:           A list of dye levels, order corresponds to scalers order
    """
    max_profile = list()
    for dye, prof, lvls, scalar in zip(dyes, dye_profiles, nlvls, scalers):
        dye_profile_scaled = numpy.array(prof) * scalar
        label = '%s (%d levels)' % (dye, lvls)
        plt.plot(range(len(prof)), dye_profile_scaled, label=label)
        max_profile.append(dye_profile_scaled)

    max_profile = numpy.sum(numpy.array(max_profile), axis=0)
    plt.plot(range(len(max_profile)), max_profile, 'k--', label='Max Profile')
    plt.plot(range(len(max_profile)), [INTENSITY_CAP] * len(max_profile), 'y--', label='Saturation')
    plt.legend(loc=('upper right'))


def get_maxlvls(nbarcodes, dyes, resolution=40):
    """
    The ideal library will take full advantage of our intensity space, which
    peaks at 65535 intensity units.  This function attempt to optimize the
    maximum level of each dye by recomposing the profiles and testing that
    they do not saturate.

    @param dyes:    A list of dye names
    @return:        A dictionary, keys are dye names, values are max intensity
    """
    # sort by prefered order so dye with most tolerance for levels is last
    dyes = sorted(dyes, key = lambda x: PREFERED_ORDER.index(x))
    # use default dye map, it should have all barcode dyes by default
    profiles = Datastore().dye_map()
    dye_profs = numpy.array([profiles[dye] for dye in dyes])
    nlvls = get_levels(nbarcodes, dyes)

    # make a group of scalars for each dye (dimension)
    scalars = [numpy.linspace(20000, MAX_INTEN[dye], resolution).reshape(-1, 1) for dye in dyes]

    # create barcode profiles by summing each combination of dyes profiles
    # to find an optimal max barcode profile
    scalar_combos = scalars.pop(0)
    while scalars:
        scalar_combos = numpy.hstack((
            numpy.repeat(scalar_combos, resolution, axis=0),
            numpy.tile(scalars.pop(0), (len(scalar_combos), 1))
        ))

        ndims = scalar_combos.shape[1]
        barcode_profs = numpy.sum(scalar_combos.reshape(-1, ndims, 1) * dye_profs[:ndims], axis=1)

        # remove barcodes that exceed the maximum
        invalid = (barcode_profs > INTENSITY_CAP).any(axis=1)
        scalar_combos = scalar_combos[~invalid]
        del barcode_profs

        # remove barcodes that are too low
        criteria = numpy.sum(numpy.abs(numpy.diff(scalar_combos/nlvls[:ndims], axis=1)), axis=1)
        mask = criteria < numpy.percentile(criteria, 2.5)
        scalar_combos = scalar_combos[mask]

    midx = numpy.argmax(numpy.sum(scalar_combos, axis=1))
    # plot_profiles(scalar_combos[midx], dyes, dye_profs, nlvls)

    return dict(zip(dyes, scalar_combos[midx]))


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
    max_lvls = get_maxlvls(nbarcodes, dyes)

    design = list()
    for dye, nlvls in zip(dyes, levels):
        int_range = numpy.linspace(MIN_INTEN, max_lvls[dye], nlvls)
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
    # nbarcodes = 288
    # dyes = ['cy5.5', '594', '633', 'pe-cy7', 'pe']

    # create design
    design, dyes, levels = get_design(nbarcodes, dyes)

