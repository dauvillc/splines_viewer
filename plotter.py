"""
Implémente la classe Plotter permettant la gestion des courbes affichées.
"""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from courbes.courbe import Courbe
from geom_utils.point import Point
from courbes.kappa import CourbeKappa


class Plotter:
    """
    Un Plotter est une structure permettant d'enregistrer des courbes paramétriques,
    de les tracer, ainsi que de gérer certaines fonctionnalités comme effacer certaines
    courbes.
    Une courbe paramétrique est représentée par un objet du type Courbe.
    """

    def __init__(self):
        # Dictionnaire (id_courbe, courbe). L'ID d'une courbe est un string concaténation du
        # type de courbe et de son numéro dans le dictionnaire
        self.courbes_ = dict()

        # Mémoire cache permettant de ne pas recalculer les courbes inchangées à chaque update.
        # self.cache[curve_id] contient le tableau numpy correspondant aux points de la courbe
        self.cache = dict()
        self.fig, self.axs = plt.subplots()

        # Résolution par défault de tracé
        self.res = 100

        # Courbe sélectionnée
        self.selected_curve, self.selected_curve_id = None, None

        # Référence vers le point de contrôle sélectionné lors d'un Drag & Drop
        self.picked_ctrl_point = None

        # Rayon maximum pour le picking d'un objet
        self.axs.get_xaxis().set_pickradius(0.01)
        self.axs.get_yaxis().set_pickradius(0.01)

    def update(self):
        """
        Met à jour l'affichage des courbes, et des points de contrôle.
        """
        self.axs.clear()

        # Dessin des courbes
        for curve_id in self.courbes_.keys():
            # Si les points de la courbe sont déjà dans le cache, on
            # les affichent
            if curve_id in self.cache:
                points = self.cache[curve_id]
                self.axs.plot(points[0, :], points[1, :])
            else:
                # Si les points ne sont pas dans le cache, il faut les
                # recalculer.
                resolution = len(list(self.selected_curve.control_points_as_points())) * 30
                points = self.courbes_[curve_id].points(resolution)
                self.cache[curve_id] = points
                self.axs.plot(points[0, :], points[1, :])

        # Dessin des points de contrôle de la courbe sélectionnée
        if self.selected_curve is not None:
            for index, pt in enumerate(self.selected_curve.control_points_as_points()):
                style = "ro"
                if self.picked_ctrl_point is not None and index == self.picked_ctrl_point:
                    style = "bo"
                # Dessine le point de contrôle en question, et récupère l'objet Line2D associé
                drawn_point, = self.axs.plot([pt[0]], [pt[1]], style)
                # Permet la possibilité de pick le point en cliquant dans un rayon de 5 pixels autour
                drawn_point.set_picker(True)
                drawn_point.set_pickradius(5)

    def plot_bending(self):
        """
        Shows the bending of the currently selected curve.
        """
        if self.selected_curve is None:
            return
        self.axs.clear()
        timesteps, values = self.selected_curve.plot_bending(self.res)
        self.axs.plot(timesteps, values)

    def add_curve(self, curve: Courbe):
        """
        Ajoute une courbe au plotter.
        Retourne l'indice de la courbe dans le gestionnaire (à retenir par exemple
        pour supprimer la courbe par la suite).
        """
        curve_id = curve.get_type() + " " + str(len(self.courbes_))
        self.courbes_[curve_id] = curve
        # Pré-calcul des points de la courbe
        resolution = len(list(curve.control_points_as_points())) * 30
        self.cache[curve_id] = curve.points(resolution)

        self.update()
        return len(self.courbes_) - 1

    def remove_curve(self, curve_id):
        """
        Retire une courbe du gestionnaire, à partir de son indice.
        """
        # On ne retire pas d'éléments de la liste des courbes, on préfère mettre les valeurs à None
        # Cela permet d'éviter de décaler les indices des autres courbes, dont l'utilisateur a besoin.
        if self.selected_curve_id == curve_id:
            self.selected_curve = None
            self.selected_curve_id = None
        del self.courbes_[curve_id]
        self.update()

    def remove_selected_curve(self):
        """
        Removes the currently selected curve if there is one.
        """
        if self.selected_curve is None:
            raise ValueError("No curve currently selected")
        self.remove_curve(self.selected_curve_id)

    def select_curve(self, curve_id):
        """
        Applique un effet de "séléction" à une courbe, en dessinant ses extrémités.
        :param curve_id: ID de la courbe visée
        """

        # Marque la courbe comme sélectionnée
        self.selected_curve = self.courbes_[curve_id]
        self.selected_curve_id = curve_id

        # Mise à jour graphique
        self.update()

    def set_res(self, new_res: int):
        """
        Indique la résolution à utiliser pour le traceur.
        """
        self.res = new_res

    def courbes(self):
        """
        :return: Le dictionnaire des courbes du plotter.
        """
        return self.courbes_

    def get_figure(self):
        """
        :return: The pyplot Figure object created by the plotter.
        """
        return self.fig

    def on_pick_event(self, event):
        """
        Event associated with the picking of a Line or a point.
        Sets the point as selected.
        """
        point = event.artist
        if isinstance(point, Line2D):
            # Remembers the picking coordinates
            self.pick_pos = (point.get_xdata()[0], point.get_ydata()[0])

            # Remembers which Control point of the selected curve has
            # been selected (precisely, remembers its index in
            # self.selected_curve.control_points() ).
            self.picked_ctrl_point = self.identify_control_point(*self.pick_pos)
            self.update()
        return True

    def drag_event(self, event):
        """
        Event associated with the dragging of a Line or a point, i.e. when
        the user moves the cursor after they clicked on a point.
        Displaces it a the position of the cursor and recomputes the selected curve.
        """
        if self.selected_curve is not None and self.picked_ctrl_point is not None:
            # Current mouse coordinates
            mouse_pos = [event.xdata, event.ydata]

            xlims, ylims = self.axs.get_xlim(), self.axs.get_ylim()
            if mouse_pos[0] is None or mouse_pos[1] is None:
                return

            # Sets this position as the new control point for the
            # currently selected curve
            self.selected_curve.set_control_point(self.picked_ctrl_point,
                                                  Point(*mouse_pos))

            # Updates the canvas
            # Delete the selected curve from the cache, as it needs to be
            # recomputed
            del self.cache[self.selected_curve_id]
            self.update()
        return True

    def on_release_event(self, event):
        """
        Event associated with the release of a Line or a point.
        Releases the currently selected control point from being selected.
        """
        if self.picked_ctrl_point is not None:
            self.picked_ctrl_point = None
        return True

    def identify_control_point(self, picked_x, picked_y):
        """
        Identifies which of the selected curve's control points,
        given the coordinates of the picking.
        :return: The index of the control point picked in
                self.selected_curve.control_points()
        """
        if self.selected_curve is None:
            return
        # Browses all control points from the selected curve, and finds
        # the one whose coordinates match picked_x, picked_y
        for k, pt in enumerate(self.selected_curve.control_points_as_points()):
            if pt[0] == picked_x and pt[1] == picked_y:
                return k

    def get_curve_parameters(self):
        """
        :return: A dictionnary indicating the selected curve's parameters and their interval.
                For example, {'tension': (0, 1)} indicates a parameter called tension, with values between
                0 and 1.
        """
        if self.selected_curve is None:
            return None
        return self.selected_curve.hyperparameters()

    def set_curve_parameter(self,  paremeter_name, value):
        """
        Sets the value for a specific parameter of a plotted curve.
        :param paremeter_name: Name of the parameter (ex: tension for a CHS).
        :param value: New value for the parameter.
        """
        curve = self.selected_curve
        if curve is None:
            raise ValueError("Error CURVEPARAM0: No curve currently selected !")
        curve.set_parameter_value(paremeter_name, value)
        # Suppress the curve's cache to recompute it
        del self.cache[self.selected_curve_id]

        # Refresh
        self.update()

    def get_ylims(self):
        """
        :return: Returns the limits of the horizontal axis as a couple (ymin, ymax)
        """
        return self.axs.get_ylim()

    def get_xlims(self):
        """
        :return: Returns the limits of the horizontal axis as a couple (xmin, xmax)
        """
        return self.axs.get_xlim()
