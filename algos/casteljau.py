"""
Defines the Casteljau algorithm.
"""


def casteljau(points, t):
    """
    Evalue la courbe de Bézier associées aux points de contrôle :param points: à la valeur
    :param t: du paramètre.
    :param points: Points de contrôle de la courbe, sous la forme d'un tableau numpy
                   de dimension (2, N) où chaque colonne est un point.
    :param t:      Valeur du paramètre (entre 0 et 1) à laquelle évaluer la courbe.
    :return        Le point résultant du calcul sous forme d'un tableau numpu [x, y]
    """
    n = points.shape[1]
    if n == 1:
        return points[:, 0]
    else:
        new_points = (1 - t) * points[:, :n-1] + t * points[:, 1:]
        return casteljau(new_points, t)