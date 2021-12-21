"""
This is the Python-based main program of planetary-motion.
It offers broader functionality than the pure Fortran version, with the most notable being plotting.

It should be noted that specifying the configuration for a Fortran-based simulation as a Python file
is a rather common practice. For other examples please see the CSC cluster configurations in
https://gitlab.com/AgenttiX/fys-4096
"""

import logging
import os.path
import subprocess
import time
import typing as tp

import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg

log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_path, exist_ok=True)
logging.basicConfig(
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_path, "log_{}.txt".format(time.strftime("%Y-%m-%d_%H-%M-%S"))))
    ],
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s"
)
logging.getLogger("OpenGL").setLevel(logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# Compilation is done automatically here to speed up development
print("Compiling Fortran code")
subprocess.run(["make", "all"], check=True)
print("Fortran code compiled")
print("\n\n")

# Your IDE may complain that the module does not exist, since the generated Python module is found dynamically
import core


import sim
from gui import MainWindow


# Solar system
# These values are from Wikipedia

sun = sim.Celestial(
    name="Sun",
    x=0,
    v=0,
    m=sim.M_SUN,
    radius=695700e3,
    color=(255, 230, 0),
)
mercury = sim.Celestial(
    name="Mercury",
    x=57909050e3,
    v=47.362e3,
    m=3.3011e23,
    radius=2439.7e3,
    color=(180, 170, 150),
    reference=sun,
    period=0.240846
)
venus = sim.Celestial(
    name="Venus",
    x=108208000e3,
    v=35.02e3,
    m=4.8675e24,
    radius=6051.8e3,
    color=(250, 190, 40),
    reference=sun,
    period=0.615198
)
earth = sim.Celestial(
    name="Earth",
    x=sim.ORBIT_R_EARTH,
    v=sim.V_EARTH,
    m=sim.M_EARTH,
    radius=6371.0e3,
    color=(25, 180, 200),
    reference=sun,
    # Let's ignore all the nasty precession stuff.
    period=1
)
moon = sim.Celestial(
    name="Moon",
    x=384399e3,
    v=1.022e3,
    m=7.342e22,
    radius=1737.4e3,
    color=(160, 160, 160),
    reference=earth,
    period=27.321661 / sim.YEAR_IN_D
)
mars = sim.Celestial(
    name="Mars",
    x=227949200e3,
    v=24.007e3,
    m=6.4171e23,
    radius=3389.5e3,
    color=(240, 130, 60),
    reference=sun,
    period=1.88082
)
jupiter = sim.Celestial(
    name="Jupiter",
    x=778.57e6*1e3,
    v=13.07e3,
    m=1.8982e27,
    radius=69911e3,
    color=(230, 180, 160),
    reference=sun,
    period=11.862
)
saturn = sim.Celestial(
    name="Saturn",
    x=1433.53e6*1e3,
    v=9.68e3,
    m=5.6834e26,
    radius=58232e3,
    color=(220, 220, 130),
    reference=sun,
    period=29.4571
)
uranus = sim.Celestial(
    name="Uranus",
    x=2875.04e6*1e3,
    v=6.8e3,
    m=8.6810e25,
    radius=25362e3,
    color=(140, 240, 220),
    reference=sun,
    period=84.0205
)
# Nep nep!
neptune = sim.Celestial(
    name="Neptune",
    x=30.07*sim.AU,
    v=5.43e3,
    m=1.02413e26,
    radius=24622e3,
    color=(110, 120, 220),
    reference=sun,
    period=164.8
)
solar_system = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]


# Utility methods

def period_from_crossings(signal: np.ndarray, dt: float) -> float:
    """
    Based on
    https://gist.github.com/endolith/255291
    """
    # Find all indices right before a rising-edge zero crossing
    indices = np.nonzero((signal[1:] >= 0) & (signal[:-1] < 0))[0]
    crossings = [i - signal[i] / (signal[i + 1] - signal[i]) for i in indices]
    logger.debug("Crossing indices: %s", indices)
    logger.debug("Crossings: %s", crossings)
    return dt*np.mean(np.diff(crossings))


def period_from_pos(pos: np.ndarray, dt: float, save_interval: int) -> float:
    sin = sin_from_pos(pos)
    return period_from_crossings(sin, dt * save_interval) / sim.YEAR_IN_S


def plot_object(pos: np.ndarray, ax: plt.Axes = None):
    if ax is None:
        fig: plt.Figure = plt.figure()
        ax: plt.Axes = fig.add_subplot()
    ax.plot(pos[:, 0], pos[:, 1])
    return ax


def plot_system(objects: tp.List[sim.Celestial], pos: np.ndarray, ax: plt.Axes = None, log: bool = False) -> plt.Axes:
    if ax is None:
        fig: plt.Figure = plt.figure()
        ax: plt.Axes = fig.add_subplot()
    for i, obj in enumerate(objects):
        ax.plot(pos[:, 0, i] / sim.AU, pos[:, 1, i] / sim.AU, color=obj.color_matplotlib, label=obj.name)
    if log:
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.set_xlabel("x (AU)")
    ax.set_ylabel("y (AU)")
    ax.legend()
    return ax


def show_simulation(sim: sim.Simulation, unit_mult: float = 1):
    sim.print()
    app = pg.mkQApp()
    win = MainWindow(sim, unit_mult=unit_mult)
    win.show()
    app.exec()


def sin_from_pos(pos: np.ndarray) -> np.ndarray:
    arr = pos[:, 1] / np.linalg.norm(pos, axis=1)

    # Replace possible nan values from the ends with the nearest values
    # https://stackoverflow.com/a/9537766/
    ind = np.where(~np.isnan(arr))[0]
    first, last = ind[0], ind[-1]
    arr[:first] = arr[first]
    arr[last + 1:] = arr[last]

    if np.any(np.isnan(arr)):
        raise ValueError("The computed sines should not contain nan values.")
    return arr


# Problem solutions

def simulate_binary_pair(
        name: str,
        center: sim.Celestial,
        satellite: sim.Celestial,
        dts: np.ndarray,
        period_true: float,
        save_interval: int = 100,
        steps: int = 10000
):
    periods = np.zeros_like(dts)
    periods_center = np.zeros_like(dts)
    radii_center_au = []

    for i in range(dts.size):
        dt = dts[i]
        simulation = sim.Simulation([center, satellite], dt=dt, g=sim.G, fix_scale=True)
        # show_simulation(sim, unit_mult=AU)
        simulation.run(steps=steps, save_interval=save_interval)
        satellite_pos = np.array(simulation.x_hist)[:, :, 1]
        satellite_angle = sin_from_pos(satellite_pos)
        center_pos = np.array(simulation.x_hist)[:, :, 0]
        center_angle = sin_from_pos(center_pos)
        # t_arr = dt*save_interval*np.arange(len(sim.x_hist)) / sim.YEAR_IN_S
        period = period_from_crossings(satellite_angle, dt * save_interval) / sim.YEAR_IN_S
        period_center = period_from_crossings(center_angle, dt * save_interval) / sim.YEAR_IN_S
        periods[i] = period
        periods_center[i] = period_center
        radii_center_au.append(np.linalg.norm(center_pos, axis=1) / sim.AU)
        logger.debug("dt = %s years", dt / sim.YEAR_IN_S)
        logger.debug("True period: %s years", period_true)
        logger.debug("Simulated period: %s years", period)

        # fig: plt.Figure = plt.figure()
        # ax: plt.Axes = fig.add_subplot()
        # ax.plot(t_arr, satellite_angle)
        # ax.set_xlabel("t (years)")
        # ax.set_ylabel(r"$\sin(\theta)$")

        # plot_system(pos, ax)

    fig1: plt.Figure = plt.figure()
    fig1_log: plt.Figure = plt.figure()
    ax1: plt.Axes = fig1.add_subplot()
    ax1_log: plt.Axes = fig1_log.add_subplot()
    for ax in (ax1, ax1_log):
        ax.plot(dts / sim.YEAR_IN_S, periods, label=f"simulated, {satellite.name}")
        ax.plot(dts / sim.YEAR_IN_S, periods_center, label=f"simulated, {center.name}", ls="--")
        ax.axhline(period_true, color="green", label="true", alpha=0.5)
        ax.set_xlabel("Timestep (years)")
        ax.set_ylabel("Period (years)")
        ax.legend()
    ax1_log.set_yscale("log")

    fig1.savefig(f"../report/fig_{name}_1.eps")
    fig1_log.savefig(f"../report/fig_{name}_1_log.eps")

    fig2: plt.Figure = plt.figure()
    ax2: plt.Axes = fig2.add_subplot()
    ax2.plot(dts / sim.YEAR_IN_S, np.abs(periods - period_true), label=satellite.name)
    ax2.plot(dts / sim.YEAR_IN_S, np.abs(periods_center - period_true), label=center.name, ls="--")
    ax2.set_yscale("log")
    ax2.set_xlabel("Timestep (years)")
    ax2.set_ylabel("Relative difference from real period (log, yr)")
    ax2.legend()
    fig2.savefig(f"../report/fig_{name}_2.eps")

    fig3: plt.Figure = plt.figure()
    ax3: plt.Axes = fig3.add_subplot()
    ax3.errorbar(
        dts / sim.YEAR_IN_S,
        np.mean(radii_center_au, axis=1) * sim.AU,
        yerr=np.std(radii_center_au, axis=1) * sim.AU,
        fmt=".",
        capsize=3
    )
    ax3.set_xlabel("Timestep (years)")
    ax3.set_ylabel(f"Radius of the motion of {center.name} (m)")
    fig3.savefig(f"../report/fig_{name}_3.eps")

    logger.debug("Periods (%s): %s", center.name, periods_center)


def part_1ac():
    dts = np.linspace(0.01, 0.1, 100)*sim.YEAR_IN_S
    period_true = 2 * np.pi * jupiter.x[0] / jupiter.v[1] / sim.YEAR_IN_S
    simulate_binary_pair(name="1a", center=sun, satellite=jupiter, dts=dts, period_true=period_true)


def part_1b():
    period_true = 2 * np.pi * jupiter.x[0] / jupiter.v[1] / sim.YEAR_IN_S
    steps_arr = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    # save_interval = 10

    angles = []
    angles_sun = []
    t_arrs = []
    dts = []

    n = len(steps_arr)
    for i, steps in enumerate(steps_arr):
        dt = period_true / steps * sim.YEAR_IN_S
        dts.append(dt)
        logger.debug("dt: %s years", dt / sim.YEAR_IN_S)
        save_interval = max(1, steps // 100)

        simulation = sim.Simulation([sun, jupiter], dt=dt, g=sim.G, fix_scale=True)
        simulation.run(steps=steps, save_interval=save_interval)
        jupiter_pos = np.array(simulation.x_hist)[:, :, 1]
        jupiter_angle = jupiter_pos[:, 1] / jupiter.x[0]
        sun_pos = np.array(simulation.x_hist)[:, :, 0]
        sun_angle = sun_pos[:, 1] / np.linalg.norm(sun_pos[:, :], axis=1)
        # print(jupiter_angle)
        t_arr = dt * save_interval * np.arange(len(simulation.x_hist)) / sim.YEAR_IN_S
        angles.append(jupiter_angle)
        angles_sun.append(sun_angle)
        t_arrs.append(t_arr)

    part1b_plot(steps_arr, t_arrs, angles)


def part1b_plot(steps_arr, t_arrs, angles):
    n = len(steps_arr)

    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_subplot()
    cmap = matplotlib.cm.get_cmap("Spectral")
    for i, (steps, t_arr, angle) in enumerate(zip(steps_arr, t_arrs, angles)):
        ax.plot(t_arr, angle, label=f"n={steps}", color=cmap(i/n))
    ax.set_xlabel("t (years)")
    ax.set_ylabel(r"$\sin(\theta)$")
    ax.legend(prop={"size": 6})

    final_angles_rad = np.arcsin([angle[-1] for angle in angles])*180/np.pi
    for (steps, angle) in zip(steps_arr, final_angles_rad):
        logger.debug("Steps: %s, Jupiter angle: %s deg", steps, angle)

    fig2: plt.Figure = plt.figure()
    ax2: plt.Axes = fig2.add_subplot()
    ax2.plot(steps_arr, -final_angles_rad)
    ax2.set_xlabel("steps")
    ax2.set_ylabel("Final angle (-1*deg, log)")
    ax2.set_xscale("log")
    ax2.set_yscale("log")

    fig.savefig("../report/fig_1b_1.eps")
    fig2.savefig("../report/fig_1b_2.eps")


def part_2a():
    dts = np.linspace(1e-4, 0.05, 100)*sim.YEAR_IN_S
    simulate_binary_pair(name="2a", center=sun, satellite=earth, dts=dts, period_true=1)


def part_2b():
    dts = np.linspace(1e-4, 0.05, 100) * sim.SIDEREAL_MONTH_IN_S
    simulate_binary_pair(name="2b", center=earth, satellite=moon, dts=dts, period_true=sim.SIDEREAL_MONTH_IN_S/sim.YEAR_IN_S)


def part_3(use_rk4: bool = False, plot: bool = True, interactive: bool = False):
    dts = np.logspace(-4, -1, 50) * sim.YEAR_IN_S
    periods = np.zeros((len(solar_system), len(dts)))
    save_interval = 10
    for i, dt in enumerate(dts):
        simulation = sim.Simulation(solar_system, dt=dt, g=sim.G, fix_scale=True)
        # For faster simulations use 10**5.
        simulation.run(steps=10**6, save_interval=save_interval, use_rk4=use_rk4)
        x_hist = np.array(simulation.x_hist)

        if i == 3:
            ax = plot_system(solar_system, x_hist)
            ax.set_title(f"dt = {dt}")

            # 3D analysis
            if interactive:
                show_simulation(simulation, unit_mult=sim.AU)

        for j in range(len(solar_system)):
            periods[j, i] = period_from_pos(x_hist[:, :, j], dt=dt, save_interval=save_interval)

    if plot:
        part3_plot(dts, periods, use_rk4)
        part3_plot(dts, periods, use_rk4, 1e-2 * sim.YEAR_IN_S)


def part3_plot(dts: np.ndarray, periods: np.ndarray, use_rk4: bool, cut: float = None):
    if cut:
        inds = dts < cut
        dts = dts[inds]
        periods = periods[:, inds]

    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_subplot()
    fig2: plt.Figure = plt.figure()
    ax2: plt.Axes = fig2.add_subplot()
    for i, obj in enumerate(solar_system[1:]):
        j = i+1
        print("dts", dts)
        print("periods:", periods[j, :])
        ax.plot(dts / sim.YEAR_IN_S, periods[j, :], label=obj.name, color=obj.color_matplotlib)
        ax2.plot(dts / sim.YEAR_IN_S, periods[j, :] / obj.period, label=obj.name, color=obj.color_matplotlib)

    ax.set_xlabel("dt (yr)")
    ax2.set_xlabel("dt (yr)")
    ax.set_ylabel("Period (yr)")
    ax2.set_ylabel("Ratio of simulated and real periods")
    ax.set_xscale("log")
    ax2.set_xscale("log")
    if not cut:
        ax.axvline(0.06, ls="--", color="black")
        ax2.axvline(0.06, ls="--", color="black")
        ax.set_yscale("log")
        ax2.set_yscale("log")
    ax.legend()
    ax2.legend()

    mode_text = "_rk4" if use_rk4 else ""
    cut_text = "_cut" if cut else ""
    try:
        fig.savefig(f"../report/fig_3_abs{mode_text}{cut_text}.eps")
        fig2.savefig(f"../report/fig_3_rel{mode_text}{cut_text}.eps")
    except ValueError as e:
        logger.exception(e)


# This is an earlier nbody version that does not work at the moment but is left here for reference.
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
    celestials = [sim.Celestial(
        x=2*np.random.rand(3) - 1,
        v=(2*np.random.rand(3) - 1)*0.1,
        m=1,
        color=tuple(np.random.randint(100, 255, (3,))),
        radius=1
    ) for _ in range(10)]

    simulation = sim.Simulation(celestials, dt=1e-3, g=1e-3, fix_scale=False, com_frame=True)
    simulation.run(steps=10**6, save_interval=100)

    # 3D analysis
    show_simulation(simulation)


if __name__ == "__main__":
    part_1ac()
    part_1b()
    part_2a()
    part_2b()
    part_3()
    part_3(use_rk4=True)

    # 3D visualizations
    # nbody_test2()
    # part_3(interactive=True, plot=False)

    plt.show()
