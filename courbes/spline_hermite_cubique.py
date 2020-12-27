"""
@author Clément Dauvilliers

Implémente les Courbes du type Spline Hermite Cubique.
Voir Courbe pour de plus amples informations sur les courbes.
"""
from builtins import map

import numpy as np
from courbes.courbe import Courbe
from courbes.hermite_cubique import CourbeHermiteCubique
from geom_utils.point import Point, points_to_array
from algos.courbure import courbure


class SplineHermiteCubique(Courbe):
    """
    Une courbe spline hermite cubique est un raccord entre plusieurs courbes
    d'Hermite cubiques telles qu'implémentées par CourbeHermiteCubique.
    Celle-ci permet d'interpoler un nombre quelconque de points ainsi que de
    tangeantes.

    Mode d'emploi:
    Pour créer une spline qui interpole les points [(0, 0), (1, 1), (2, 2)] (oui bon c'est pas ouf mais voilà):
    - Créer le tableau de points: points = [Point(0, 0), Point(1, 1), Point(2, 2)]
    - Créer les bornes du paramètres: par exemple, param_dom = np.linspace(0, 1, 3) pour t entre 0 et 1
    - Créer la courbe: spline = SplineHermiteCubique(points, param_dom, 0.5)
    - Dessiner:
        trace = spline.points(1000)
        plt.plot(trace[0, :], trace[1, :])
    """
    def __init__(self, points, param_steps, **parameters):
        """
        :param points:      Points interpolés par la courbe, sous la forme
                            d'un itérable de Points.
        :param param_steps: Itérable tel que len(points) == len(param_steps).
                            Indique les bornes successives des intervalles correspondant
                            à chaque courbe hermite constituant le spline. Classiquement,
                            correspond à une répartition équidistante.
        :param tension:     Indicates the curve tension.
        :param tangent:   Defines the ends' tangent computation. Can be either "zero" (default) or "approximated".
                            If zero, the end derivatives will be taken null.
                            If approximated, the end derivatives will be taken as the growth rate between
                            the two points at each end.
        """
        self.curve_type = "Cubic Hermite Spline"
        # Liste des courbes hermites constituant la spline totale
        self.courbes = []
        self.params = param_steps
        self.control_points_ = points_to_array(points)

        if "tension" in parameters:
            self.tension = parameters["tension"]
        else:
            self.tension = 0.2

        if "tangent" in parameters:
            self.tangent = parameters["tangent"]
        else:
            self.tangent = "approximated"

        # Estimation des tangeantes (Les extrémités sont approximées par des tangeantes nulles)
        tans = []
        if self.tangent == "approximated":
            tans = [(points[1] - points[0]) / (param_steps[1] - param_steps[0])]
            for k in range(1, len(points) - 1):
                tans.append((points[k + 1] - points[k - 1]) * (1 - self.tension ) / (param_steps[k + 1] - param_steps[k - 1]))
            tans.append((points[-1] - points[-2]) / (param_steps[-1] - param_steps[-2]))
        else:
            tans = [Point(0, 0)]
            for k in range(1, len(points) - 1):
                tans.append((points[k + 1] - points[k - 1]) * (1 - self.tension ) / (param_steps[k + 1] - param_steps[k - 1]))
            tans.append(Point(0, 0))

        # Remembers the tangents for the bending curve
        self.tans = tans

        for k in range(len(points) - 1):
            courbe = CourbeHermiteCubique(points[k], points[k + 1], tans[k], tans[k + 1])
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
        self.__init__(points, self.params, tension=self.tension, tangent=self.tangent)

    def hyperparameters_values(self):
        """
        Returns a map of the curve's parameters along with their values.
        :return:
        """
        return {'tension': self.tension, 'tangent': self.tangent}

    def hyperparameters(self):
        """
        An Hyperparameter is a parameter that controls the curve but isn't a parameter
        of evalutation of the curve (For example: the tension for a cubic hermite spline).
        :return: A map of the parameters and values they can take. When those values are float, a tuple
                    (limit_inf, limit_sup, nb_of_values) is given, otherwise, a tuple of the possible values.
        """
        return {"tension": (0, 1, 20), "tangent": ("zero", "approximated")}
