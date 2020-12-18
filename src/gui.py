import typing as tp

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PySide2 import QtCore, QtGui, QtWidgets

from sim import Simulation


class NBodyWidget(gl.GLViewWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("FYS2085 project: Planetary motion")
        self.pos: tp.Optional[gl.GLScatterPlotItem] = None
        self.color = (1, 1, 1, .5)
        # self.create_grids()

        # Apparently setting the default camera position does not work
        # self.setCameraPosition(
        #     # pos=pg.QtGui.QVector3D(10, 10, 10)
        #     distance=1000
        # )

    def create_grids(self, size: float = 1):
        size2 = 4*size
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

    def set_pos(self, pos, color=None, size=None):
        kwargs = {
            "color": color if color is not None else self.color
        }
        if size is not None:
            kwargs["size"] = size
        if self.pos is None:
            self.pos = gl.GLScatterPlotItem(pos=pos, **kwargs)
            self.addItem(self.pos)
        else:
            self.pos.setData(pos=pos, **kwargs)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, sim: Simulation, *args, unit_mult: float = 1, **kwargs):
        super().__init__(*args, **kwargs)

        # UI creation
        self.resize(1280, 720)
        cw = QtWidgets.QWidget()
        self.setCentralWidget(cw)
        layout = QtWidgets.QGridLayout()
        cw.setLayout(layout)

        self.nbody = NBodyWidget()
        layout.addWidget(self.nbody, 0, 0)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        layout.addWidget(self.slider, 1, 0)
        self.slider.sliderMoved.connect(self.redraw)
        self.slider.setRange(1, 50)
        self.slider.setSingleStep(10)
        self.slider.setTickInterval(10)

        # Simulation
        self.sim = sim
        self.unit_mult = unit_mult
        self.colors = np.array([[*cel.color, 0] for cel in sim.celestials])
        self.sizes = 1

        self.nbody.create_grids(1)
        self.nbody.setCameraPosition(distance=1)
        sim_len = len(self.sim.x_hist)
        self.slider.setSliderPosition(0)
        self.slider.setRange(0, sim_len-1)
        self.slider.setRange(0, sim_len-1)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(1)

        self.redraw(0)

    def redraw(self, hist_ind: int):
        x = self.sim.x_hist[hist_ind] / self.unit_mult
        # self.nbody.set_pos(x, color=self.colors, size=self.sizes)
        print(x.T)
        self.nbody.set_pos(x.T)
