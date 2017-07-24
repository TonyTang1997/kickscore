import numpy as np

from math import exp, sqrt
from .kernel import Kernel


MEASUREMENT_VECTOR = np.array([1., 0., 0.])
NOISE_EFFECT = np.array([0., 0., 1.])
STATIONARY_MEAN = np.zeros(3)


class Matern52(Kernel):

    def __init__(self, var, lscale):
        self.var = var
        self.lscale = lscale
        self.lambda_ = sqrt(5) / lscale

    def k_mat(self, ts1, ts2=None, diag=False):
        if ts2 is None:
            ts2 = ts1
        r = Kernel.distances(ts1, ts2) / self.lscale
        sqrt5 = sqrt(5)
        return self.var * (1 + sqrt5 * r + (5/3) * r**2) * np.exp(-sqrt5 * r)

    def k_diag(self, ts):
        return self.var * np.ones(len(ts))

    @property
    def order(self):
        return 3

    def transition(self, delta):
        """Transition matrix :math:`A` for a given time interval."""
        # TODO This can be improved by rewriting in terms of $d / a$.
        d = delta
        a = self.lambda_
        A = np.array([
            [(d*d * a*a) / 2 + d * a + 1,
                d * (d * a + 1),
                d*d / 2],
            [-(d*d * a**3) / 2,
                -(d*d * a*a) + d * a + 1,
                -(d / 2) * (d * a - 2)],
            [(d * a*a*a / 2) * (d * a - 2),
                (d * a*a) * (d * a - 3),
                (d*d * a*a - 4 * d * a + 2) / 2],
        ])
        return exp(-d * a) * A

    def noise_cov(self, delta):
        d = delta
        a = self.lambda_
        c = exp(-2 * d * a)
        x11 = -(1 / 3) * (c * (2 * d**4 * a**4 + 4 * d**3 * a**3
                + 6 * d*d * a*a + 6 * d * a + 3) - 3)
        x12 = c * (2 / 3) * a**5 * d**4
        x13 = -(a*a / 3) * (c * (2 * d**4 * a**4 - 4 * d**3 * a**3
                - 2 * d*d * a*a - 2 * d * a - 1) + 1)
        x22 = -(a*a / 3) * (c * (2 * d**4 * a**4 - 4 * d**3 * a**3
                + 2 * d*d * a*a + 2 * d * a + 1) - 1)
        x23 = c * (2 / 3) * d*d * a**5 * (d * a - 2)**2
        x33 = -(a**4 / 3) * (c * (2 * d**4 * a**4 - 12 * d**3 * a**3
                + 22 * d*d * a*a - 10 * d * a + 3) - 3)
        mat = np.array([
            [x11, x12, x13],
            [x12, x22, x23],
            [x13, x23, x33],
        ])
        return self.var * mat

    @property
    def initial_mean(self):
        return STATIONARY_MEAN

    @property
    def initial_cov(self):
        return self.stationary_cov

    @property
    def measurement_vector(self):
        return MEASUREMENT_VECTOR

    @property
    def feedback(self):
        a = self.lambda_
        mat = np.array([
            [0     , 1         , 0      ],
            [0     , 0         , 1      ],
            [-a**3 , -3 * a**2 , -3 * a ],
        ])
        return mat

    @property
    def noise_effect(self):
        return NOISE_EFFECT

    @property
    def noise_density(self):
        return (16 / 3) * self.var * self.lambda_**5

    @property
    def stationary_mean(self):
        return STATIONARY_MEAN

    @property
    def stationary_cov(self):
        a = self.lambda_
        mat = np.array([
            [1        , 0       , -a*a / 3],
            [0        , a*a / 3 , 0       ],
            [-a*a / 3 , 0       , a**4    ],
        ])
        return self.var * mat
