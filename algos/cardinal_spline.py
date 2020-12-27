"""
Ce module contient les implémentations naïves des calculs des cardinales splines
"""


def cardinal_spline(k, points, c, u):
    """
    Renvoie la kième cardinale spline (1<= k <= N)
    points est la liste de tous les points d'interpolation
    u est l'échelle de temps (vecteur)
    """
    tangent = [0, 0]
    for i in range(2):
        tangent[i] = (1-c)*(points[i][k+1] - points[i][k-1])/(u[k+1] - u[k-1])
    return tangent