"""
This is the Python-based main program of planetary-motion.
It offers broader functionality than the pure Fortran version, with the most notable being plotting.

It should be noted that specifying the configuration for a Fortran-based simulation as a Python file
is a rather common practice. For other examples please see the CSC cluster configurations in
https://gitlab.com/AgenttiX/fys-4096
"""

import subprocess


import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg


# Compilation is done automatically here to speed up development
print("Compiling Fortran code")
subprocess.run(["make", "all"], check=True)
print("Fortran code compiled")
print("\n\n")

# Your IDE may complain that the module does not exist, since the generated Python module is found dynamically
import core


from sim import Celestial, Simulation, AU, YEAR_IN_D, YEAR_IN_S, G, M_EARTH, ORBIT_R_EARTH, M_SUN, V_EARTH
from gui import MainWindow


# Solar system
# These values are from Wikipedia

sun = Celestial(
    x=0,
    v=0,
    m=M_SUN,
    radius=695700e3,
    color=(255, 230, 0),
)
mercury = Celestial(
    x=57909050e3,
    v=47.362e3,
    m=3.3011e23,
    radius=2439.7e3,
    color=(180, 170, 150),
    reference=sun,
    period=0.240846
)
venus = Celestial(
    x=108208000e3,
    v=35.02e3,
    m=4.8675e24,
    radius=6051.8e3,
    color=(250, 190, 40),
    reference=sun,
    period=0.615198
)
earth = Celestial(
    x=ORBIT_R_EARTH,
    v=V_EARTH,
    m=M_EARTH,
    radius=6371.0e3,
    color=(25, 180, 200),
    reference=sun,
    # Let's ignore all the nasty precession stuff
    period=1
)
moon = Celestial(
    x=384399e3,
    v=1.022e3,
    m=7.342e22,
    radius=1737.4e3,
    color=(160, 160, 160),
    reference=earth,
    period=27.321661 / YEAR_IN_D
)
mars = Celestial(
    x=227949200e3,
    v=24.007e3,
    m=6.4171e23,
    radius=3389.5e3,
    color=(240, 130, 60),
    reference=sun,
    period=1.88082
)
jupiter = Celestial(
    x=778.57e6*1e3,
    v=13.07e3,
    m=1.8982e27,
    radius=69911e3,
    color=(230, 180, 160),
    reference=sun,
    period=11.862
)
saturn = Celestial(
    x=1433.53e6*1e3,
    v=9.68e3,
    m=5.6834e26,
    radius=58232e3,
    color=(220, 220, 130),
    reference=sun,
    period=29.4571
)
uranus = Celestial(
    x=2875.04e6*1e3,
    v=6.8e3,
    m=8.6810e25,
    radius=25362e3,
    color=(140, 240, 220),
    reference=sun,
    period=84.0205
)
# Nep nep!
neptune = Celestial(
    x=30.07*AU,
    v=5.43e3,
    m=1.02413e26,
    radius=24622e3,
    color=(110, 120, 220),
    reference=sun,
    period=164.8
)
solar_system = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]


def show_simulation(sim: Simulation, unit_mult: float = 1):
    sim.print()
    app = pg.mkQApp()
    win = MainWindow(sim, unit_mult=unit_mult)
    win.show()
    app.exec_()


def period_from_crossings(signal, dt):
    """
    Based on
    https://gist.github.com/endolith/255291
    """
    # Find all indices right before a rising-edge zero crossing
    indices = np.nonzero((signal[1:] >= 0) & (signal[:-1] < 0))[0]
    crossings = [i - signal[i] / (signal[i + 1] - signal[i]) for i in indices]
    print(indices)
    print(crossings)
    return dt*np.mean(np.diff(crossings))


def part_1a():
    dts = np.linspace(0.01, 0.1, 20)*YEAR_IN_S
    save_interval = 100
    period_true = 2 * np.pi * jupiter.x[0] / jupiter.v[1] / YEAR_IN_S

    periods = np.zeros_like(dts)
    for i in range(dts.size):
        dt = dts[i]
        sim = Simulation([sun, jupiter], dt=dt, g=G, fix_scale=True)
        # show_simulation(sim, unit_mult=AU)
        sim.run(steps=10000, save_interval=save_interval)
        jupiter_pos = np.array(sim.x_hist)[:, :, 1]
        jupiter_angle = jupiter_pos[:, 1] / jupiter.x[0]
        # t_arr = dt*save_interval*np.arange(len(sim.x_hist)) / YEAR_IN_S
        period = period_from_crossings(jupiter_angle, dt*save_interval) / YEAR_IN_S
        periods[i] = period
        print(f"dt = {dt / YEAR_IN_S} years, true period: {period_true} years, simulated: {period} years")

        # fig: plt.Figure = plt.figure()
        # ax: plt.Axes = fig.add_subplot()
        # ax.plot(t_arr, jupiter_angle)
        # ax.set_xlabel("t (years)")
        # ax.set_ylabel(r"$\sin(\theta)$")

    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_subplot()
    ax.plot(dts / YEAR_IN_S, periods)
    ax.axhline(period_true)
    ax.set_xlabel("Timestep (years)")
    ax.set_ylabel("Period (years)")
    fig.savefig("../report/fig_1a.eps")


def part_1b():
    period_true = 2 * np.pi * jupiter.x[0] / jupiter.v[1] / YEAR_IN_S
    steps = 300
    save_interval = 10
    dt = period_true / steps * YEAR_IN_S
    print("dt", dt / YEAR_IN_S)

    sim = Simulation([sun, jupiter], dt=dt, g=G, fix_scale=True)
    sim.run(steps=steps, save_interval=save_interval)
    jupiter_pos = np.array(sim.x_hist)[:, :, 1]
    jupiter_angle = jupiter_pos[:, 1] / jupiter.x[0]
    # print(jupiter_angle)
    t_arr = dt * save_interval * np.arange(len(sim.x_hist)) / YEAR_IN_S

    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_subplot()
    ax.plot(t_arr, jupiter_angle)
    ax.set_xlabel("t (years)")
    ax.set_ylabel(r"$\sin(\theta)$")

    print(f"Jupiter angle: {np.arcsin(jupiter_angle[-1])*180/np.pi} deg")


def part_3():
    sim = Simulation(solar_system, dt=0.01*YEAR_IN_S, g=G, fix_scale=True)
    sim.run(steps=100, save_interval=1)
    show_simulation(sim, unit_mult=AU)


# def nbody_test():
#     print("Starting")
#     n_objs = 10
#     dt = 0.1
#     # n_iters = 10
#
#     x = np.asfortranarray(2*np.random.rand(3, n_objs) - 1) * 10
#     # v = np.asfortranarray(np.random.rand(3, n_objs))
#     v = np.zeros_like(x)
#     a = np.zeros_like(x)
#     m = np.ones(n_objs, order="F")
#
#     print("x")
#     print(x.T)
#     print(core.core.iterate.__doc__)
#     # core.core.iterate(x, v, a, m, dt, 1)
#
#     app = pg.mkQApp()
#     win = MainWindow()
#     win.show()
#     win.nbody.set_pos(x.T)
#
#     def update():
#         core.core.iterate(x, v, a, m, dt, 1, g=1, min_dist=1)
#         win.nbody.set_pos(x.T)
#
#     timer = pg.QtCore.QTimer()
#     timer.timeout.connect(update)
#     timer.start(100)
#
#     app.exec_()
#
#     print("x")
#     print(x.T)
#     print("v")
#     print(v.T)
#     print("a")
#     print(a.T)


def nbody_test2():
    celestials = [Celestial(
        x=2*np.random.rand(3) - 1,
        v=(2*np.random.rand(3) - 1)*0.1,
        m=1,
        color=tuple(np.random.randint(100, 255, (3,))),
        radius=1
    ) for _ in range(10)]

    sim = Simulation(celestials, dt=0.1, g=1)
    sim.run(steps=10000, save_interval=100)
    show_simulation(sim)


if __name__ == "__main__":
    # nbody_test()
    # nbody_test2()
    # part_1a()
    part_1b()
    # part_3()

    plt.show()
