"""
Defines the Lagrange interpolation curve.
"""


import numpy as np
from courbes.courbe import Courbe
from algos.aitken_neville import aitken_neville
from geom_utils.point import points_to_array, from_numpy_array, Point
from courbes.courbure_lagrange import CourbureLagrange


class CourbeLagrange(Courbe):
    """
    Polynome de degré n interpolant n points
    """
    def __init__(self, points, params):
        """
        :param points: les points d'interpolation (tableau de Point)
        :param params: les paramètres associés
        :param res: résolution de la courbe entre deux points
        (P(ti) = Pi)
        """
        super().__init__(points)
        self.curve_type = "Lagrange Interpolation Curve"
        self.control_points_ = points_to_array(points)
        self.params = params

    def points(self, res=100):
        """
        Calcule tous les points de la courbe polynomiale
        selon la résolution et les renvoie dans une matrice
        de taille 2xn
        """
        points = np.zeros((2, res+1))
        for k in range(res + 1):
            alpha = k/res
            t = (1 - alpha)*self.params[0] + alpha*self.params[-1]
            eval_en_t = aitken_neville(from_numpy_array(self.control_points_), self.params, t)
            points[:, k] = [eval_en_t[0], eval_en_t[1]]
        return points

    def plot_bending(self, res):
        """
        Renvoie la liste des temps d'évaluation de la courbure
        et des valeurs associées, sous la forme de deux tableaux
        :return     les temps, les valeurs
        """
        return CourbureLagrange(list(self.control_points_as_points()), self.params).trace(res)

    def set_control_point(self, pt_index, value: Point):
        """
        Modifies the value of the (pt_index)th control point.
        Implies recomputing the whole curve.
        :param pt_index: Index of the control point to modify
                         in self.control_points()
        :param value:    new value for the control point
        """
        # Get the current control points
        points = list(self.control_points_as_points())
        # Replace the value for the aimed control point
        points[pt_index] = value
        # Recreate the curve with the new control points
        self.__init__(points, self.params)
