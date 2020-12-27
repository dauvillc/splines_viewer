"""
Implémente une courbe d'interpolation d'Hermite cubique.
Voir Courbe pour de plus amples informations.
"""


import numpy as np
from algos.casteljau import casteljau
from courbes.courbe import Courbe
from geom_utils.point import Point, points_to_array


class CourbeHermiteCubique(Courbe):
    """
    Une courbe d'Hermite cubique permet d'interpoler deux points P0, P1
    ainsi que leurs tangeantes M0 et M1.
    """
    def __init__(self, p0: Point, p1: Point, m0, m1, param_interval=None):
        """
        :param p0:      Premier point à interpoler.
        :param p1:      Second point à interpoler.
        :param m0:      Première tangeante à interpoler.
        :param m1:      Seconde tangeante à interpoler.
        :param param_interval:      Couple de valeurs (a, b) indiquant
                                    l'intervalle dans lequel se trouve le paramètre de la courbe.
                                    Si celui-ci n'est pas précisé, il sera pris entre 0 (Interpolation de PO)
                                    et 1 (Interpolation de P1).
        """
        self.curve_type = "Hermite Cubic"
        self.p0 = p0.copy()
        self.p1 = p1.copy()
        self.m0 = m0.copy()
        self.m1 = m1.copy()
        self.control_points_ = points_to_array([p0, p1])
        if param_interval is not None:
            self.param_interval = (param_interval[0], param_interval[1])
        else:
            self.param_interval = (0, 1)

        # Calcul des points de Béziers associés à la courbe.
        # Cette implémentation est plus rapide et numériquement plus stable que le
        # calcul direct des polynômes d'Hermite.
        self.bezierPoints = np.array([
            [self.p0[0], self.p0[0] + (1 / 3) * self.m0[0], self.p1[0] - (1 / 3) * self.m1[0], self.p1[0]],
            [self.p0[1], self.p0[1] + (1 / 3) * self.m0[1], self.p1[1] - (1 / 3) * self.m1[1], self.p1[1]]
        ])

    def points(self, res):
        """
        Calcule la courbe et renvoie les points calculées sous la forme
        d'une matrice numpy P de dimensions (2, res) où P[:, i] correspond
        au point numéro i.
        :param res  Résolution demandée pour le tracé.
        """
        # Valeurs du paramètre auxquelles la courbe va être évaluée
        param_vals = np.linspace(*self.param_interval, res)

        # Matrice résultat
        P = np.zeros((2, res))

        # Calcul des points à l'aide de l'algorithme de Casteljau
        for k in range(res):
            # P[:, k] = colonne numéro k de P (et donc le point numéro k)
            P[:, k] = casteljau(self.bezierPoints, param_vals[k])

        return P
