"""
Defines the Point object.
"""


import numpy as np
from itertools import tee


def pairs(iterable):
    """
    Iterates over the pairs of an iterable.
    For an iterable (A, B, C, D), returns (A, B); then (C, D)...
    The iterable must contain an even positive number of elements.
    """
    k0 = 0
    while k0 <= len(iterable) - 2:
        yield iterable[k0], iterable[k0 + 1]
        k0 += 2


def points_to_array(point_array):
    """
    Converts an array of Points into a 2D numpy array
    of shape (2, number of points).
    :param point_array: Iterable of Points
    :return: a ndarray N such that N[:, i] = points_array[i]
    """
    res_array = np.empty((2, len(point_array)))
    for k, point in enumerate(point_array):
        res_array[:, k] = (point.x, point.y)
    return res_array


def from_numpy_array(np_array):
    """
    Converts a 2D numpy array N of shape (2, nb_points) into a list
    of Points
    :return: A list of Points P so that P[i] == Point(column i)
    """
    pts_list = []
    for k in range(np_array.shape[1]):
        pts_list.append(Point(np_array[0, k], np_array[1, k]))
    return pts_list


def from_string(coordinates):
    """
    Creates a list of Points from a string containing its coordinates.
    :param coordinates: String indicating the coordinates.
    Must match the form: x0 y0 x1 y1 ..
    For example, points (0, 3) and (1, 2) are written "0 3 1 2".
    :return: A list of Points with the corresponding coordinate
    """
    points = []
    coords_char = coordinates.split()

    # Check that an even number of coordinates was received
    if len(coords_char) % 2 != 0:
        raise IndexError("Missing coordinate")

    for x, y in pairs(coords_char):
        points.append(Point(float(x), float(y)))
    return points


class Point:
    """
    A point is a couple of real coordinates, which can be added to another point,
    substracted from another point, multiplied by a real value.
    """

    def __init__(self, x, y):
        self.x, self.y = x, y

    def copy(self):
        """
        Returns a deep copy of this point
        """
        return Point(self.x, self.y)

    def __getitem__(self, item):
        if not 0 <= item <= 1:
            raise IndexError("Tentative d'accès à la coordonnée " + str(item) + " d'un point")
        else:
            if item == 0:
                return self.x
            else:
                return self.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def times(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __repr__(self):
        return str(self)
