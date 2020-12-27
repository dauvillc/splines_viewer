"""
Object containing the application's GUI Interface.
"""
import numpy as np
from tkinter import *
from tkinter.messagebox import showerror
from tkinter.ttk import Combobox
from plotter import Plotter
from courbes.spline_hermite_cubique import SplineHermiteCubique
from courbes.splines_c2 import SplineC2
from courbes.lagrange import CourbeLagrange
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from geom_utils.point import from_numpy_array, from_string

"""
Constructors for types of curves that can be created by the user
"""
curves_constructors = {'Cubic Hermite Spline': SplineHermiteCubique,
                       'Lagrange Interpolation': CourbeLagrange,
                       'C2 Spline': SplineC2}


def empty_widget(widget):
    """
    Empties a given widget.
    """
    for child in widget.winfo_children():
        child.destroy()  # HAAAAARDCOOOOOORE


class Interface(Frame):
    """
    The application's main window frame.
    """

    def __init__(self, root_window, width=1024, height=768, **kwargs):
        """
        :param root_window: Tkinter root window (obtained with tkinter.Tk() ).
        :param kwargs:
        """
        # Root window parametrisation
        root_window.geometry(str(width) + "x" + str(height))
        root_window.minsize(800, 600)
        root_window.title("Curve Plotter")

        # Generates the main window. The main buttons (Reduce, Quit) are automatically generated !
        Frame.__init__(self, width=width, height=height, **kwargs)
        self.pack(fill=BOTH, expand=TRUE)

        # MATPLOTLIB INTEGRATION ------------------------------------------

        self.plotter = Plotter()
        # Integrates the plt figure into a canvas object
        canvas = FigureCanvasTkAgg(self.plotter.fig, master=self)
        canvas.draw()
        # Places the canvas (and thus the plotting) on the right of
        # the window, and tells it to be as large as possible
        canvas.get_tk_widget().place(relx=0.2, relwidth=0.6, relheight=0.8)
        self.fig_canvas = canvas

        # Connections for drag & drop events
        self.fig_canvas.mpl_connect("pick_event", self.canvas_on_pick_event)

        # WIDGETS ---------------------------------------------------------
        # Widgets are of two types:
        # - permanent widgets will always be present on screen (On the left
        #       of the plotter, and curves menu on the right)
        # - Temporary widgets appear when the user selects a specific action.
        #       For example, clicking the "Add curve" button creates a menu
        #       at the bottom which allow for the creation of new curves.

        # MAIN MENU ---

        # Frame containing the permanent widgets
        permanent_menu = Frame(self, borderwidth=2, relief=GROOVE)
        permanent_menu.place(relheight=0.8, relwidth=0.2)
        self.permanent_menu = permanent_menu

        # Curve addition button
        buttonCurveAddition = Button(permanent_menu, text="Add a curve", command=self.createCurveMode)
        buttonCurveAddition.pack(side=TOP)
        self.buttonCurveAddition = buttonCurveAddition

        # CURVES LIST ---
        # Frame containing the curves list
        curves_list_frame = Frame(self, borderwidth=2, relief=GROOVE)
        curves_list_frame.place(relx=0.8, relwidth=0.2, relheight=0.8)
        self.curves_list_frame = curves_list_frame
        self.curves_list = None
        self.showCurvesList()

        # BOTTOM MENU ---

        # Frame containing the temporary widgets
        temporary_menu = Frame(self, borderwidth=2, relief=GROOVE)
        temporary_menu.place(rely=0.8, relwidth=1, relheight=0.2)
        self.temporary_menu = temporary_menu

        self.create_button = None
        self.cancel_button = None
        self.nb_points_entry = None
        self.control_points_entry = None
        self.listCurveType = None
        self.parameters_frame = None

    # CURVES LIST -----------------------------------------------------------------------------------

    def showCurvesList(self):
        """
        Shows the list of the plotter's curves on the right side menu.
        """
        # The list is implemented as a scrollbar
        label = Label(self.curves_list_frame, text="Current Curves", font=30)
        label.pack(side=TOP, pady=5)
        curves_scrollbar = Scrollbar(self.curves_list_frame)
        curves_scrollbar.pack(side=LEFT, pady=10)
        curves_scrollbar.place(relx=0.9, rely=0.05, relwidth=0.08, relheight=0.35)
        # ListBox containing the list of curves
        curves_list = Listbox(self.curves_list_frame, yscrollcommand=curves_scrollbar.set, exportselection=False)
        curves_list.place(rely=0.05, relx=0.03, relwidth=0.87, relheight=0.35)
        curves_list.bind("<<ListboxSelect>>", self.select_curve_callback)
        self.curves_list = curves_list

        # Add the curves to the list
        for curve_id in self.plotter.courbes().keys():
            curves_list.insert(END, curve_id)
        curves_scrollbar.config(command=curves_list.yview)

    def refreshCurvesList(self):
        """
        Refreshes the curves menu
        """
        empty_widget(self.curves_list_frame)
        self.showCurvesList()

    def createCurveMode(self):
        """
        Creates and draws the widgets that allow the user to create
        new curves and plot them.
        """
        # Curve selection frame
        curve_selection_frame = Frame(self.temporary_menu, borderwidth=2, relief=GROOVE)
        curve_selection_frame.place(relwidth=0.3, relheight=1)

        # Curve type selection list
        label1 = Label(curve_selection_frame, text="Curve type:").pack(side=TOP, pady=5)
        self.listCurveType = Combobox(curve_selection_frame, values=list(curves_constructors.keys()))
        self.listCurveType.pack(side=TOP, pady=5)

        # Create ! Button
        self.create_button = Button(curve_selection_frame, text="Create curve", command=self.createCurveCallback)
        self.create_button.pack(side=TOP, pady=5)

        # Cancel Button
        self.cancel_button = Button(curve_selection_frame, text="Cancel", command=self.resetMode)
        self.cancel_button.pack(side=TOP, pady=5)

        # Frame containing everything to create the curve
        curve_creation_frame = Frame(self.temporary_menu, borderwidth=2, relief=GROOVE)
        curve_creation_frame.place(relx=0.3, relwidth=0.7, relheight=1)

        # Entry for number of points
        Label(curve_creation_frame, text="Number of control points:").place(relx=0.05, rely=0.02)
        self.nb_points_entry = Entry(curve_creation_frame, width=40)
        self.nb_points_entry.place(relx=0.05, rely=0.15)

        # Entry for control points
        ctrl_points_entry_label = Label(curve_creation_frame,
                                        text="[Optional] Enter control points coordinates as such: x00 x01 x10 x11 ...")
        ctrl_points_entry_label.place(relx=0.05, rely=0.4)
        self.control_points_entry = Entry(curve_creation_frame, width=70)
        self.control_points_entry.place(relx=0.05, rely=0.55)

    def resetMode(self):
        """
        Disables any temporary widget and returns to the original
        state of the application.
        """
        empty_widget(self.temporary_menu)

    def showCurveParameters(self):
        """
        Displays a menu to adjust the selected curve's parameters.
        """
        # Obtain a dictionnary of the selected curve's parameters from the plotter
        params = self.plotter.get_curve_parameters()
        if params is None:
            raise ValueError("Can't show parameters, no curve currently selected")

        # For each parameter, create an entry to let the user modify it
        # First, define a frame to contain everything
        parameters_frame = Frame(self.curves_list_frame, borderwidth=2, relief=GROOVE)
        parameters_frame.place(rely=0.41, relx=0.03, relheight=0.5, relwidth=0.88)

        rely = 0.01
        # A map remembers all widgets associated to parameters, in order to retrieve their values
        # in the callback
        for param_name, param_values in params.items():
            if isinstance(param_values[0], (float, int)):
                # The parameter can be adjusted with a scale (a bar that can slide
                # to adjust the value).
                limit_inf, limit_sup, nb_values = param_values
                scaler = Scale(parameters_frame, from_=limit_inf, to=limit_sup,
                               orient=HORIZONTAL, resolution=(limit_sup - limit_inf) / nb_values,
                               command=lambda x: self.set_parameter_callback(scaler.param_name, scaler.get()), label=param_name)
                # Set the value of the widegt to the current value of the parameter
                scaler.set(self.plotter.selected_curve.hyperparameters_values()[param_name])

                # Remembers the parameter's name to use it inside the callback function
                scaler.param_name = param_name
                scaler.place(rely=rely)
            else:
                Label(parameters_frame, text=param_name).place(rely=rely)
                selection_box = Combobox(parameters_frame, values=param_values)
                selection_box.place(rely=rely + 0.1, relwidth=0.8)
                selection_box.bind("<<ComboboxSelected>>",
                                   lambda x: self.set_parameter_callback(selection_box.param_name, selection_box.get()))

                # Remembers the parameter's name tu use it inside the callback function
                selection_box.param_name = param_name

                # Set the value of the widegt to the current value of the parameter
                selection_box.set(self.plotter.selected_curve.hyperparameters_values()[param_name])
            rely += 0.2

        # Curve suppression button
        buttonCurveSuppression = Button(parameters_frame, text="Remove Curve", relief=GROOVE,
                                        command=self.remove_curve_callback)
        buttonCurveSuppression.pack(side=BOTTOM, pady=5)

        # Curve bending for cubic hermite splines
        # Show Bending button
        showBendingButton = Button(parameters_frame, text="Show Bending", relief=GROOVE,
                                   command=self.show_bending_callback)
        showBendingButton.pack(side=BOTTOM, pady=5)

        # Show curves button (opposite of showing the bending curve)
        showCurvesButton = Button(parameters_frame, text="Show Curves", relief=GROOVE,
                                  command=self.show_curves_callback)
        showCurvesButton.pack(side=BOTTOM, pady=5)

        self.parameters_frame = parameters_frame

    def set_parameter_callback(self, param_name, param_value):
        """
        Callback called when the user modifies a parameter in the curve
        parameter menu. Sets the value into the curve, recomputes the curve,
        and refresh the plt figure.
        """
        # Sets it into the selected curve
        self.plotter.set_curve_parameter(param_name, param_value)

        # Refresh the figure canvas
        self.fig_canvas.draw()

    def remove_curve_callback(self):
        """
        Callback called when the user presses the "Remove Curve" button.
        Suppresses the currently selected curve.
        """
        self.plotter.remove_selected_curve()
        self.fig_canvas.draw()
        self.refreshCurvesList()

    def show_bending_callback(self):
        """
        Shows on the figure canvas the bending of the selected curve instead
        of the curves.
        """
        self.plotter.plot_bending()
        self.fig_canvas.draw()

    def show_curves_callback(self):
        """
        Shows the curves on the matplotlib canvas.
        """
        self.plotter.update()
        self.fig_canvas.draw()

    # CURVE CREATION ----------------------------------------------------------------------------------

    def createCurveCallback(self):
        """
        Callback called when the user presses the "Create curve" button.
        """
        # Obtain the number of points from the input entry
        try:
            nb_points = int(self.nb_points_entry.get())
            if nb_points < 2:
                raise ValueError
        except ValueError:
            showerror("Creation Error", "Please insert an integer greater than 2")
            return

        # Constructor
        constructor = curves_constructors[self.listCurveType.get()]

        # Create the points
        # Either the user has entered specific coordinates
        # or the points are generated along the y=x line
        if self.control_points_entry.get() != "":
            # Obtain the coordinates from the user's input
            try:
                points = from_string(self.control_points_entry.get())
                # Check that user has entered the corresponding amount
                # of control points
                if len(points) != nb_points:
                    raise IndexError
            except ValueError:
                showerror("Curve creation error", "Please enter floating coordinates")
                return
            except IndexError:
                showerror("Curve creation error", "Missing coordinate(s)")
                return
        else:
            ylims = self.plotter.get_xlims()
            xlims = self.plotter.get_ylims()
            coords = np.vstack((np.linspace(*xlims, nb_points), np.linspace(*ylims, nb_points)))
            points = from_numpy_array(coords)

        # Create the params evenly spaced by 1
        params = np.arange(nb_points)

        # Create the curve using the constructor
        curve = constructor(points, params)

        # Add the curve to the plotter
        self.plotter.add_curve(curve)

        # Refresh the figure and the curves list
        self.fig_canvas.draw()
        self.showCurvesList()

    # FIGURE EVENTS -----------------------------------------------------------------------------------

    def select_curve_callback(self, event):
        """
        Applies a graphical "selection effect" to a curve given its id.
        """
        # Listbox event concerned
        listbox = event.widget
        if listbox != self.curves_list:
            return

        # Gets the curve id from the text of the list option that was clicked
        curve_id = listbox.get(int(listbox.curselection()[0]))
        self.plotter.select_curve(curve_id)

        # Show the curve menu
        self.showCurveParameters()

        # Refreshes the figure
        self.fig_canvas.draw()

    def canvas_on_pick_event(self, event):
        """
        Callback called when the user picks an artist on the plt figure.
        """
        self.plotter.on_pick_event(event)
        self.fig_canvas.draw()
        self.fig_canvas.mpl_connect("motion_notify_event", self.canvas_drag_event)
        self.fig_canvas.mpl_connect("button_release_event", self.canvas_release_event)

    def canvas_drag_event(self, event):
        """
        Callback called when the user drags a picked artist on the plt figure.
        """
        self.plotter.drag_event(event)
        self.fig_canvas.draw()

    def canvas_release_event(self, event):
        """
        Callback called when the user releases the mouse button on the plt canvas.
        """
        self.plotter.on_release_event(event)
        self.fig_canvas.mpl_disconnect("motion_notify_event")
        self.fig_canvas.mpl_disconnect("button_release_event")
        self.fig_canvas.draw()
