"""
Fichier de test du module d'interfaces GUI tkinter.
"""

import numpy as np
from tkinter import *
from interface.Interface import Interface
from geom_utils.point import Point
from courbes.spline_hermite_cubique import SplineHermiteCubique
from courbes.splines_c2 import SplineC2
from courbes.lagrange import CourbeLagrange


if __name__ == "__main__":
    # Create a few curves
    points = [Point(0, 0), Point(-1, 4), Point(3, 3), Point(4, 7)]

    spline = SplineHermiteCubique(points, np.arange(len(points)), tension=0)
    spline2 = SplineC2(points, np.arange(len(points)))
    lag1 = CourbeLagrange(points, np.arange(len(points)))

    # Create the window and plot the curves
    window = Interface(Tk())
    window.plotter.add_curve(spline)
    window.plotter.add_curve(spline2)
    window.plotter.add_curve(lag1)
    window.plotter.update()
    window.refreshCurvesList()

    # Display the window
    window.mainloop()
