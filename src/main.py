"""
This is the Python-based main program of planetary-motion.
It offers broader functionality than the pure Fortran version, with the most notable being plotting.

It should be noted that specifying the configuration for a Fortran-based simulation as a Python file
is a rather common practice. For other examples please see the CSC cluster configurations in
https://gitlab.com/AgenttiX/fys-4096
"""

import subprocess


import numpy as np
import pyqtgraph as pg


# Compilation is done automatically here to speed up development
print("Compiling Fortran code")
subprocess.run(["./build.sh"], check=True)
print("Fortran code compiled")
print("\n\n")

# Your IDE may complain that the module does not exist, since the generated Python module is found dynamically
import core


from sim import Celestial, Simulation, AU, YEAR_IN_D, YEAR_IN_S
from gui import MainWindow


# Solar system
# These values are from Wikipedia

sun = Celestial(
    x=0,
    v=0,
    m=1.9885e30,
    radius=695700,
    color=(255, 230, 0),
)
mercury = Celestial(
    x=57909050,
    v=47.362,
    m=3.3011e23,
    radius=2439.7,
    color=(180, 170, 150),
    reference=sun,
    period=0.240846
)
venus = Celestial(
    x=108208000,
    v=35.02,
    m=48675e24,
    radius=6051.8,
    color=(250, 190, 40),
    reference=sun,
    period=0.615198
)
earth = Celestial(
    x=149598023,
    v=29.78,
    m=5972.34e24,
    radius=6371.0,
    color=(25, 180, 200),
    reference=sun,
    # Let's ignore all the nasty precession stuff
    period=1
)
moon = Celestial(
    x=384399,
    v=1.022,
    m=7.342e22,
    radius=1737.4,
    color=(160, 160, 160),
    reference=earth,
    period=27.321661 / YEAR_IN_D
)
mars = Celestial(
    x=227949200,
    v=24.007,
    m=6.4171e23,
    radius=3389.5,
    color=(240, 130, 60),
    reference=sun,
    period=1.88082
)
jupiter = Celestial(
    x=778.57e6,
    v=13.07,
    m=1.8982e27,
    radius=69911,
    color=(230, 180, 160),
    reference=sun,
    period=11.862
)
saturn = Celestial(
    x=1433.53e6,
    v=9.68,
    m=5.6834,
    radius=58232,
    color=(220, 220, 130),
    reference=sun,
    period=29.4571
)
uranus = Celestial(
    x=2875.04e9,
    v=6.8,
    m=8.6810e25,
    radius=25362,
    color=(140, 240, 220),
    reference=sun,
    period=84.0205
)
# Nep nep!
neptune = Celestial(
    x=30.07*AU,
    v=5.43,
    m=1.02413e26,
    radius=24622,
    color=(110, 120, 220),
    reference=sun,
    period=164.8
)
solar_system = [sun, mercury, venus, earth, mars, jupiter, saturn, neptune]


def show_simulation(sim: Simulation):
    sim.print()
    app = pg.mkQApp()
    win = MainWindow(sim)
    win.show()
    app.exec_()


def part_1a():
    sim = Simulation([sun, jupiter], dt=0.1*YEAR_IN_S)
    sim.run(steps=1000, save_interval=100)
    show_simulation(sim)


def nbody_test():
    print("Starting")
    n_objs = 10
    dt = 0.1
    # n_iters = 10

    x = np.asfortranarray(2*np.random.rand(3, n_objs) - 1) * 10
    # v = np.asfortranarray(np.random.rand(3, n_objs))
    v = np.zeros_like(x)
    a = np.zeros_like(x)
    m = np.ones(n_objs, order="F")

    print("x")
    print(x.T)
    print(core.core.iterate.__doc__)
    # core.core.iterate(x, v, a, m, dt, 1)

    app = pg.mkQApp()
    win = MainWindow()
    win.show()
    win.nbody.set_pos(x.T)

    def update():
        core.core.iterate(x, v, a, m, dt, 1, g=1, min_dist=1)
        win.nbody.set_pos(x.T)

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100)

    app.exec_()

    print("x")
    print(x.T)
    print("v")
    print(v.T)
    print("a")
    print(a.T)


if __name__ == "__main__":
    # nbody_test()
    part_1a()
