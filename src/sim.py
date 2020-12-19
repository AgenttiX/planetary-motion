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
YEAR_IN_S = 31557600
# Scaling
M_SUN = 1.9885e30
M_EARTH = 5.97234e24
ORBIT_R_EARTH = 149598023e3
V_EARTH = 29.78e3


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
    def __init__(self, celestials: tp.List[Celestial], dt: float, g: float = 1, fix_scale: bool = False):
        self.celestials = celestials
        self.g = g
        self.dt = dt
        self.fix_scale = fix_scale

        self.x = np.asfortranarray(np.array([cel.x for cel in celestials]).T)
        self.v = np.asfortranarray(np.array([cel.v for cel in celestials]).T)
        self.m = np.array([cel.m for cel in celestials], order="F")
        self.a = np.zeros_like(self.x)

        # The simulation did not work with the astrophysical values,
        # probably due to some floating-point errors, so this conversion was added as a fix.
        if self.fix_scale:
            self.dt /= YEAR_IN_S
            self.x /= AU
            self.v *= YEAR_IN_S / AU
            self.m /= M_EARTH

            # This is an ugly hack but I'm in a hurry and for some reason
            # cannot figure out how to convert the gravitational
            # constant properly. (It should be trivial.)
            # self.g = 1.195e-4
            self.g = M_EARTH / M_SUN * (V_EARTH * YEAR_IN_S / AU)**2

            # print("Periods in years")
            # print(2*np.pi*self.x[0, :] / self.v[1, :])

        self.min_dist = 1e-4*np.min(np.abs(self.x))
        self.x_hist = []

        # print("SIMULATION LOAD")
        # print("dt", self.dt)
        # print("g", self.g)
        # print("x")
        # print(self.x.T)
        # print("v")
        # print(self.v.T)
        # print("a")
        # print(self.a.T)
        # print("m")
        # print(self.m.T)
        # print("LOAD DEBUG PRINT END")

    def run(self, steps: int, save_interval: int):
        if steps % save_interval != 0:
            raise ValueError("Steps must be a multiple of the save interval")
        start_x = self.x.copy()
        if self.fix_scale:
            start_x *= AU
        self.x_hist.append(start_x)
        batches = steps // save_interval
        self.print()
        for i in range(batches):
            print("Batch", i, "of", batches)
            core.core.iterate(
                self.x, self.v, self.a, self.m, self.dt,
                n_steps=save_interval,
                g=self.g,
                min_dist=self.min_dist)
            new_x = self.x.copy()
            if self.fix_scale:
                new_x *= AU
            self.x_hist.append(new_x)

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
