"""
This is the Python-based main program of planetary-motion.
It offers broader functionality than the pure Fortran version, with the most notable being plotting.
"""

import subprocess
import typing as tp

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PySide2 import QtWidgets

# Compilation is done automatically here to speed up development
print("Compiling Fortran code")
subprocess.run(["./build.sh"], check=True)
print("Fortran code compiled")
print("\n\n")

# Your IDE may complain that the module does not exist, since the generated Python module is found dynamically
import core


class NBodyWidget(gl.GLViewWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("FYS2085 project: Planetary motion")
        self.pos: tp.Optional[gl.GLScatterPlotItem] = None
        self.color = (1, 1, 1, .5)
        self.create_grids()

    def create_grids(self, size: float = 10):
        size2 = 2*size
        vec = pg.QtGui.QVector3D(size2, size2, size2)
        gx = gl.GLGridItem(size=vec)
        gx.rotate(90, 0, 1, 0)
        # gx.translate(-10, 0, 0)
        self.addItem(gx)
        gy = gl.GLGridItem(size=vec)
        gy.rotate(90, 1, 0, 0)
        # gy.translate(0, -10, 0)
        self.addItem(gy)
        gz = gl.GLGridItem(size=vec)
        # gz.translate(0, 0, -10)
        self.addItem(gz)

    def set_pos(self, pos):
        if self.pos is None:
            self.pos = gl.GLScatterPlotItem(pos=pos, color=self.color)
            self.addItem(self.pos)
        else:
            self.pos.setData(pos=pos, color=self.color)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nbody = NBodyWidget()
        self.setCentralWidget(self.nbody)
        self.resize(1280, 720)


class Celestial:
    def __init__(
            self,
            x: tp.Union[np.ndarray, float],
            m: float,
            radius: float,
            color: tp.Tuple[int, int, int],
            reference: "Celestial",
            x_min: float,
            x_max: float,
            texture_low: str = None,
            texture_high: str = None,
    ):
        if isinstance(x, (int, float)):
            self.x = np.array([x, 0, 0])
        else:
            self.x = x
        self.m = m
        self.radius = radius
        self.color = color
        self.texture_low = texture_low
        self.texture_high = texture_high


def main():
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
    print(x)
    print(core.core.iterate.__doc__)
    # core.core.iterate(x, v, a, m, dt, 1)

    print("x")
    print(x)
    print("v")
    print(v)
    print("a")
    print(a)

    app = pg.mkQApp()
    win = MainWindow()
    win.show()
    win.nbody.set_pos(x.T)

    def update():
        core.core.iterate(x, v, a, m, dt, 1)
        win.nbody.set_pos(x.T)

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100)

    app.exec_()


if __name__ == "__main__":
    main()
