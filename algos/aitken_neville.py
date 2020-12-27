

import copy

"""
Implémente l'algorithme d'Aitken-Neville
(partie 2, question 7: polynomes de Lagrange)
"""


def aitken_neville(pts, tps, t):
    """
    évalue le polynome d'interpolation au temps :param t:
    :param pts: les points d'interpolation (tableau de Point)
    :param tps: les paramètres associés
    :param t: l'instant où l'on évalue
    """
    # nombre de points
    n = len(pts)
    # le triangle de l'algorithme (en réalité un tableau
    # dont les éléments deviennent inutiles au fur et à mesure)
    triangle = copy.deepcopy(pts)
    for k in range(n):
        for i in range(n - k-1):
            p1 = triangle[i]*(tps[i+k+1] - t)/(tps[i+k+1] - tps[i])
            p2 = triangle[i+1]*((t - tps[i])/(tps[i+k+1] - tps[i]))
            triangle[i] = p1 + p2
    return triangle[0]