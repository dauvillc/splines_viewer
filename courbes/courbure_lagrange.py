import numpy as np
import matplotlib.pyplot as plt
from geom_utils.point import Point

"""
Coubure d'un polynôme de Lagrange.
N'est PAS un objet Courbe
"""

class CourbureLagrange:

    def __init__(self, pts, param_steps):
        """
        :param pts          points d'interpolation
        :param param_steps  paramètres associés
        """
        self.pts = pts
        self.steps = param_steps

    def first_derivative(self, t):
        """
        Calcule la dérivée première du polynôme en l'instant t.
        La renvoie sous forme d'un tableau numpy [x, y]
        :param t       instant d'évaluation
        :return        la dérivée première
        """
        somme_i = Point(0, 0)
        n = len(self.pts)
        for i in range(n):
            somme_j = 0
            for j in range(n):
                produit = 1
                if j != i:
                    for k in range(n):
                        if k!=j and k!=i:
                            produit *= (t-self.steps[k])/(self.steps[i]-self.steps[k])
                    produit *= 1 / (self.steps[i] - self.steps[j])
                    somme_j += produit
            somme_i += self.pts[i]*somme_j
        return np.array([somme_i.x, somme_i.y])

    def second_derivative(self, t):
        """
        Calcule la dérivée seconde du polynôme en l'instant t.
        La renvoie sous forme d'un tableau numpy [x, y]
        :param t       instant d'évaluation
        :return        la dérivée seconde
        """
        somme_i = Point(0, 0)
        n = len(self.pts)
        for i in range(n):
            somme_j = 0
            for j in range(n):
                somme_k = 0
                if j != i:
                    for k in range(n):
                        produit = 1
                        if k!=j and k!=i:
                            for p in range(n):
                                if p!=i and p!=j and p!=k:
                                    produit *= (t-self.steps[p])/(self.steps[i] - self.steps[p])
                            produit*= 1/(self.steps[i] - self.steps[k])
                            somme_k += produit
                    somme_j += somme_k*(1/(self.steps[i] - self.steps[j]))
                somme_i += self.pts[i]*somme_j
        return np.array([somme_i.x, somme_i.y])

    def trace(self, res):
        """
        Renvoie la liste des temps d'évaluation de la courbure
        et des valeurs associées, sous la forme de deux tableaux
        :return     les temps, les valeurs
        """
        temps = []
        courbe = []
        for i in range(len(self.steps)-1):
            for t in np.linspace(self.steps[i], self.steps[i+1], res):
                temps.append(t)
                x_prime = self.first_derivative(t)
                x_seconde = self.second_derivative(t)
                concat = np.array([[x_prime[0], x_seconde[0]], [x_prime[1], x_seconde[1]]])
                det = np.absolute(np.linalg.det(concat))
                denom = np.linalg.norm(x_prime)**3
                if denom == 0:
                    courbe.append(0)
                else:
                    courbe.append(det/denom)
        return temps, courbe