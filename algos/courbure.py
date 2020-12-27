#! /usr/bin/env python3

"""
Courbe de la courbure de la courbe spline de Hermite cubique
entre deux points d'interpolation
"""

from algos.casteljau import casteljau
import numpy as np
from geom_utils.point import Point
import matplotlib.pyplot as plt


def first_derivative(p0: Point, p1: Point, m0: Point, m1: Point, t):
    """
    calcule la dérivée première de la paramétrisation
    (c'est un point de R2) à l'instant t
    :param p0   le premier point d'interpolation
    :param p1   le second poitn d'interpolation
    :param m0   tangente au premier point
    :param m1   tangente au second point
    :param t
        l'instant d'évaluation (entre 0 et 1)
    :return     le vecteur de dérivée première sous
                forme d'un tableau numpy [x, y]
    """
    pt0 = m0
    pt1 = p1*3 - m0 - p0*3 - m0
    pt2 = m1
    pts_cntrl = np.array([[pt0.x, pt1.x, pt2.x], [pt0.y, pt1.y, pt2.y]])
    return casteljau(pts_cntrl, t)


def second_derivative(p0: Point, p1: Point, m0: Point, m1: Point, t):
    """
    calcule la dérivée seconde de la paramétrisation
    (c'est un point de R2) à l'instant t
    :param p0   le premier point d'interpolation
    :param p1   le second poitn d'interpolation
    :param m0   tangente au premier point
    :param m1   tangente au second point
    :param t    l'instant d'évaluation (entre 0 et 1)
    :return     le vecteur de dérivée seconde sous
                forme d'un tableau numpy [x, y]
    """
    pt0 = p1*6 - m1*2 - p0*6 - m0*4
    pt1 = m1*4 - p1*6 + p0*6 + m0*2
    pts_cntrl = np.array([[pt0.x, pt1.x], [pt0.y, pt1.y]])
    return casteljau(pts_cntrl, t)


def courbure(p0: Point, p1: Point, m0: Point, m1: Point, t):
    """
    calcule la courbure de la paramétrisation
     à l'instant t
    :param p0: le premier point d'interpolation
    :param p1: le second point d'interpolation
    :param m0: tangente au premier point
    :param m1: tangente au second point
    :param t
        l'instant d'évaluation (entre 0 et 1)
    """
    x_prime = first_derivative(p0, p1, m0, m1, t)
    x_seconde = second_derivative(p0, p1, m0, m1, t)
    concat = np.array([[x_prime[0], x_seconde[0]], [x_prime[1], x_seconde[1]]])
    det = np.absolute(np.linalg.det(concat))
    denom = np.linalg.norm(x_prime)**3
    #Si la dérivée est nulle, je suppose que la courbure aussi...
    if denom == 0:
        return 0
    return det / denom


def trace_courbure(p0, p1, m0, m1, res):
    """
    Affiche la fonction de courbure
    """
    valeurs = []
    for t in np.linspace(0, 1, res):
        valeurs.append(courbure(p0, p1, m0, m1, t))
    plt.plot(np.linspace(0, 1, res), valeurs)
    plt.show()