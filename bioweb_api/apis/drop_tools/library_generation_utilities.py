from collections import OrderedDict
import itertools

from matplotlib import pyplot as plt
import numpy
from scipy.spatial import distance

from bioweb_api import HOSTNAME
from bioweb_api.utilities.logging_utilities import APP_LOGGER
from profile_database.datastore import Datastore
from profile_database.constants import DYE_NAME, PROFILE, LOT_NUMBER, \
    INTENSITY_CONC_RATIO, DYE_PE, DYE_CY7, DYE_FAM, DYE_JOE, DYE_IF700, \
    DYE_IF660, DYE_IF594, DYE_IF610, DYE_AT633, DATE, DYE_IF555, PEAK_PIXEL

# the minimum and maximum number of dyes
MIN_NDYES  = 2
SATURATION_CAP = 65535
MAX_INTEN = SATURATION_CAP
MIN_INTEN = 3000
# the minimum number of levels per barcode dye, must be at least two
DEFAULT_MIN_NLEVELS = 2
DEFAULT_MAX_NLEVELS = 4

# based on pdms chip data, 40 mW laser power, Gain 0
# by default PE should be restriced to two levels
# any dyes that must have a restricted number of levels below the default are set here
# user requests can override these setting (if user requests 3 levels of PE they will get 3 levels)
MAX_NLEVELS = {
    DYE_PE: 2,
}



class LibraryDesign(object):
    def __init__(self, requested_nbarcodes, requested_dye_lots=None,
                 requested_ndyes=None, min_peak_difference=3,
                 assay_dye=DYE_FAM, assay_intensity=15000,
                 pico1_dye=None, pico1_intensity=15000,
                 pico2_dye=DYE_JOE, pico2_intensity=15000,
                 intensity_scaler=1.25):
        """
        @param requested_nbarcodes: Integer, number of barcodes user requires
        @param requested_dye_lots:  List of tuples, each tuple is...
                                    (dye name, dye lot number, dye number of levels)
        @param requested_ndyes:     Integer, number of dyes user requires
        @param min_peak_difference: Integer, minimum difference between dye peaks
        @param assay_dye:           String, name of assay dye
        @param assay_intensity:     Integer, intensity of assay dye
        @param pico1_dye:           String, name of picoinjection 1 dye
        @param pico1_intensity:     Integer, intensity of picoinjection 1 dye
        @param pico2_dye:           String, name of picoinjection 2 dye
        @param pico2_intensity:     Integer, intensity of picoinjection 2 dye
        @param intensity_scaler:    Float, maximum difference in level increase
                                    between lowest and highest levels
        """
        self._requested_nbarcodes = requested_nbarcodes
        self._requested_dye_lots = requested_dye_lots if requested_dye_lots is not None else list()
        self._requested_ndyes = requested_ndyes

        self._assay_dye = assay_dye
        self._assay_intensity = assay_intensity
        self._pico1_dye = pico1_dye
        self._pico1_intensity = pico1_intensity
        self._pico2_dye = pico2_dye
        self._pico2_intensity = pico2_intensity
        self._intensity_scaler = intensity_scaler
        self._min_peak_difference = min_peak_difference

        # check inputs for invalid entries
        self._validate_inputs()

        # set barcode dye data variables
        self._barcode_profile_map = OrderedDict()
        self._barcode_lot_map = OrderedDict()
        self._barcode_potency_map = OrderedDict()
        self._barcode_peaks_map = OrderedDict()
        self._set_barcode_maps()
        self._barcode_dyes = numpy.array(self._barcode_profile_map.keys())
        self._barcode_profiles = numpy.array(self._barcode_profile_map.values())
        self._barcode_peaks = numpy.array(self._barcode_peaks_map.values())

        # set min and max level variables
        self._barcode_min_nlvls = numpy.array([DEFAULT_MIN_NLEVELS for _ in self._barcode_dyes])
        self._barcode_max_nlvls = numpy.array([self.default_max_nlvls(dye) for dye in self._barcode_dyes])
        self._barcode_lvl_ranges = None
        self._set_nlvls()

        # set non-barcode variables
        self._non_barcode_profile_map = OrderedDict()
        self._non_barcode_lot_map = OrderedDict()
        self._non_barcode_intensity_map = OrderedDict()
        self._non_barcode_peaks = None
        self._non_barcode_profile = None
        self._normalized_non_barcode_profile = None
        self._set_non_barcode_profiles()

        self._design_candidates = list()

    @property
    def need_additional_db_dyes(self):
        """
        @return:    Bool, whether or not user needs additional dyes.  True when 
                    there is a request for more dyes than the user specified.  
                    False otherwise
        """
        return self._requested_ndyes is not None and self._requested_ndyes > len(self._requested_dye_lots)

    def default_max_nlvls(self, dye):
        return MAX_NLEVELS.get(dye, DEFAULT_MAX_NLEVELS)

    def _validate_inputs(self):
        """
        Check inputs for conflicts.
        """
        if self._requested_ndyes is not None:
            if self._requested_ndyes < MIN_NDYES:
                raise Exception('The number of barcode dyes must be greater than %d.' % MIN_NDYES)

        for name, _, nlvls in self._requested_dye_lots:
            if self._pico1_dye == name:
                raise Exception('Pico 1 dye cannot be a barcode dye.')
            if self._pico2_dye == name:
                raise Exception('Pico 2 dye cannot be a barcode dye.')
            if self._assay_dye == name:
                raise Exception('Assay dye cannot be a barcode dye.')

            if nlvls is not None and nlvls < DEFAULT_MIN_NLEVELS:
                raise Exception('Requested number of levels for dye %s is below minimum of %d' %
                                (name, DEFAULT_MIN_NLEVELS))

            if nlvls is not None and nlvls > self.default_max_nlvls(name):
                raise Exception('Requested number of levels for dye %s is above maximum %d' %
                                (name, self.default_max_nlvls(name)))

        if self._requested_dye_lots:
            dye_names = [name for name, _, _ in self._requested_dye_lots]
            lot_numbers = [lot for _, lot, _ in self._requested_dye_lots]
            if len(set(dye_names)) != len(dye_names):
                raise Exception('Duplicate dye names were found.')

            if len(set(lot_numbers)) != len(lot_numbers):
                raise Exception('Duplicate lot numbers were found.')

    def _set_barcode_maps(self):
        """
        Set the dictionary with available barcode dye profiles
        """
        # get requested lots first
        for name, lot, _ in self._requested_dye_lots:
            # preference should be lot then name
            if lot is not None:
                db_records = sorted(Datastore(url=HOSTNAME).get_lot(lot), key=lambda x: x[DATE])
            else:
                db_records = sorted(Datastore(url=HOSTNAME).get_dye(name), key=lambda x: x[DATE])

            if not db_records:
                raise Exception('Dye %s was not found in the database.' % name)

            most_recent = db_records[-1]
            self._barcode_profile_map[most_recent[DYE_NAME]] = numpy.array(most_recent[PROFILE])
            self._barcode_lot_map[most_recent[DYE_NAME]] = most_recent[LOT_NUMBER]
            self._barcode_potency_map[most_recent[DYE_NAME]] = most_recent[INTENSITY_CONC_RATIO]
            self._barcode_peaks_map[most_recent[DYE_NAME]] = most_recent[PEAK_PIXEL]

        # The user may want the algorithm to recommend one or more additional dyes
        # get all the profiles (most recent are preferred)
        if not self._requested_dye_lots or self.need_additional_db_dyes:
            non_barcode_dyes = {self._assay_dye, self._pico1_dye, self._pico2_dye}
            for profile in sorted(Datastore(url=HOSTNAME).get_profiles(), key=lambda x: x[DATE], reverse=True):
                if profile[DYE_NAME] not in self._barcode_profile_map and profile[DYE_NAME] not in non_barcode_dyes:
                    self._barcode_profile_map[profile[DYE_NAME]] = numpy.array(profile[PROFILE])
                    self._barcode_lot_map[profile[DYE_NAME]] = profile[LOT_NUMBER]
                    self._barcode_potency_map[profile[DYE_NAME]] = profile[INTENSITY_CONC_RATIO]
                    self._barcode_peaks_map[profile[DYE_NAME]] = profile[PEAK_PIXEL]

    def _set_non_barcode_profiles(self):
        """
        Set the normalized and combined profile for non-barcode dyes
        """
        prof_len = self._barcode_profiles.shape[1]
        self._non_barcode_profile = numpy.tile(0.0, (prof_len,))
        self._normalized_non_barcode_profile = numpy.tile(0.0, (prof_len,))
        non_barcode_peaks = list()

        for non_barcode_dye, intensity in zip([self._assay_dye, self._pico1_dye, self._pico2_dye],
                                  [self._assay_intensity, self._pico1_intensity, self._pico2_intensity]):
            if non_barcode_dye is not None:
                db_records = sorted(Datastore(url=HOSTNAME).get_dye(non_barcode_dye), key=lambda x: x[DATE])
                if not db_records:
                    raise Exception('Could not retrieve %s information from the database.' % non_barcode_dye)
                most_recent = db_records[-1]
                profile = numpy.array(most_recent[PROFILE])
                self._non_barcode_profile += (profile * intensity)
                self._normalized_non_barcode_profile += profile
                self._non_barcode_profile_map[non_barcode_dye] = profile
                self._non_barcode_lot_map[non_barcode_dye] = most_recent[LOT_NUMBER]
                self._non_barcode_intensity_map[non_barcode_dye] = intensity
                non_barcode_peaks.append(db_records[-1][PEAK_PIXEL])

        self._non_barcode_peaks = numpy.array(non_barcode_peaks)

    def _set_nlvls(self):
        """
        Sets the minimum/maximum number of levels for a dye if the user specified it.
        Also sets the lvl ranges for each dye.
        """
        lvl_ranges = list()
        for name, _, nlvls in self._requested_dye_lots:
            if nlvls is not None:
                dye_idx = numpy.where(self._barcode_dyes == name)[0]
                self._barcode_min_nlvls[dye_idx] = nlvls
                self._barcode_max_nlvls[dye_idx] = nlvls

        for min_nlvl, max_nlvl in zip(self._barcode_min_nlvls, self._barcode_max_nlvls):
            lvl_ranges.append(numpy.arange(min_nlvl, max_nlvl + 1, dtype=numpy.uint8))

        self._barcode_lvl_ranges = numpy.array(lvl_ranges)

    def generate(self):
        """
        Generate a library design.
        """
        if self._requested_ndyes is None:
            for ndyes in xrange(1, len(self._barcode_profiles)+1):
                self._generate(ndyes)
        else:
            self._generate(self._requested_ndyes)

        self._design_candidates.sort(key=lambda x: x['separability'], reverse=True)

        if not self._design_candidates:
            raise Exception('Unable to generate design.')

        # best_design = self._design_candidates[0]
        # self.plot(best_design)

        return self._design_candidates

    def _generate(self, ndyes, nchoose=5):
        """
        @param ndyes:   1nteger, number of dyes to use per solution
        #param nchoose: Integer, maximum number of combinations that will be further optimized
        """
        # check to see if the minimum maximum levels of dyes can make the requested number of dyes
        min_nbarcodes = numpy.product(self._barcode_min_nlvls[numpy.argsort(self._barcode_min_nlvls)[:ndyes]])
        max_nbarcodes = numpy.product(self._barcode_max_nlvls[numpy.argsort(self._barcode_max_nlvls)[-ndyes:]])

        # too many dyes were selected
        if min_nbarcodes > self._requested_nbarcodes:
            APP_LOGGER.info('Cannot generate requested number of barcodes (%d).  '
                            'Smallest library would have %d barcodes.' %
                            (self._requested_nbarcodes, min_nbarcodes))
            return

        # too few dyes were selected
        if max_nbarcodes < self._requested_nbarcodes:
            APP_LOGGER.info('Cannot generate requested number of barcodes (%d).  '
                            'Largest library would have %d barcodes.' %
                            (self._requested_nbarcodes, max_nbarcodes))
            return

        # find the optimal number of levels for each dye combination
        requested_dye_idxs = set(range(len(self._requested_dye_lots)))
        optimal_nlvls = list()
        for dye_idxs in itertools.combinations(xrange(len(self._barcode_profiles)), ndyes):
            dye_idxs = numpy.array(dye_idxs)

            # ignore combinations that do not include requested dyes
            if self.need_additional_db_dyes and \
                    self._requested_dye_lots and \
                    not requested_dye_idxs.issubset(dye_idxs):
                continue

            # ignore combinations in which the peaks are too close
            peaks = numpy.concatenate((self._barcode_peaks[dye_idxs], self._non_barcode_peaks))
            if numpy.any(numpy.diff(numpy.sort(peaks)) < self._min_peak_difference):
                continue

            try:
                candidate_nlvls, candidate_lowest_peak = self._calc_optimal_nlvls(dye_idxs)
                optimal_nlvls.append((candidate_lowest_peak, dye_idxs, candidate_nlvls))
            except Exception as e:
                APP_LOGGER.exception(e)

        optimal_nlvls.sort(key=lambda x: x[0])

        for _, dye_idxs, nlvls in optimal_nlvls[: nchoose]:
            try:
                self._make_design(nlvls, dye_idxs)
            except Exception as e:
                APP_LOGGER.exception(e)

    def _make_design(self, nlvls, dye_idxs):
        """
        Generate the optimal design based on the number of levels for each dye.

        @param dye_idxs:    1D numpy array of the indexes of the barcode dyes
        @param nlvls:       1D numpy array of the number of levels for each dye
        """
        dye_max_intensities = self._calc_dye_max_intensities(dye_idxs, nlvls)
        intensity_lvls = list()
        design = {'barcode_dyes': {}, 'fiducial_dyes': {}}
        if self._assay_dye is not None:
            design['fiducial_dyes'][self._assay_dye] = {
                'intensity': int(self._assay_intensity),
                'lot_number': str(self._non_barcode_lot_map[self._assay_dye]),
            }

        if self._pico1_dye is not None:
            design['fiducial_dyes'][self._pico1_dye] = {
                'intensity': int(self._pico1_intensity),
                'lot_number': str(self._non_barcode_lot_map[self._pico1_dye]),
            }

        if self._pico2_dye is not None:
            design['fiducial_dyes'][self._pico2_dye] = {
                'intensity': int(self._pico2_intensity),
                'lot_number': str(self._non_barcode_lot_map[self._pico2_dye]),
            }

        for dname, lvls, max_intensity in zip(self._barcode_dyes[dye_idxs], nlvls, dye_max_intensities):
            scales = numpy.linspace(1.0, self._intensity_scaler, lvls-1)
            intensity_space = max_intensity - MIN_INTEN
            min_intensity_space = intensity_space/numpy.sum(scales)
            scaled_intensity_spaces = (scales * min_intensity_space)
            lvls_scaled_intensity = numpy.cumsum(numpy.concatenate(([MIN_INTEN], scaled_intensity_spaces)))
            intensity_lvls.append(lvls_scaled_intensity)
            design['barcode_dyes'][str(dname)] = {'potency': float(self._barcode_potency_map[dname]),
                                  'lot_number': str(self._barcode_lot_map[dname]),
                                  'intensities': [int(lvl) for lvl in lvls_scaled_intensity]}
        centroids = numpy.array(numpy.meshgrid(*intensity_lvls, copy=False)).T.reshape(-1, len(intensity_lvls))
        nn_dist = distance.squareform(distance.pdist(centroids))
        nn_dist[nn_dist == 0.0] = numpy.nan
        min_dists = numpy.nanmin(nn_dist, axis=1)
        ave_distance = numpy.mean(min_dists)
        design['separability'] = int(ave_distance)

        self._design_candidates.append(design)

    def _calc_optimal_nlvls(self, dye_idxs):
        """
        Get the number of levels for each dye based on the number of
        barcodes and dyes that the user requested.

        @param dye_idxs:    1D numpy array of the indexes of the barcode dyes
        @return:            1D numpy array of integers specifying the optimal
                            number of levels for each dye and float specifying
                            max intensity that can be expected by combining this
                            the number of levels.
        """
        nlvls_ranges = [self._barcode_lvl_ranges[idx] for idx in dye_idxs]

        # faster way to generate cartesian product of a list of arrays than itertools.product
        nlvl_products = numpy.array(numpy.meshgrid(*nlvls_ranges, copy=False)).T.reshape(-1, len(dye_idxs))

        # remove solutions where the number of barcodes does not match the requested number of barcodes
        nlvl_products = nlvl_products[numpy.product(nlvl_products, axis=1) == self._requested_nbarcodes]

        if nlvl_products.size <= 0:
            raise Exception('Cannot make %d barcodes from: %s' %
                            (self._requested_nbarcodes, ', '.join(self._barcode_dyes[dye_idxs])))

        # tile the barcode profiles based on the number of valid nlvl combinations
        normalized_profiles = numpy.tile(self._barcode_profiles[dye_idxs], (len(nlvl_products), 1, 1))
        # multiply each dye profile by the number of levels (nlvls)
        normalized_profiles *= nlvl_products.reshape(-1, len(dye_idxs), 1)

        summed_profiles = numpy.sum(normalized_profiles, axis=1)
        # add the profile representing the non barcode dyes
        summed_profiles += self._normalized_non_barcode_profile.reshape(1, -1)

        # get the peak intensity of the summed profile
        peak_intensities = numpy.amax(summed_profiles, axis=1)
        lowest_peak_idx = numpy.argmin(peak_intensities)

        # the best combination will have a lowest summed profile peak intensity
        return nlvl_products[lowest_peak_idx], peak_intensities[lowest_peak_idx]

    def _rm_saturated(self, scalar_combos, dye_idxs):
        """
        Remove designs where the max barcode profile exceeds the saturation limit

        @param scalar_combos:   Numpy array, max intensity combinations
        @return:                Numpy array, max intensity combinations
        """
        # use default dye map, it should have all barcode dyes by default
        ndims = scalar_combos.shape[1]
        dye_profs = self._barcode_profiles[dye_idxs[:ndims]]

        barcode_profs = numpy.sum(scalar_combos.reshape(-1, ndims, 1) * dye_profs, axis=1)
        barcode_profs += self._non_barcode_profile

        # remove barcodes that exceed the maximum
        invalid = (barcode_profs > SATURATION_CAP).any(axis=1)
        del barcode_profs
        return scalar_combos[~invalid]

    def _rm_most_variable(self, scalar_combos, percent_best, nlvls):
        """
        Remove designs where the dyes have the most uneven intensity/level

        @param scalar_combos:   Numpy array, max intensity combinations
        @param percent_best:    Float, the percentage of combinations to return
        @return:                Numpy array, max intensity combinations
        """
        # criteria is the variance of intensity per level between dyes, lower is better
        ndims = scalar_combos.shape[1]
        intensity_per_lvl = scalar_combos/nlvls[:ndims]
        var_intensity_per_lvl = numpy.var(intensity_per_lvl, axis=1)

        # remove solutions that have a low probability of success
        mask_ = var_intensity_per_lvl < numpy.percentile(var_intensity_per_lvl, percent_best)
        return scalar_combos[mask_]

    def _calc_dye_max_intensities(self, dye_idxs, nlvls, resolution=100.0):
        """
        The ideal library will take full advantage of our intensity space, which
        peaks at 65535 intensity units.  This function attempt to optimize the
        maximum level of each dye by recomposing the profiles and testing that
        they do not saturate.

        @param dye_idxs:    1D numpy array of the indexes of the barcode dyes
        @param nlvls:       1D numpy array of the number of levels for each dye
        @param resolution:  Float, intensity unit spacing, i.e. resolution of 100.0
                            would result in intensities of: 1000.0, 1100.00, 1200.0...
        @return:            1D numpy of maximum intensities for each dye.
        """
        dye_max_intensities = None
        # test various percent cutoffs
        for percent_best in numpy.arange(2.5, 25, 2.5):
            try:
                # make a group of scalars for each dye (dimension)
                scalars = [numpy.linspace(10000.0, MAX_INTEN, resolution).reshape(-1, 1) for _ in dye_idxs]
                # create barcode profiles by summing each combination of dyes profiles
                # to find an optimal max barcode profile
                scalar_combos = scalars.pop(0)
                while scalars:
                    scalar_combos = numpy.hstack((
                        numpy.repeat(scalar_combos, resolution, axis=0),
                        numpy.tile(scalars.pop(0), (len(scalar_combos), 1))
                    ))
                    scalar_combos = self._rm_saturated(scalar_combos, dye_idxs)
                    scalar_combos = self._rm_most_variable(scalar_combos, percent_best, nlvls)

                midx = numpy.argmax(numpy.sum(scalar_combos, axis=1))

                dye_max_intensities = scalar_combos[midx]
                break
            except Exception as e:
                APP_LOGGER.exception(e)

        if dye_max_intensities is None or len(dye_max_intensities) != len(dye_idxs):
            raise Exception('A library cannot be generated from this combination of dyes.')

        return dye_max_intensities

    def plot(self, design):
        """
        A function to generate a visualization of the candidate profiles
        and what their recomposition would look like.

        @param design:  A dictionary with library design information
        """
        fig = plt.figure()
        profiles = list()
        for dye in design['dyes']:
            intensities = design['dyes'][dye]['intensities']
            max_intensity = max(intensities)
            profile = self._barcode_profile_map[dye] * max_intensity
            profiles.append(profile)
            plt.plot(range(len(profile)), profile, label='%s, %d levels' % (dye, len(intensities)))

        for dye in self._non_barcode_profile_map:
            max_intensity = self._non_barcode_intensity_map[dye]
            profile = self._non_barcode_profile_map[dye] * max_intensity
            profiles.append(profile)
            plt.plot(range(len(profile)), profile, label=dye)

        plt.title('%d Dyes, Separability: %d' % (len(design['dyes']), design['separability']))
        max_profile = numpy.sum(numpy.array(profiles), axis=0)
        plt.plot(range(len(max_profile)), max_profile, 'k--', label='Max Profile')
        plt.plot(range(len(max_profile)), [SATURATION_CAP] * len(max_profile), 'y--', label='Saturation')
        plt.legend(loc=('upper right'))
        plt.show()
        plt.close(fig)


if __name__ == '__main__':
    import time
    input_requested_nbarcodes = 192
    input_dyes = [DYE_IF594, DYE_IF610, DYE_AT633, DYE_IF660, DYE_IF700, DYE_CY7]
    input_lots = ['LMS-70020-048A', 'LMS-70020-049A', 'LMS-70020-050A', 'LMS-70020-054A', 'LMS-70020-055A', 'LMS-70020-056B']
    input_nlvls = [None, None, None, None, None, None]
    pico1_dye = DYE_IF555
    pico1_intensity = 15000
    requested_ndyes = None
    requested_dye_lots = list(zip(input_dyes, input_lots, input_nlvls))
    # requested_dye_lots = None

    ld = LibraryDesign(
        requested_dye_lots=requested_dye_lots,
        requested_nbarcodes=input_requested_nbarcodes,
        pico1_dye=DYE_IF555,
        pico1_intensity=pico1_intensity,
        requested_ndyes=requested_ndyes,
    )

    start = time.time()
    ld.generate()
    print time.time() - start
    # for dye, data in design.items():
    #     print dye, data
    #
    # for dye_name, data in design.items():
    #     print '%s: %s' % (dye_name, [round(l, 2) for l in data['levels']],)