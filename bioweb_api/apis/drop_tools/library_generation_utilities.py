import itertools

from matplotlib import pyplot as plt
import numpy

from primary_analysis.dye_datastore import Datastore

# the minimum and maximum number of dyes
MIN_NDYES  = 1
MAX_NDYES  = 5
SATURATION_CAP = 65535
MAX_INTEN = {
    'pe-cy7': 30000,
    'cy5.5':  SATURATION_CAP,
    '633':    SATURATION_CAP,
    '594':    SATURATION_CAP,
    'pe':     30000,
}
MIN_INTEN = 3000
# the minimum number of levels per barcode dye, must be at least two
MIN_NLEVELS = 2

# based on pdms chip data, 40 mW laser power, Gain 0
BARCODE_DYES = {
    'pe-cy7': {'max_nlvls': 3, 'intensity_ugml': 1550.0},
    'cy5.5':  {'max_nlvls': 4, 'intensity_ugml': 3646.7},
    '633':    {'max_nlvls': 3, 'intensity_ugml': 1666.0},
    '594':    {'max_nlvls': 4, 'intensity_ugml': 3500.7},
    'pe':     {'max_nlvls': 2, 'intensity_ugml': 8333.3},
}

# Define a preferred order from the dyes that you would prefer to have the
# least levels and those that you would prefer to have the most levels.
# In this case 594 is at the end indicating that it is preferred to have
# the most levels (if needed).
PREFERED_ORDER = ['pe', 'pe-cy7', '633', 'cy5.5', '594']


class LibraryDesign(object):
    def __init__(self, dyes, requested_nbarcodes):
        # change the order based on preferred order
        self.dyes = [dye for dye in PREFERED_ORDER if dye in dyes]
        self._validate_dyes()

        self.requested_nbarcodes = requested_nbarcodes
        self.profiles = Datastore().dye_map()
        # fam and joe usually emit a maximum of 15000 intensity units
        self.fam_profile = numpy.array(self.profiles['fam']) * 15000
        self.joe_profile = numpy.array(self.profiles['joe']) * 15000

        self.nlvls = None
        self.dye_max_intensities = None

        self._get_nlevels()
        self._get_max_intensities()

    def generate(self, intensity_scaler=1.25):
        """
        Generate a design based on the dyes and requested number of barcodes

        @param intensity_scaler:    Float, scaled difference in intensity between the
                                    highest two levels and the lowest two.  For example
                                    a value of 1.25 means that the highest two levels have
                                    an intensity difference that is 1.25X greater than the
                                    lowest two levels.
        @return:                    A tuple containing the design (a list of dictionaries
                                    containing information on each dye in the design), and
                                    the input dyes and levels for each dye.
        """
        design = list()
        for dye, nlvls in reversed(zip(self.dyes, self.nlvls)):
            # scales are how the intensity gap between each level will scale
            # scales [1.0, 1.125, 1.25] means that the gap between the highest two
            # levels is 1.25 times greater than the gap between the lowest two levels
            scales = numpy.linspace(1.0, intensity_scaler, nlvls-1)

            # total relative intensity space the dye has to work with
            intensity_space = self.dye_max_intensities[dye] - MIN_INTEN

            # intensity space between levels at a scale of 1.0 (the minimum)
            min_intensity_space = intensity_space/numpy.sum(scales)

            # intensity space between levels scaled
            scaled_intensity_spaces = (scales * min_intensity_space)

            # scaled levels
            lvls_scaled_intensity = numpy.cumsum(numpy.concatenate(([MIN_INTEN], scaled_intensity_spaces)))

            # convert to ug/ml
            lvls_scaled_ug_ml = lvls_scaled_intensity / BARCODE_DYES[dye]['intensity_ugml']
            design.append({'name': dye, 'levels': ', '.join([str(round(lvl, 2)) for lvl in lvls_scaled_ug_ml])})

        return design, self.dyes, map(int, self.nlvls)

    def _rm_saturated(self, scalar_combos):
        """
        Remove designs where the max barcode profile exceeds the saturation limit

        @param scalar_combos:   Numpy array, max intensity combinations
        @return:                Numpy array, max intensity combinations
        """
        # use default dye map, it should have all barcode dyes by default
        ndims = scalar_combos.shape[1]
        dye_profs = numpy.array([self.profiles[dye] for dye in self.dyes[:ndims]])

        barcode_profs = numpy.sum(scalar_combos.reshape(-1, ndims, 1) * dye_profs, axis=1)
        barcode_profs += self.fam_profile
        barcode_profs += self.joe_profile

        # remove barcodes that exceed the maximum
        invalid = (barcode_profs > SATURATION_CAP).any(axis=1)
        del barcode_profs
        return scalar_combos[~invalid]

    def _rm_most_variable(self, scalar_combos):
        """
        Remove designs where the dyes have the most uneven intensity/level

        @param scalar_combos:   Numpy array, max intensity combinations
        @return:                Numpy array, max intensity combinations
        """
        # criteria is the variance of intensity per level between dyes, lower is better
        ndims = scalar_combos.shape[1]
        intensity_per_lvl = scalar_combos/self.nlvls[:ndims]
        var_intensity_per_lvl = numpy.var(intensity_per_lvl, axis=1)

        # keep the 2.5% lowest
        mask = var_intensity_per_lvl < numpy.percentile(var_intensity_per_lvl, 2.5)
        return scalar_combos[mask]

    def _get_max_intensities(self, resolution=40):
        """
        The ideal library will take full advantage of our intensity space, which
        peaks at 65535 intensity units.  This function attempt to optimize the
        maximum level of each dye by recomposing the profiles and testing that
        they do not saturate.

        @param resolution:  Integer, the number of intensities to test per dye
        """
        # make a group of scalars for each dye (dimension)
        scalars = [numpy.linspace(20000, MAX_INTEN[dye], resolution).reshape(-1, 1) for dye in self.dyes]

        # create barcode profiles by summing each combination of dyes profiles
        # to find an optimal max barcode profile
        scalar_combos = scalars.pop(0)
        while scalars:
            scalar_combos = numpy.hstack((
                numpy.repeat(scalar_combos, resolution, axis=0),
                numpy.tile(scalars.pop(0), (len(scalar_combos), 1))
            ))

            scalar_combos = self._rm_saturated(scalar_combos)
            scalar_combos = self._rm_most_variable(scalar_combos)

        midx = numpy.argmax(numpy.sum(scalar_combos, axis=1))
        # self.plot(scalar_combos[midx])

        self.dye_max_intensities = dict(zip(self.dyes, scalar_combos[midx]))

    def _validate_dyes(self):
        """
        Check the users input for invalid dyes
        """
        if not self.dyes:
            raise Exception('No dyes were entered.')

        if len(set(self.dyes)) != len(self.dyes):
            raise Exception('Duplicate dye entries found.')

        if not (MIN_NDYES <= len(self.dyes) <= MAX_NDYES):
            raise Exception('The number of dyes must be between %d and %d.' %
                            (MIN_NDYES, MAX_NDYES))

        for dye in self.dyes:
            if dye not in BARCODE_DYES:
                raise Exception('%s is not a valid dye.' % str(dye))

    def _get_nlevels(self):
        """
        Get the number of levels for each dye based on the number of
        barcodes and dyes that the user requested.  This function used a
        brute force search of all possible combinations of levels.

        @return:    A list of integers specifying the number of
                    levels of each dye, order corresponds to
                    the order of the dyes entered by the user.
        """
        dye_lvls = [range(MIN_NLEVELS, BARCODE_DYES[dye]['max_nlvls'] + 1) for dye in self.dyes]
        dye_lvl_combinations = numpy.array(list(itertools.product(*dye_lvls)))

        nbarcodes = numpy.product(dye_lvl_combinations, axis=1)
        valid_lvl_combinations = dye_lvl_combinations[nbarcodes - self.requested_nbarcodes == 0]

        if valid_lvl_combinations.size <= 0:
            raise Exception('Library cannot be made using specified inputs')

        self.nlvls = valid_lvl_combinations[0]

    def plot(self, scalers):
        """
        A function to generate a visualization of the candidate profiles
        and what their recomposition would look like.

        @param scalers: A list of integers used to scale each dye
        """
        dye_profiles = numpy.array([self.profiles[dye] for dye in self.dyes])
        max_profile = list()
        for dye, prof, lvls, scalar in zip(self.dyes, dye_profiles, self.nlvls, scalers):
            dye_profile_scaled = numpy.array(prof) * scalar
            label = '%s (%d levels)' % (dye, lvls)
            plt.plot(range(len(prof)), dye_profile_scaled, label=label)
            max_profile.append(dye_profile_scaled)
        plt.plot(range(len(self.fam_profile)), self.fam_profile, label='fam')
        plt.plot(range(len(self.joe_profile)), self.joe_profile, label='joe')
        max_profile.append(self.joe_profile)
        max_profile.append(self.fam_profile)

        max_profile = numpy.sum(numpy.array(max_profile), axis=0)
        plt.plot(range(len(max_profile)), max_profile, 'k--', label='Max Profile')
        plt.plot(range(len(max_profile)), [SATURATION_CAP] * len(max_profile), 'y--', label='Saturation')
        plt.legend(loc=('upper right'))
        plt.show()

    def get_csv_str(self):
        """
        Generate the contents of a csv file.

        @return:        A csv string.
        """
        delimiter = ','
        header = delimiter.join(self.dyes)
        rows = [header]
        for row in itertools.product(*[range(l) for l in self.nlvls]):
            rows.append(delimiter.join(map(str, row)))

        return '\n'.join(rows)


if __name__ == '__main__':
    # input_requested_nbarcodes = 24
    # input_dyes = ['cy5.5', '594', '633']
    input_requested_nbarcodes = 288
    input_dyes = ['cy5.5', '594', '633', 'pe-cy7', 'pe']

    ld = LibraryDesign(input_dyes, input_requested_nbarcodes)
    design, dyes, levels = ld.generate()

    print design
    print dyes
    print levels