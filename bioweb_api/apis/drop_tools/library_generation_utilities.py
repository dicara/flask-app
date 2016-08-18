import itertools

from matplotlib import pyplot as plt
import numpy

from bioweb_api import HOSTNAME
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from profile_database.datastore import Datastore
from profile_database.constants import DYE_NAME, PROFILE, LOT_NUMBER, \
    DETECTION_UUID, INTENSITY_CONC_RATIO, DYE_594, DYE_CY5_5, DYE_PE, \
    DYE_ALEXA700, DYE_633, DYE_CY7, DYE_FAM, DYE_JOE, DYE_ALEXA660, \
    DYE_DYLIGHT594, DYE_DYLIGHT633

# the minimum and maximum number of dyes
MIN_NDYES  = 1
MAX_NDYES  = 6
SATURATION_CAP = 65535
MAX_INTEN = {
    DYE_CY7: SATURATION_CAP,
    DYE_CY5_5: SATURATION_CAP,
    DYE_633: SATURATION_CAP,
    DYE_594: SATURATION_CAP,
    DYE_PE: SATURATION_CAP,
    DYE_ALEXA700: SATURATION_CAP,
    DYE_DYLIGHT594: SATURATION_CAP,
    DYE_ALEXA660: SATURATION_CAP,
    DYE_DYLIGHT633: SATURATION_CAP,
}

MIN_INTEN = 3000
# the minimum number of levels per barcode dye, must be at least two
MIN_NLEVELS = 2

# based on pdms chip data, 40 mW laser power, Gain 0
MAX_NLEVELS = {
    DYE_CY7: 4,
    DYE_CY5_5: 4,
    DYE_633: 4,
    DYE_594: 4,
    DYE_PE: 2,
    DYE_ALEXA700: 2,
    DYE_DYLIGHT594: 4,
    DYE_ALEXA660: 4,
    DYE_DYLIGHT633: 4,
}

# Define a preferred order from the dyes that you would prefer to have the
# least levels and those that you would prefer to have the most levels.
# In this case 594 is at the end indicating that it is preferred to have
# the most levels (if needed).
PREFERED_ORDER = [
    DYE_ALEXA700,
    DYE_PE,
    DYE_CY7,
    DYE_DYLIGHT633,
    DYE_633,
    DYE_ALEXA660,
    DYE_CY5_5,
    DYE_DYLIGHT594,
    DYE_594,
]


class LibraryDesign(object):
    def __init__(self, dyes_lots, requested_nbarcodes):
        # change the order based on preferred order
        self.dyes_lots = dyes_lots
        self._validate_dyes_lots()

        # sort dyes by preferred order
        self.dyes_lots.sort(key=lambda x: dict(zip(PREFERED_ORDER, range(len(PREFERED_ORDER))))[x[0]])
        self.dye_names = [dname for dname, _ in self.dyes_lots]
        self.lot_numbers = [lot_number for _, lot_number in self.dyes_lots]

        self.requested_nbarcodes = requested_nbarcodes
        self.profiles = self.get_profiles()

        # fam and joe usually emit a maximum of 15000 intensity units
        self.fam_profile = numpy.array(self.profiles[DYE_FAM][PROFILE]) * 15000
        self.joe_profile = numpy.array(self.profiles[DYE_JOE][PROFILE]) * 15000

        self.nlvls = None
        self.dye_max_intensities = None

        self._get_nlevels()
        self._set_dye_max_intensities()

    def get_profiles(self):
        """
        @return:    Dictionary, key is dye name, value is array of normalized
                    drop profile.
        """
        profiles = dict()
        db_profiles = Datastore(url=HOSTNAME).get_profiles()
        db_profiles.sort(key=lambda  x:x[DETECTION_UUID])
        for profile in db_profiles:
            if (profile[DYE_NAME], profile[LOT_NUMBER],) in self.dyes_lots:
                profiles[profile[DYE_NAME]] = {PROFILE: profile[PROFILE],
                                               INTENSITY_CONC_RATIO: profile[INTENSITY_CONC_RATIO]}
            elif profile[DYE_NAME] in [DYE_JOE, DYE_FAM]:
                profiles[profile[DYE_NAME]] = {PROFILE: profile[PROFILE],
                                               INTENSITY_CONC_RATIO: profile[INTENSITY_CONC_RATIO]}

        return profiles

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
        design = dict()
        for dye, nlvls in reversed(zip(self.dye_names, self.nlvls)):
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
            lvls_scaled_ug_ml = lvls_scaled_intensity / self.profiles[dye][INTENSITY_CONC_RATIO]
            design[dye] = [lvl for lvl in lvls_scaled_ug_ml]

        return design, self.dye_names, map(int, self.nlvls)

    def _rm_saturated(self, scalar_combos):
        """
        Remove designs where the max barcode profile exceeds the saturation limit

        @param scalar_combos:   Numpy array, max intensity combinations
        @return:                Numpy array, max intensity combinations
        """
        # use default dye map, it should have all barcode dyes by default
        ndims = scalar_combos.shape[1]
        dye_profs = numpy.array([self.profiles[dye][PROFILE] for dye in self.dye_names[:ndims]])

        barcode_profs = numpy.sum(scalar_combos.reshape(-1, ndims, 1) * dye_profs, axis=1)
        barcode_profs += self.fam_profile
        barcode_profs += self.joe_profile

        # remove barcodes that exceed the maximum
        invalid = (barcode_profs > SATURATION_CAP).any(axis=1)
        del barcode_profs
        return scalar_combos[~invalid]

    def _rm_most_variable(self, scalar_combos, percent_best):
        """
        Remove designs where the dyes have the most uneven intensity/level

        @param scalar_combos:   Numpy array, max intensity combinations
        @param percent_best:    Float, the percentage of combinations to return
        @return:                Numpy array, max intensity combinations
        """
        # criteria is the variance of intensity per level between dyes, lower is better
        ndims = scalar_combos.shape[1]
        intensity_per_lvl = scalar_combos/self.nlvls[:ndims]
        var_intensity_per_lvl = numpy.var(intensity_per_lvl, axis=1)

        # remove solutions that have a low probability of success
        mask_ = var_intensity_per_lvl < numpy.percentile(var_intensity_per_lvl, percent_best)
        return scalar_combos[mask_]

    def _set_dye_max_intensities(self, resolution=100.0):
        """
        The ideal library will take full advantage of our intensity space, which
        peaks at 65535 intensity units.  This function attempt to optimize the
        maximum level of each dye by recomposing the profiles and testing that
        they do not saturate.

        @param resolution:      Float, intensity unit spacing, i.e. resolution of 100.0
                                would result in intensities of: 1000.0, 1100.00, 1200.0...
        """
        # test various percent cutoffs
        for percent_best in numpy.arange(2.5, 25, 2.5):
            try:
                # make a group of scalars for each dye (dimension)
                scalars = [numpy.linspace(10000.0, MAX_INTEN[dye], resolution).reshape(-1, 1) for dye in self.dye_names]

                # create barcode profiles by summing each combination of dyes profiles
                # to find an optimal max barcode profile
                scalar_combos = scalars.pop(0)
                while scalars:
                    scalar_combos = numpy.hstack((
                        numpy.repeat(scalar_combos, resolution, axis=0),
                        numpy.tile(scalars.pop(0), (len(scalar_combos), 1))
                    ))
                    scalar_combos = self._rm_saturated(scalar_combos)
                    scalar_combos = self._rm_most_variable(scalar_combos, percent_best)

                midx = numpy.argmax(numpy.sum(scalar_combos, axis=1))
                # self.plot(scalar_combos[midx])

                self.dye_max_intensities = dict(zip(self.dye_names, scalar_combos[midx]))
                break
            except Exception as e:
                APP_LOGGER.exception(e)

        if not self.dye_max_intensities or len(self.dye_max_intensities) != len(self.dye_names):
            raise Exception('A library cannot be generated from this combination of dyes.')

    def _validate_dyes_lots(self):
        """
        Check the users input for invalid dyes
        """
        if not self.dyes_lots:
            raise Exception('No dyes were entered.')

        dye_names = [dname for dname, _ in self.dyes_lots]
        lot_numbers = [lot_number for _, lot_number in self.dyes_lots]
        if len(set(dye_names)) != len(dye_names):
            raise Exception('Duplicate dye names were found.')

        if len(set(lot_numbers)) != len(lot_numbers):
            raise Exception('Duplicate lot numbers were found.')

        if not (MIN_NDYES <= len(dye_names) <= MAX_NDYES):
            raise Exception('The number of dyes must be between %d and %d.' %
                            (MIN_NDYES, MAX_NDYES))

        for dname in dye_names:
            if dname not in MAX_NLEVELS:
                raise Exception('%s is not a valid dye.' % str(dname))

    def _get_nlevels(self):
        """
        Get the number of levels for each dye based on the number of
        barcodes and dyes that the user requested.  This function used a
        brute force search of all possible combinations of levels.

        @return:    A list of integers specifying the number of
                    levels of each dye, order corresponds to
                    the order of the dyes entered by the user.
        """
        dye_lvls = [range(MIN_NLEVELS, MAX_NLEVELS[dye] + 1) for dye in self.dye_names]
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
        dye_profiles = numpy.array([self.profiles[dye][PROFILE] for dye in self.dye_names])
        max_profile = list()
        for dye, prof, lvls, scalar in zip(self.dye_names, dye_profiles, self.nlvls, scalers):
            dye_profile_scaled = numpy.array(prof) * scalar
            label = '%s (%d levels)' % (dye, lvls)
            plt.plot(range(len(prof)), dye_profile_scaled, label=label)
            max_profile.append(dye_profile_scaled)
        plt.plot(range(len(self.fam_profile)), self.fam_profile, label=DYE_FAM)
        plt.plot(range(len(self.joe_profile)), self.joe_profile, label=DYE_JOE)
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
        header = delimiter.join(self.dye_names)
        rows = [header]
        for row in itertools.product(*[range(l) for l in self.nlvls]):
            rows.append(delimiter.join(map(str, row)))

        return '\n'.join(rows)


if __name__ == '__main__':
    input_requested_nbarcodes = 24
    input_dyes = [DYE_CY5_5, DYE_594, DYE_633, DYE_PE, ]
    input_lots = ['CY5.5RP000-16-012', 'DY594RPE000-16-009', 'DY633RPE000-16-009', 'RPE000-15-026B', ]

    ld = LibraryDesign(list(zip(input_dyes, input_lots)), input_requested_nbarcodes)
    design, dyes, levels = ld.generate()

    for dye, lvls in design.items():
        print '%s: %s' % (dye, [round(l, 2) for l in lvls],)