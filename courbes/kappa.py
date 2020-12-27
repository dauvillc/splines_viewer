import numpy as np
from algos.courbure import courbure


class CourbeKappa:
    """
    Courbure d'une courbe spline de Hermite cubique
    N'est pas un objet Courbe...
    """

    def __init__(self, pts, param_steps, tension):
        """
        :param pts          points de contrôle de la courbe spline de Hermite cubique
        :param param_steps  Itérable tel que len(points) == len(param_steps).
                            Indique les bornes successives des intervalles correspondant
                            à chaque courbe hermite constituant le spline. Classiquement,
                            correspond à une répartition équidistante.
        :param tension      paramètre de tension des tangentes
        """
        self.pts = pts
        self.param_steps = param_steps
        # Estimation des tangeantes (Les extrémités sont approximées par des tangeantes nulles)
        tans = [(pts[1] - pts[0])/(param_steps[1] - param_steps[0])]
        for k in range(1, len(pts) - 1):
            tans.append(
                (pts[k + 1] - pts[k - 1]) * (1 - tension) / (param_steps[k + 1] - param_steps[k - 1]))
        tans.append((pts[-1] - pts[-2])/(param_steps[-1] - param_steps[-2]))
        self.tans = tans

    def trace(self, res):
        """
        Dessine la courbure en un certain nombre de points
        :param res      résolution de la courbure entre deux
                        points d'interpolation
        :return T, C: temps du tracé, et valeurs de la courbure à ces pas de temps
        """
        temps = np.zeros((len(self.param_steps)-1)*res)
        courbe = np.zeros((len(self.pts)-1)*res)
        for i in range(len(self.param_steps)-1):
            lin_steps = np.linspace(self.param_steps[i], self.param_steps[i+1], res)
            for j in range(res):
                temps[i*res + j] = lin_steps[j]
            for n in range(res):
                t = n/res
                courbe[i*res + n] = courbure(self.pts[i], self.pts[i+1], self.tans[i], self.tans[i+1], t)
        return temps, courbe