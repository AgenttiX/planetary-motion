import logging
import typing as tp

import numpy as np

import core

logger = logging.getLogger(__name__)

# Units and constants
# Astronomical unit (in m)
AU = 1.495978707e11
# Gravitational constant
G = 6.67430e-11
# Time
SIDEREAL_MONTH_IN_D = 27.321661
SIDEREAL_MONTH_IN_S = 2360591.5104
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
            color: tp.Tuple[int, int, int] = (0, 0, 0),
            name: str = None,
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
        self.period = period

        self.color = color
        self.name = name
        self.texture_low = texture_low
        self.texture_high = texture_high

    @property
    def color_matplotlib(self) -> tp.Tuple[float, float, float]:
        return self.color[0] / 255, self.color[1] / 255, self.color[2] / 255


class Simulation:
    def __init__(
            self,
            celestials: tp.List[Celestial],
            dt: float,
            g: float = 1,
            fix_scale: bool = False,
            # Center-of-momentum frame
            com_frame: bool = True):
        self.celestials = celestials
        self.g = g
        self.dt = dt
        self.fix_scale = fix_scale
        self.com_frame = com_frame

        # Indices: (dim, celestial)
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

            self.g = G * AU**-3 * M_EARTH * YEAR_IN_S**2
            g_check = M_EARTH / M_SUN * (V_EARTH * YEAR_IN_S / AU)**2
            if not np.isclose(self.g, g_check, rtol=1e-3):
                logger.debug("G (value): %s", self.g)
                logger.debug("G (from Solar system): %s", g_check)
                raise ValueError("G does not correspond to the values of the Solar system.")

            # print("Periods in years")
            # print(2*np.pi*self.x[0, :] / self.v[1, :])

        if self.com_frame:
            total_m = np.sum(self.m)
            total_p = np.sum(self.m * self.v, axis=1)
            self.v = (self.v.T - total_p.T / total_m).T
            print("Total momentum:", np.sum(self.m * self.v, axis=1))
            center_of_mass = np.sum(self.m * self.x, axis=1) / total_m
            self.x = (self.x.T - center_of_mass).T
            print("Center of mass:", np.sum(self.m * self.x, axis=1) / total_m)

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

    def run(self, steps: int, save_interval: int, use_rk4: bool = False):
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
            if use_rk4:
                core.core.iterate_rk4(
                    self.x, self.v, self.a, self.m, self.dt,
                    n_steps=save_interval,
                    g=self.g,
                    min_dist=self.min_dist)
            else:
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
