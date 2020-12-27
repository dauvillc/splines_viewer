"""
Implémente la classe générique Courbe.
"""


import numpy as np
from geom_utils.point import Point


class Courbe:
    """
    Une Courbe représente une courbe paramétrée qui doit nécessairement pouvoir:
    - être contenue, c'est-à-dire comprendre une structure de données qui définit pleinement
      la courbe ET ses paramètres.
    - être calculée: la Courbe doit nécessairement implémenter la méthode points() pour
      permettre à un agent externe de la tracer.
    """
    def __init__(self, points, **parameters):
        """
        :param points   Itérable contenant des couples (x, y) définissant les points
                        associés à la courbe.
        :param parameters Paramètres supplémentaires de la courbe (dépend du type de courbe).
        ACTUELLEMENT NON IMPLEMENTEE (Voir  SplineHermiteCubique)
        """
        self.curve_type = "none"

    def points(self, res: int) -> np.ndarray:
        """
        Calcule la courbe et renvoie les points calculées sous la forme
        d'une matrice numpy P de dimensions (2, res) où P[:, i] correspond
        au point numéro i.
        :param res  Résolution demandée pour le tracé.
        """
        pass

    def get_type(self):
        """
        :return: The type of this curve as a string.
        """
        return self.curve_type

    def control_points(self):
        """
        :return: The curve's control points as a 2D numpy array
                  of shape (2, number of points).
        """
        return self.control_points_

    def control_points_as_points(self):
        """
        Iterates over this curve's control points as Point objects
        """
        for k in range(self.control_points_.shape[1]):
            yield Point(self.control_points_[0, k], self.control_points_[1, k])

    def hyperparameters_values(self):
        """
        Returns a map of this curve's parameters names associated to their values.
        """
        return {}

    def hyperparameters(self):
        """
        An Hyperparameter is a parameter that controls the curve but isn't a parameter
        of evalutation of the curve (For example: the tension for a cubic hermite spline).
        :return: A dictionnary D = {name_of_parameter: (min_val, max_val)}
        """
        return {}

    def set_parameter_value(self, parameter_name, value: float):
        """
        Sets a value for a given parameter of the curve.
        :param parameter_name Name of the parameter
        :param value New value for the parameter.
        """
        init_params = self.hyperparameters_values()
        init_params[parameter_name] = value
        self.__init__(list(self.control_points_as_points()), self.params, **init_params)