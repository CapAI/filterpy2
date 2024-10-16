# -*- coding: utf-8 -*-
"""Copyright 2015 Roger R Labbe Jr.

FilterPy library.
http://github.com/rlabbe/filterpy

Documentation at:
https://filterpy.readthedocs.org

Supporting book at:
https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python

This is licensed under an MIT license. See the readme.MD file
for more information.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy.random as random
import numpy as np
import matplotlib.pyplot as plt
from filterpy2.common import Saver
from filterpy2.kalman import SquareRootKalmanFilter, KalmanFilter

DO_PLOT = False


def test_noisy_1d():
    f = KalmanFilter(dim_x=2, dim_z=2)

    f.x = np.array([[2.0], [0.0]])  # initial state (location and velocity)

    f.F = np.array([[1.0, 1.0], [0.0, 1.0]])  # state transition matrix

    f.H = np.array([[1.0, 0.0], [0.0, 1.0]])  # Measurement function
    f.P *= 1000.0  # covariance matrix
    f.R *= 5  # state uncertainty
    f.Q *= 0.0001  # process uncertainty

    fsq = SquareRootKalmanFilter(dim_x=2, dim_z=2)

    fsq.x = np.array([[2.0], [0.0]])  # initial state (location and velocity)

    fsq.F = np.array([[1.0, 1.0], [0.0, 1.0]])  # state transition matrix

    fsq.H = np.array([[1.0, 0.0], [0.0, 1.0]])  # Measurement function
    fsq.P = np.eye(2) * 1000.0  # covariance matrix
    fsq.R *= 5  # state uncertainty
    fsq.Q *= 0.0001  # process uncertainty

    # does __repr__ work?
    str(fsq)

    measurements = []
    results = []

    zs = []
    s = Saver(fsq)
    for t in range(100):
        # create measurement = t plus white noise for position and 1 +
        # white noise for velocity
        z = np.array([[t], [1.0]]) + random.randn(2, 1) * 20
        zs.append(z)

        # perform kalman filtering
        f.update(z)
        f.predict()

        fsq.update(z)
        fsq.predict()

        assert abs(f.x[0, 0] - fsq.x[0, 0]) < 1.0e-12
        assert abs(f.x[1, 0] - fsq.x[1, 0]) < 1.0e-12

        S_from_sqrt = fsq.S
        SI_from_sqrt = fsq.SI
        for i in range(f.S.shape[0]):
            for j in range(f.S.shape[1]):
                assert abs(f.S[i, j] - S_from_sqrt[i, j]) < 1e-6
                assert abs(f.SI[i, j] - SI_from_sqrt[i, j]) < 1e-6

        # save data
        results.append(f.x[0, 0])
        measurements.append(z)
        s.save()
    s.to_array()

    for i in range(f.P.shape[0]):
        for j in range(f.P.shape[1]):
            assert abs(f.P[i, j] - fsq.P[i, j]) < 1e-6

    # now do a batch run with the stored z values so we can test that
    # it is working the same as the recursive implementation.
    # give slightly different P so result is slightly different
    f.x = np.array([[2.0, 0]]).T
    f.P = np.eye(2) * 100.0
    m, c, _, _ = f.batch_filter(zs, update_first=False)

    # plot data
    if DO_PLOT:
        (p1,) = plt.plot(measurements, "r", alpha=0.5)
        (p2,) = plt.plot(results, "b")
        (p4,) = plt.plot(m[:, 0], "m")
        (p3,) = plt.plot([0, 100], [0, 100], "g")  # perfect result
        plt.legend(
            [p1, p2, p3, p4],
            ["noisy measurement", "KF output", "ideal", "batch"],
            loc=4,
        )

        plt.show()


if __name__ == "__main__":
    DO_PLOT = True
    test_noisy_1d()
