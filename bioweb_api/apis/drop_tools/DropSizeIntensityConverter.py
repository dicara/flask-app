import itertools

import numpy
from scipy.spatial import distance
from sklearn import mixture

'''
CV_RATIO is the coefficient of variation (CV) scalar to adjust drop size
CV to intensity CV.  BKGROUND_STD is the background standard deviation
to account for decomp and spectral noise.  Both these values were
calculated from experimental data.
'''
CV_RATIO = 1.184
BKGROUND_STD = 300.0


class Cluster(object):
    """
    A collection of drops
    """
    def __init__(self, drops, cluster_id):
        """
        @param drops:       A 2D numpy array of drop decomps
        @param cluster_id:  A string specifying the cluster id
        """
        self.drops = drops
        self.ndims = drops.shape[1]
        self.cluster_id = cluster_id
        # store idxs of clusters that collide
        self.collisions = list()
        # store the % overlap of colliding clusters, same
        # length as self.collisions
        self.perc_overlap = list()

    @property
    def centroid(self):
        """
        @return: Numpy array representing cluster centroid
        """
        return numpy.median(self.drops, axis=0)


def make_centroids(lvls, ranges):
    """
    Make centroids based on dye levels and intensity range.

    @param lvls:    A list of integers, each integer is the number of lvls for
                    a dimension.
    @param ranges:  A list of tuples, each tuple has two integers specifying
                    the intensity range for that dimension.
    @return:        A numpy array of centroids.
    """
    intensities = list()
    for nlvls, (low, high) in zip(lvls, ranges):
        intensities.append(numpy.linspace(low, high, nlvls))
    return numpy.array(list(itertools.product(*intensities)))


def make_clusters(centroids, drop_ave, drop_std):
    """
    Make clusters from centroids.  Add noise based on drop size and
    standard deviation of drop size.

    @param centroids:   A 2D numpy array of the centroids.
    @param drop_ave:    Float specifying the average drop size.
    @param drop_std:    Float specifying standard deviation of drop size.
    @return:            A list where each element is a Cluster object.
    """

    # convert drop coefficient of variation (cv) to intensity cv
    ndims = centroids.shape[1]
    # simulate 500 drops per dimension, cap at 2000 drops
    ndrops = ndims * 500 if ndims * 500 <= 2000 else 2000
    drop_cv = drop_std/drop_ave
    int_cv = drop_cv * CV_RATIO

    # create clusters from centroids
    clusters = list()
    fill_len = len(str(len(centroids)))
    for idx, centroid in enumerate(centroids):
        # make a cluster from centroid
        cluster_data = numpy.array([centroid] * ndrops)

        # make a standard deviation for each drop
        stddevs = numpy.random.normal(0.0, 1.0, size=ndrops)

        # convert the stddev to intensities based on the intensity cv
        intensity_std = centroid * int_cv + 0.1
        deviations = numpy.array([intensity_std]*ndrops)
        deviations *= stddevs.reshape(cluster_data.shape[0], -1)

        # apply the deviations to the centroid to create the cluster
        cluster_data += deviations

        # add noise to simulate decomp/spectral noise
        cluster_data += numpy.random.normal(0.0, BKGROUND_STD, size=cluster_data.shape)
        cluster_id = 'c%s' % str(idx).zfill(fill_len)
        clusters.append(Cluster(cluster_data, cluster_id))

    return clusters


def check_collision(clusters, num_nn_check=4, min_prob_thresh=0.66):
    """
    Check for possible cross contamination (collision) between clusters
    using sklearn's gaussian mixture model.  Collision information is
    appended to cluster objects.

    @param clusters:        A list of Cluster objects.
    @param num_nn_check:    A integer specifying the number of nearest
                            neighbors to check for each cluster
    @param min_prob_thresh: A float specifying the minimum probability
                            a drop must have to belong to a cluster.
    @return:                A list of tuples specifying potential cluster
                            collisions. Tuple format is (cluster ID#1,
                            cluster ID#2, percent overlap)
    """
    # get nearest neighbors
    ndrops = len(clusters[0].drops)
    centroids = numpy.array([c.centroid for c in clusters])
    dists = distance.squareform(distance.pdist(centroids))
    nearest_neighbors_idxs = numpy.argsort(dists, axis=1)[:, 1:num_nn_check+1]

    # make a list of unique index pairs to prevent redundant checking
    nn_checks = list()
    for idx, nns in enumerate(nearest_neighbors_idxs):
        nn_checks.extend([sorted([idx, nn]) for nn in nns])
    nn_checks = set(map(tuple, nn_checks))

    collisions = list()
    # check for collisions
    for idx1, idx2 in nn_checks:
        c1 = clusters[idx1]
        c2 = clusters[idx2]
        gmm = mixture.GMM(n_components=2, covariance_type='full')
        data = numpy.concatenate((c1.drops, c2.drops))
        gmm.fit(data)
        probabilities = gmm.predict_proba(data)
        max_prob = numpy.amax(probabilities, axis=1)
        above_thresh = numpy.where(max_prob <= min_prob_thresh)[0]
        if above_thresh.size > 0:
            perc_overlap = (len(above_thresh) / (ndrops * 2.0)) * 100
            clusters[idx1].collisions.append(idx2)
            clusters[idx2].collisions.append(idx1)
            clusters[idx1].perc_overlap.append(perc_overlap)
            clusters[idx2].perc_overlap.append(perc_overlap)
            collisions.append({'id_1': c1.cluster_id,
                               'id_2': c2.cluster_id,
                               'overlap': perc_overlap})

    return collisions



if __name__ == '__main__':
    # a simple example using two dyes at 4 levels each
    centroids = make_centroids([4, 4], [(0, 30000), (0, 30000)])
    clusters = make_clusters(centroids, drop_ave=28.0, drop_std=1.5)
    check_collision(clusters)

    # plot it
    from matplotlib import pyplot
    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)
    for idx, c in enumerate(clusters):
        color = 'r' if c.collisions else 'y'
        ax.scatter(c.drops[:, 0], c.drops[:, 1], edgecolor='none', s=5, c=color)
        cstr = 'c%s' % str(idx).zfill(1)
        if c.collisions:
            for cid, per in zip(c.collisions, c.perc_overlap):
                cstr += ' c%s: %s%%,' % (str(cid).zfill(1), str(round(per,1)))
        ax.annotate(cstr, xy=c.centroid)

    pyplot.show()