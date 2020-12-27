"""
@author Clément Dauvilliers

Implémente les Courbes du type Spline Hermite Cubique.
Voir Courbe pour de plus amples informations sur les courbes.
"""
from builtins import map

import numpy as np
from courbes.courbe import Courbe
from courbes.hermite_cubique import CourbeHermiteCubique
from geom_utils.point import Point, points_to_array, from_numpy_array
from algos.courbure import courbure


def compute_derivatives(points):
    """
    Computes the values of the derivative at each parameter that allow
    the total spline to be C2.
    :param points: Interpolation points as a list of Points
    :return: A numpy array D where D[i] is the value for the derivative at parameter t_i.
    """
    # The values are solution of a linear system AD = Y
    # where Yi = 3(Pi+1 - Pi)
    # and       |2 1 0 0 0 |
    #       A = |1 4 1 0 0 |
    #           |0 1 4 1 ..|
    #           |.. ... ...|

    # Create the system's matrix A
    N = len(points) - 2
    main_diag = np.diag([4] * (N + 2))
    main_diag[0, 0], main_diag[N + 1, N + 1] = 2, 2
    lower_diag = np.diag([1] * (N + 1), -1)
    upper_diag = np.diag([1] * (N + 1), 1)
    A = lower_diag + main_diag + upper_diag

    # Create Y
    # Converts the Points list into a numpy array
    interp_points = points_to_array(points)

    # Create Y for the points' first coordinates
    Y1 = np.empty(N + 2)
    Y1[1:-1] = 3 * (interp_points[0, 2:] - interp_points[0, :-2])
    Y1[0] = 3 * (interp_points[0, 1] - interp_points[0, 0])
    Y1[-1] = 3 * (interp_points[0, -1] - interp_points[0, -2])

    # Create Y for the points' second coordinates
    Y2 = np.empty(N + 2)
    Y2[1:-1] = 3 * (interp_points[1, 2:] - interp_points[1, :-2])
    Y2[0] = 3 * (interp_points[1, 1] - interp_points[1, 0])
    Y2[-1] = 3 * (interp_points[1, -1] - interp_points[1, -2])

    # Solve the systems for both coordinates
    D1 = np.linalg.solve(A, Y1)
    D2 = np.linalg.solve(A, Y2)

    # Return the final values
    return np.vstack((D1, D2))


class SplineC2(Courbe):
    """
    Une courbe spline hermite cubique est un raccord entre plusieurs courbes
    d'Hermite cubiques telles qu'implémentées par CourbeHermiteCubique. Le raccord
    est fait de manière à ce que la courbe totale soit de classe C2.
    """
    def __init__(self, points, param_steps, **parameters):
        """
        :param points:      Points interpolés par la courbe, sous la forme
                            d'un itérable de Points.
        :param param_steps: Itérable tel que len(points) == len(param_steps).
                            Indique les bornes successives des intervalles correspondant
                            à chaque courbe hermite constituant le spline. Classiquement,
                            correspond à une répartition équidistante.
        """
        self.curve_type = "C2 Spline"

        # Calcul des dérivées
        derivs = from_numpy_array(compute_derivatives(points))
        # Remembers the derivative's values for the bending curve
        self.tans = derivs

        # Liste des courbes hermites constituant la spline totale
        self.courbes = []
        self.params = param_steps
        self.control_points_ = points_to_array(points)

        # Création des courbes
        for k in range(len(points) - 1):
            courbe = CourbeHermiteCubique(points[k], points[k + 1], derivs[k], derivs[k + 1])
            self.courbes.append(courbe)

    def points(self, res: int):
        """
        Calcule la courbe et renvoie les points calculées sous la forme
        d'une matrice numpy P de dimensions (2, res) où P[:, i] correspond
        au point numéro i.
        :param res  Résolution demandée pour le tracé.
        """
        # Chaque courbe HermiteCubique de self.courbes calcule les points
        # du tracé qu'elle retourne sous la forme d'un tableau numpy de dimensions (2, nb_points).
        # Il suffit de concaténer tous tableau dans le sens des colonnes (axis 1) pour récupérer
        # le tableau de dimensions (2, nb_points_total).
        return np.concatenate([courbe.points(int(res / len(self.courbes))) for courbe in self.courbes], axis=1)

    def plot_bending(self, res):
        """
        Dessine la courbure en un certain nombre de points
        :param res      résolution de la courbure entre deux
                        points d'interpolation
        :return T, C: temps du tracé, et valeurs de la courbure à ces pas de temps
        """
        points = list(self.control_points_as_points())
        temps = np.zeros((len(self.params)-1)*res)
        courbe = np.zeros((len(points)-1)*res)
        for i in range(len(self.params)-1):
            lin_steps = np.linspace(self.params[i], self.params[i+1], res)
            for j in range(res):
                temps[i*res + j] = lin_steps[j]
            for n in range(res):
                t = n/res
                courbe[i*res + n] = courbure(points[i], points[i+1], self.tans[i], self.tans[i+1], t)
        return temps, courbe

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

    def hyperparameters_values(self):
        """
        Returns a map of the curve's parameters along with their values.
        :return:
        """
        return {}

    def hyperparameters(self):
        """
        An Hyperparameter is a parameter that controls the curve but isn't a parameter
        of evalutation of the curve (For example: the tension for a cubic hermite spline).
        :return: A map of the parameters and values they can take. When those values are float, a tuple
                    (limit_inf, limit_sup, nb_of_values) is given, otherwise, a tuple of the possible values.
        """
        return {}
