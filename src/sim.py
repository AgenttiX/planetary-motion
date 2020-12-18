import typing as tp

import numpy as np

import core

# Units and constants
# Astronomical unit
AU = 1.495978707e11
# Gravitational constant
G = 6.67430e-11
# Time
YEAR_IN_D = 365.25
YEAR_IN_S = 86400


class Celestial:
    def __init__(
            self,
            x: tp.Union[np.ndarray, float],
            v: tp.Union[np.ndarray, float],
            m: float,
            radius: float,
            color: tp.Tuple[int, int, int],
            reference: "Celestial" = None,
            period: float = None,
            x_min: float = None,
            x_max: float = None,
            texture_low: str = None,
            texture_high: str = None,
    ):
        """
        A celestial object
        :param x: position (m)
        :param v: velocity (m/s)
        :param m: mass (kg)
        :param radius: (m)
        :param color: RGB color tuple
        :param reference: reference object for the position and velocity
        :param period: orbital period (years)
        """
        if isinstance(x, (int, float)):
            self.x = np.array([x, 0, 0])
        else:
            self.x = x
        if isinstance(v, (int, float)):
            self.v = np.array([0, v, 0])
        else:
            self.v = v
        if reference is not None:
            self.x += reference.x
            self.v += reference.v
        self.reference = reference
        self.m = m
        self.radius = radius
        self.color = color
        self.texture_low = texture_low
        self.texture_high = texture_high


class Simulation:
    def __init__(self, celestials: tp.List[Celestial], dt: float, g: float = 1):
        self.celestials = celestials
        self.g = g
        self.dt = dt

        self.x = np.asfortranarray(np.array([cel.x for cel in celestials]).T)
        self.v = np.asfortranarray(np.array([cel.v for cel in celestials]).T)
        self.m = np.array([cel.m for cel in celestials], order="F")
        self.a = np.zeros_like(self.x)

        self.min_dist = 1e-4*np.min(self.x)
        self.x_hist = []

    def run(self, steps: int, save_interval: int):
        if steps % save_interval != 0:
            raise ValueError("Steps must be a multiple of the save interval")
        self.x_hist.append(self.x.copy())
        batches = steps // save_interval
        for i in range(batches):
            print("Batch", i, "of", batches)
            core.core.iterate(self.x, self.v, self.a, self.m, self.dt, self.g, self.min_dist, save_interval)
            self.x_hist.append(self.x.copy())

    def print(self):
        print("Start:")
        print("x")
        print(self.x_hist[0].T)
        print("Now:")
        print("x")
        print(self.x.T)
        print("v")
        print(self.v.T)
        print("a")
        print(self.a.T)
