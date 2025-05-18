import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import pandas as pd
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.patheffects as path_effects
from matplotlib.cm import get_cmap
import os
import platform

# Allowed functions for safe evaluation
allowed_functions = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "log": sp.log, "ln": sp.log, "exp": sp.exp,
    "e": sp.E, "pi": sp.pi
}

class ModernUI:
    """Helper class for modern UI elements"""
    
    @staticmethod
    def set_theme(root, dark_mode=False):
        """Set a modern theme for the application"""
        style = ttk.Style()
        
        if dark_mode:
            # Dark mode theme
            root.configure(bg='#2d2d2d')
            
            # Configure colors for dark mode
            style.configure('TFrame', background='#2d2d2d')
            style.configure('TLabel', background='#2d2d2d', foreground='#ffffff', font=('Segoe UI', 10))
            style.configure('TButton', font=('Segoe UI', 10))
            style.configure('TCheckbutton', background='#2d2d2d', foreground='#ffffff', font=('Segoe UI', 10))
            style.configure('TRadiobutton', background='#2d2d2d', foreground='#ffffff', font=('Segoe UI', 10))
            style.configure('TEntry', font=('Segoe UI', 10))
            style.configure('TCombobox', font=('Segoe UI', 10))
            
            # Configure Notebook (tabs)
            style.configure('TNotebook', background='#2d2d2d', tabmargins=[2, 5, 2, 0])
            style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 10), background='#3d3d3d', foreground='#ffffff')
            
            # Configure Treeview (for tables)
            style.configure('Treeview', font=('Segoe UI', 9), background='#3d3d3d', foreground='#ffffff', fieldbackground='#3d3d3d')
            style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background='#3d3d3d', foreground='#ffffff')
            
            # Configure LabelFrame
            style.configure('TLabelframe', background='#2d2d2d', foreground='#ffffff')
            style.configure('TLabelframe.Label', font=('Segoe UI', 10, 'bold'), background='#2d2d2d', foreground='#ffffff')
            
            # Map states for hover effects in dark mode
            style.map('TButton', 
                background=[('active', '#3d3d3d')],
                foreground=[('active', '#ffffff')])
            style.map('TCheckbutton', 
                background=[('active', '#3d3d3d')],
                foreground=[('active', '#ffffff')])
            style.map('TRadiobutton', 
                background=[('active', '#3d3d3d')],
                foreground=[('active', '#ffffff')])
            
            # Configure row colors for Treeview
            style.map('Treeview', 
                background=[('selected', '#4a6984')],
                foreground=[('selected', '#ffffff')])
            
        else:
            # Light mode theme
            root.configure(bg='#f0f0f0')
            
            # Try to use a more modern theme if available
            try:
                if platform.system() == "Windows":
                    root.tk.call('source', 'azure.tcl')
                    root.tk.call('set_theme', 'light')
                else:
                    style.theme_use('clam')  # Use 'clam' theme as a fallback
            except:
                # Fallback to a custom style
                available_themes = style.theme_names()
                if 'clam' in available_themes:
                    style.theme_use('clam')
            
            # Configure colors for light mode
            style.configure('TFrame', background='#f5f5f5')
            style.configure('TLabel', background='#f5f5f5', foreground='#000000', font=('Segoe UI', 10))
            style.configure('TButton', font=('Segoe UI', 10))
            style.configure('TCheckbutton', background='#f5f5f5', foreground='#000000', font=('Segoe UI', 10))
            style.configure('TRadiobutton', background='#f5f5f5', foreground='#000000', font=('Segoe UI', 10))
            style.configure('TEntry', font=('Segoe UI', 10))
            style.configure('TCombobox', font=('Segoe UI', 10))
            
            # Configure Notebook (tabs)
            style.configure('TNotebook', background='#f5f5f5', tabmargins=[2, 5, 2, 0])
            style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 10))
            
            # Configure Treeview (for tables)
            style.configure('Treeview', font=('Segoe UI', 9), background='#ffffff', foreground='#000000', fieldbackground='#ffffff')
            style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
            
            # Configure LabelFrame
            style.configure('TLabelframe', background='#f5f5f5')
            style.configure('TLabelframe.Label', font=('Segoe UI', 10, 'bold'))
    
    @staticmethod
    def create_tooltip(widget, text, dark_mode=False):
        """Create a tooltip for a widget"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Create a toplevel window
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            bg_color = "#2d2d2d" if dark_mode else "#ffffff"
            fg_color = "#ffffff" if dark_mode else "#000000"
            
            label = ttk.Label(tooltip, text=text, justify='left',
                             background=bg_color, foreground=fg_color, relief="solid", borderwidth=1,
                             font=("Segoe UI", 9, "normal"), padding=(5, 2))
            label.pack(ipadx=1)
            
            widget.tooltip = tooltip
            
        def leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    @staticmethod
    def create_button(parent, text, command, icon=None, tooltip=None, dark_mode=False):
        """Create a modern button with optional icon and tooltip"""
        btn = ttk.Button(parent, text=text, command=command)
        if tooltip:
            ModernUI.create_tooltip(btn, tooltip, dark_mode)
        return btn

class NumericalMethods:
    def __init__(self, master):
        self.master = master
        self.master.title("Numerical Root-Finding Methods")
        self.master.geometry("1280x800")
        self.master.minsize(1000, 700)  # Set minimum window size
        
        # Create symbolic variable for equation parsing
        self.x_sym = sp.Symbol('x')
        self.function = None
        self.function_str = ""
        self.roots = []
        self.iterations_data = []  # Will be a list of dictionaries with 'root' and 'data' keys
        self.root_annotations = []  # Store annotation objects for hover effects
        
        # Graph scaling
        self.min_x, self.max_x = -5, 5
        self.min_y, self.max_y = -5, 5
        self.num_points = 1000
        self.zoom_factor = 1.2
        
        # Number precision option
        self.use_full_precision = tk.BooleanVar(value=False)
        
        # Dark mode option
        self.use_dark_mode = tk.BooleanVar(value=False)
        self.use_dark_mode.trace("w", self.toggle_dark_mode)
        
        # Set initial theme
        ModernUI.set_theme(self.master, False)
        
        # Method descriptions for help
        self.method_descriptions = {
            "Graphical Method": "Finds roots by identifying where the function crosses the x-axis on a graph. Simple but less accurate than other methods.",
            
            "Incremental Method": "Searches for sign changes in the function by evaluating it at small increments. Once a sign change is detected, a root exists in that interval.",
            
            "Bisection Method": "Repeatedly divides an interval in half and selects the subinterval where the function changes sign. Simple and reliable but converges slowly.",
            
            "Regula Falsi Method": "Also known as the False Position method. Uses linear interpolation between two points to estimate the root. Faster than bisection but may converge slowly for some functions.",
            
            "Newton-Raphson Method": "Uses the function and its derivative to find increasingly accurate approximations. Very fast convergence when close to a root, but requires the derivative and a good initial guess.",
            
            "Secant Method": "Similar to Newton-Raphson but doesn't require derivatives. Uses two points to approximate the derivative. Good convergence rate without needing the derivative function."
        }
        
        # Create main UI
        self.create_widgets()
        
        # Set default function
        self.function_entry.focus_set()
    
    def toggle_dark_mode(self, *args):
        """Toggle between light and dark mode"""
        dark_mode = self.use_dark_mode.get()
        
        # Update the theme
        ModernUI.set_theme(self.master, dark_mode)
        
        if dark_mode:
            # Dark mode
            plt.style.use('dark_background')
            
            # Update results text
            self.results_text.configure(bg='#3d3d3d', fg='#ffffff', insertbackground='#ffffff')
            
            # Update tooltips
            for widget in self.tooltip_widgets:
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.destroy()
                ModernUI.create_tooltip(widget, widget.tooltip_text, True)
            
            # Update graph if it exists
            if hasattr(self, 'ax'):
                self.fig.set_facecolor('#2d2d2d')
                self.ax.set_facecolor('#2d2d2d')
                self.ax.tick_params(colors='#ffffff')
                self.ax.xaxis.label.set_color('#ffffff')
                self.ax.yaxis.label.set_color('#ffffff')
                self.ax.title.set_color('#ffffff')
                
                # Make grid lines white for better visibility
                self.ax.grid(True, linestyle='--', alpha=0.7, color='#ffffff')
                
                # Update axes
                self.ax.spines['bottom'].set_color('#ffffff')
                self.ax.spines['top'].set_color('#ffffff')
                self.ax.spines['left'].set_color('#ffffff')
                self.ax.spines['right'].set_color('#ffffff')
                
                # Update canvas
                self.canvas.draw()
            
            # Update table colors
            if hasattr(self, 'table_scrollable_frame'):
                for tree in self.find_all_treeviews(self.table_scrollable_frame):
                    tree.tag_configure("even", background="#3d3d3d", foreground="#ffffff")
                    tree.tag_configure("odd", background="#2d2d2d", foreground="#ffffff")
        else:
            # Light mode
            plt.style.use('default')
            
            # Update results text
            self.results_text.configure(bg='#ffffff', fg='#000000', insertbackground='#000000')
            
            # Update tooltips
            for widget in self.tooltip_widgets:
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.destroy()
                ModernUI.create_tooltip(widget, widget.tooltip_text, False)
            
            # Update graph if it exists
            if hasattr(self, 'ax'):
                self.fig.set_facecolor('#ffffff')
                self.ax.set_facecolor('#ffffff')
                self.ax.tick_params(colors='#000000')
                self.ax.xaxis.label.set_color('#000000')
                self.ax.yaxis.label.set_color('#000000')
                self.ax.title.set_color('#000000')
                
                # Reset grid lines to default
                self.ax.grid(True, linestyle='--', alpha=0.7, color='#b0b0b0')
                
                # Update axes
                self.ax.spines['bottom'].set_color('#000000')
                self.ax.spines['top'].set_color('#000000')
                self.ax.spines['left'].set_color('#000000')
                self.ax.spines['right'].set_color('#000000')
                
                # Update canvas
                self.canvas.draw()
            
            # Update table colors
            if hasattr(self, 'table_scrollable_frame'):
                for tree in self.find_all_treeviews(self.table_scrollable_frame):
                    tree.tag_configure("even", background="#f0f0f0", foreground="#000000")
                    tree.tag_configure("odd", background="#ffffff", foreground="#000000")
    
    def find_all_treeviews(self, parent):
        """Find all Treeview widgets in a parent widget"""
        treeviews = []
        for child in parent.winfo_children():
            if isinstance(child, ttk.Treeview):
                treeviews.append(child)
            treeviews.extend(self.find_all_treeviews(child))
        return treeviews
    
    def create_widgets(self):
        # Store widgets that need tooltips for dark mode updates
        self.tooltip_widgets = []
        
        # Main frame with padding
        main_frame = ttk.Frame(self.master, padding=(15, 15))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a paned window for resizable panels
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for inputs and controls
        left_panel = ttk.Frame(paned_window, width=350)
        
        # Right panel for visualization
        self.right_panel = ttk.Frame(paned_window)
        
        # Add panels to paned window
        paned_window.add(left_panel, weight=1)
        paned_window.add(self.right_panel, weight=3)
        
        # Create a header frame
        header_frame = ttk.Frame(left_panel)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # App title and version
        title_label = ttk.Label(header_frame, text="Numerical Root-Finding Methods", 
                               font=("Segoe UI", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Dark mode toggle
        dark_mode_frame = ttk.Frame(header_frame)
        dark_mode_frame.pack(side=tk.RIGHT)
        
        dark_mode_check = ttk.Checkbutton(
            dark_mode_frame, 
            text="Dark Mode",
            variable=self.use_dark_mode
        )
        dark_mode_check.pack(side=tk.RIGHT)
        
        # Create a notebook for organized input sections
        input_notebook = ttk.Notebook(left_panel)
        input_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Function input tab
        function_tab = ttk.Frame(input_notebook, padding=10)
        input_notebook.add(function_tab, text="Function")
        
        # Method selection tab
        method_tab = ttk.Frame(input_notebook, padding=10)
        input_notebook.add(method_tab, text="Method")
        
        # Parameters tab
        params_tab = ttk.Frame(input_notebook, padding=10)
        input_notebook.add(params_tab, text="Parameters")
        
        # Function input section
        ttk.Label(function_tab, text="Enter function f(x):", font=("Segoe UI", 12)).pack(anchor=tk.W, pady=(5, 5))
        
        # Function entry with a modern look
        function_frame = ttk.Frame(function_tab)
        function_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.function_entry = ttk.Entry(function_frame, font=("Segoe UI", 12))
        self.function_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.function_entry.insert(0, "f(x) = x^3 - 0.165*x^2 + 3.993*10^-4")
        
        # Function examples section
        examples_frame = ttk.LabelFrame(function_tab, text="Examples", padding=(10, 5))
        examples_frame.pack(fill=tk.X, pady=10)
        
        examples_text = "f(x) = x^2 - 4\nf(x) = e^-x - x\nf(x) = 3*x + sin(x) - e^x\nf(x) = x^3 - 0.165*x^2 + 3.993*10^-4"
        examples_label = ttk.Label(examples_frame, text=examples_text, font=("Segoe UI", 10))
        examples_label.pack(anchor=tk.W, pady=5)
        
        # Quick insert buttons for examples
        examples_buttons_frame = ttk.Frame(examples_frame)
        examples_buttons_frame.pack(fill=tk.X, pady=5)
        
        example_functions = [
            "x^2 - 4", 
            "e^-x - x", 
            "3*x + sin(x) - e^x",
            "x^3 - 0.165*x^2 + 3.993*10^-4"
        ]
        
        for i, func in enumerate(example_functions):
            btn = ttk.Button(
                examples_buttons_frame, 
                text=f"Example {i+1}", 
                command=lambda f=func: self.insert_example(f)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Help button for syntax
        help_button = ttk.Button(
            function_tab, 
            text="Syntax Help", 
            command=self.show_syntax_help
        )
        help_button.pack(anchor=tk.W, pady=(5, 10))
        help_button.tooltip_text = "Learn about function syntax and supported operations"
        ModernUI.create_tooltip(help_button, help_button.tooltip_text, self.use_dark_mode.get())
        self.tooltip_widgets.append(help_button)
        
        # Method selection section
        ttk.Label(method_tab, text="Select Method:", font=("Segoe UI", 12)).pack(anchor=tk.W, pady=(5, 5))
        
        self.method_var = tk.StringVar()
        methods = [
            "Graphical Method",
            "Incremental Method",
            "Bisection Method",
            "Regula Falsi Method",
            "Newton-Raphson Method",
            "Secant Method"
        ]
        
        # Method selection with radio buttons for better UX
        methods_frame = ttk.Frame(method_tab)
        methods_frame.pack(fill=tk.X, pady=5)
        
        for method in methods:
            method_radio = ttk.Radiobutton(
                methods_frame, 
                text=method, 
                value=method, 
                variable=self.method_var
            )
            method_radio.pack(anchor=tk.W, pady=2)
        
        # Set default method
        self.method_var.set(methods[0])
        
        # Method description
        desc_frame = ttk.LabelFrame(method_tab, text="Method Description", padding=(10, 5))
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.method_desc_label = ttk.Label(
            desc_frame, 
            text=self.method_descriptions["Graphical Method"],
            wraplength=300, 
            justify=tk.LEFT, 
            font=("Segoe UI", 10)
        )
        self.method_desc_label.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Update description when method changes
        self.method_var.trace("w", self.update_method_description)
        
        # Add method help button
        method_help_button = ttk.Button(
            method_tab, 
            text="Detailed Method Help", 
            command=self.show_method_help
        )
        method_help_button.pack(anchor=tk.W, pady=(5, 10))
        method_help_button.tooltip_text = "Learn more about each numerical method"
        ModernUI.create_tooltip(method_help_button, method_help_button.tooltip_text, self.use_dark_mode.get())
        self.tooltip_widgets.append(method_help_button)
        
        # Parameters section
        # Common parameters
        common_params_frame = ttk.LabelFrame(params_tab, text="Search Range", padding=(10, 5))
        common_params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid layout for parameters
        ttk.Label(common_params_frame, text="From:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.x_min_var = tk.StringVar(value="-5")
        ttk.Entry(common_params_frame, textvariable=self.x_min_var, width=10).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(common_params_frame, text="To:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.x_max_var = tk.StringVar(value="5")
        ttk.Entry(common_params_frame, textvariable=self.x_max_var, width=10).grid(row=0, column=3, pady=5, padx=5)
        
        # Convergence parameters
        conv_params_frame = ttk.LabelFrame(params_tab, text="Convergence Parameters", padding=(10, 5))
        conv_params_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(conv_params_frame, text="Tolerance:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.tolerance_var = tk.StringVar(value="0.0001")
        tolerance_entry = ttk.Entry(conv_params_frame, textvariable=self.tolerance_var, width=10)
        tolerance_entry.grid(row=0, column=1, pady=5, padx=5)
        tolerance_entry.tooltip_text = "Stopping criterion for convergence"
        ModernUI.create_tooltip(tolerance_entry, tolerance_entry.tooltip_text, self.use_dark_mode.get())
        self.tooltip_widgets.append(tolerance_entry)
        
        ttk.Label(conv_params_frame, text="Max Iterations:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.max_iter_var = tk.StringVar(value="100")
        max_iter_entry = ttk.Entry(conv_params_frame, textvariable=self.max_iter_var, width=10)
        max_iter_entry.grid(row=1, column=1, pady=5, padx=5)
        max_iter_entry.tooltip_text = "Maximum number of iterations"
        ModernUI.create_tooltip(max_iter_entry, max_iter_entry.tooltip_text, self.use_dark_mode.get())
        self.tooltip_widgets.append(max_iter_entry)
        
        # Method-specific parameters
        method_params_frame = ttk.LabelFrame(params_tab, text="Method-Specific Parameters", padding=(10, 5))
        method_params_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(method_params_frame, text="Step Size (Incremental):").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.step_size_var = tk.StringVar(value="0.1")
        step_size_entry = ttk.Entry(method_params_frame, textvariable=self.step_size_var, width=10)
        step_size_entry.grid(row=0, column=1, pady=5, padx=5)
        step_size_entry.tooltip_text = "Interval size for incremental search"
        ModernUI.create_tooltip(step_size_entry, step_size_entry.tooltip_text, self.use_dark_mode.get())
        self.tooltip_widgets.append(step_size_entry)
        
        ttk.Label(method_params_frame, text="Initial Guess (Newton/Secant):").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.initial_guess_var = tk.StringVar(value="1.0")
        initial_guess_entry = ttk.Entry(method_params_frame, textvariable=self.initial_guess_var, width=10)
        initial_guess_entry.grid(row=1, column=1, pady=5, padx=5)
        initial_guess_entry.tooltip_text = "Starting point for iteration"
        ModernUI.create_tooltip(initial_guess_entry, initial_guess_entry.tooltip_text, self.use_dark_mode.get())
        self.tooltip_widgets.append(initial_guess_entry)
        
        ttk.Label(method_params_frame, text="Second Guess (Secant):").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.second_guess_var = tk.StringVar(value="2.0")
        second_guess_entry = ttk.Entry(method_params_frame, textvariable=self.second_guess_var, width=10)
        second_guess_entry.grid(row=2, column=1, pady=5, padx=5)
        second_guess_entry.tooltip_text = "Second point for secant method"
        ModernUI.create_tooltip(second_guess_entry, second_guess_entry.tooltip_text, self.use_dark_mode.get())
        self.tooltip_widgets.append(second_guess_entry)
        
        # Action buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=10)
        
        find_roots_btn = ttk.Button(
            button_frame, 
            text="Find Roots", 
            command=self.find_roots,
            style='Accent.TButton'  # Custom style for primary button
        )
        find_roots_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(
            button_frame, 
            text="Clear Results", 
            command=self.clear_results
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(left_panel, text="Results", padding=(10, 5))
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            width=40, 
            height=10, 
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create tabs for graph and table in right panel
        self.tabs = ttk.Notebook(self.right_panel)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        
        self.graph_frame = ttk.Frame(self.tabs)
        self.table_frame = ttk.Frame(self.tabs)
        
        self.tabs.add(self.graph_frame, text="Graph")
        self.tabs.add(self.table_frame, text="Iterations Table")
        
        # Add precision toggle checkbox to table frame
        self.precision_frame = ttk.Frame(self.table_frame)
        self.precision_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.precision_check = ttk.Checkbutton(
            self.precision_frame, 
            text="Use full-precision floating-point numbers",
            variable=self.use_full_precision,
            command=self.update_table
        )
        self.precision_check.pack(anchor=tk.W)
        
        # Create initial empty figure
        self.create_empty_figure()
    
    def insert_example(self, function_text):
        """Insert an example function into the entry field"""
        self.function_entry.delete(0, tk.END)
        self.function_entry.insert(0, f"f(x) = {function_text}")
    
    def update_method_description(self, *args):
        """Update the method description when the selected method changes"""
        selected_method = self.method_var.get()
        if selected_method in self.method_descriptions:
            self.method_desc_label.config(text=self.method_descriptions[selected_method])
    
    def show_method_help(self):
        """Show detailed help about each numerical method"""
        help_text = """
Numerical Root-Finding Methods:

1. Graphical Method:
   - Visually identifies where the function crosses the x-axis
   - Advantages: Simple, visual, gives approximate locations of all roots
   - Disadvantages: Limited accuracy, depends on graph resolution

2. Incremental Method:
   - Systematically evaluates the function at small steps
   - Detects sign changes to locate intervals containing roots
   - Advantages: Simple, can find multiple roots
   - Disadvantages: Accuracy depends on step size

3. Bisection Method:
   - Repeatedly divides an interval in half and selects the subinterval where the function changes sign
   - Advantages: Always converges, reliable, simple
   - Disadvantages: Slow convergence (linear)

4. Regula Falsi Method (False Position):
   - Uses linear interpolation between points where function has opposite signs
   - Advantages: Faster than bisection, always converges
   - Disadvantages: Can be slow for certain functions

5. Newton-Raphson Method:
   - Uses function value and derivative to find increasingly better approximations
   - Formula: x_{n+1} = x_n - f(x_n)/f'(x_n)
   - Advantages: Very fast convergence (quadratic) near roots
   - Disadvantages: Requires derivative, sensitive to initial guess, can diverge

6. Secant Method:
   - Approximates the derivative using two points
   - Formula: x_{n+1} = x_n - f(x_n)(x_n - x_{n-1})/(f(x_n) - f(x_{n-1}))
   - Advantages: Good convergence without needing derivatives
   - Disadvantages: Requires two initial points, can diverge
        """
        
        help_window = tk.Toplevel(self.master)
        help_window.title("Numerical Methods Help")
        help_window.geometry("700x500")
        help_window.minsize(600, 400)
        
        # Make the window modal
        help_window.transient(self.master)
        help_window.grab_set()
        
        # Apply dark mode if enabled
        if self.use_dark_mode.get():
            help_window.configure(bg='#2d2d2d')
        
        # Add a frame with padding
        frame = ttk.Frame(help_window, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a title
        title_label = ttk.Label(frame, text="Numerical Root-Finding Methods", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Add scrolled text with the help content
        help_text_widget = scrolledtext.ScrolledText(frame, font=("Segoe UI", 11), wrap=tk.WORD)
        if self.use_dark_mode.get():
            help_text_widget.configure(bg='#3d3d3d', fg='#ffffff', insertbackground='#ffffff')
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.configure(state="disabled")
        
        # Add a close button
        close_button = ttk.Button(frame, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)
        
        # Center the window on the screen
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def show_syntax_help(self):
        help_text = """
Function Syntax Help:

Input Format:
- Start with "f(x) = " followed by your equation

Basic operations:
- Addition: +
- Subtraction: -
- Multiplication: *
- Division: /
- Power: ^ or **

Constants:
- Pi: pi
- Euler's number (e): e

Functions:
- Exponential: e^x or exp(x)
- Sine: sin(x)
- Cosine: cos(x)
- Tangent: tan(x)
- Natural logarithm: ln(x) or log(x)
- Square root: sqrt(x)

Examples:
- f(x) = x^2 - 4
- f(x) = e^-x - x
- f(x) = 3*x + sin(x) - e^x
        """
        
        help_window = tk.Toplevel(self.master)
        help_window.title("Function Syntax Help")
        help_window.geometry("600x500")
        help_window.minsize(500, 400)
        
        # Make the window modal
        help_window.transient(self.master)
        help_window.grab_set()
        
        # Apply dark mode if enabled
        if self.use_dark_mode.get():
            help_window.configure(bg='#2d2d2d')
        
        # Add a frame with padding
        frame = ttk.Frame(help_window, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a title
        title_label = ttk.Label(frame, text="Function Syntax Help", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Add scrolled text with the help content
        help_text_widget = scrolledtext.ScrolledText(frame, font=("Segoe UI", 11), wrap=tk.WORD)
        if self.use_dark_mode.get():
            help_text_widget.configure(bg='#3d3d3d', fg='#ffffff', insertbackground='#ffffff')
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.configure(state="disabled")
        
        # Add a close button
        close_button = ttk.Button(frame, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)
        
        # Center the window on the screen
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def create_empty_figure(self):
        # Clear previous figure if exists
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Create figure with improved styling
        self.fig = Figure(figsize=(8, 6), dpi=100, constrained_layout=True)
        self.ax = self.fig.add_subplot(111)
        
        # Apply dark mode if enabled
        dark_mode = self.use_dark_mode.get()
        if dark_mode:
            self.fig.set_facecolor('#2d2d2d')
            self.ax.set_facecolor('#2d2d2d')
            self.ax.tick_params(colors='#ffffff')
            self.ax.xaxis.label.set_color('#ffffff')
            self.ax.yaxis.label.set_color('#ffffff')
            self.ax.title.set_color('#ffffff')
            
            # Make grid lines white for better visibility in dark mode
            grid_color = '#ffffff'
            
            # Update axes
            self.ax.spines['bottom'].set_color('#ffffff')
            self.ax.spines['top'].set_color('#ffffff')
            self.ax.spines['left'].set_color('#ffffff')
            self.ax.spines['right'].set_color('#ffffff')
        else:
            grid_color = '#b0b0b0'  # Default grid color for light mode
        
        self.ax.set_title("Function Graph", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("x", fontsize=12)
        self.ax.set_ylabel("f(x)", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7, color=grid_color)
        self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # Create toolbar frame
        toolbar_frame = ttk.Frame(self.graph_frame)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Add zoom controls
        zoom_in_btn = ttk.Button(toolbar_frame, text="Zoom In", command=self.zoom_in)
        zoom_in_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        zoom_out_btn = ttk.Button(toolbar_frame, text="Zoom Out", command=self.zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        reset_view_btn = ttk.Button(toolbar_frame, text="Reset View", command=self.reset_view)
        reset_view_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create canvas
        canvas_frame = ttk.Frame(self.graph_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add zoom and pan functionality
        self.canvas.get_tk_widget().bind("<ButtonPress-1>", self.on_press)
        self.canvas.get_tk_widget().bind("<ButtonRelease-1>", self.on_release)
        self.canvas.get_tk_widget().bind("<B1-Motion>", self.on_drag)
        self.canvas.get_tk_widget().bind("<MouseWheel>", self.on_scroll)  # Windows
        self.canvas.get_tk_widget().bind("<Button-4>", self.on_scroll)    # Linux scroll up
        self.canvas.get_tk_widget().bind("<Button-5>", self.on_scroll)    # Linux scroll down
        
        # Add hover detection for annotations
        self.canvas.get_tk_widget().bind("<Motion>", self.on_mouse_move)
        
        # Reset root annotations list
        self.root_annotations = []
    
    def zoom_in(self):
        """Zoom in on the graph"""
        x_center, y_center = (self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2
        scale = 1 / self.zoom_factor
        
        width = (self.max_x - self.min_x) * scale
        height = (self.max_y - self.min_y) * scale

        self.min_x, self.max_x = x_center - width / 2, x_center + width / 2
        self.min_y, self.max_y = y_center - height / 2, y_center + height / 2

        self.update_graph()
    
    def zoom_out(self):
        """Zoom out on the graph"""
        x_center, y_center = (self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2
        scale = self.zoom_factor
        
        width = (self.max_x - self.min_x) * scale
        height = (self.max_y - self.min_y) * scale

        self.min_x, self.max_x = x_center - width / 2, x_center + width / 2
        self.min_y, self.max_y = y_center - height / 2, y_center + height / 2

        self.update_graph()
    
    def reset_view(self):
        """Reset the graph view to default"""
        try:
            self.min_x = float(self.x_min_var.get())
            self.max_x = float(self.x_max_var.get())
            
            # Calculate appropriate y range based on function
            if self.function is not None:
                x = np.linspace(self.min_x, self.max_x, 100)
                y = self.function(x)
                y_range = max(y) - min(y)
                self.min_y = min(y) - 0.1 * y_range
                self.max_y = max(y) + 0.1 * y_range
            else:
                self.min_y, self.max_y = -5, 5
                
            self.update_graph()
        except:
            self.min_x, self.max_x = -5, 5
            self.min_y, self.max_y = -5, 5
            self.update_graph()

    def on_mouse_move(self, event):
        """Handle mouse movement to detect hover over root annotations"""
        if not hasattr(self, 'fig') or not self.root_annotations:
            return
            
        # Convert display coordinates to data coordinates
        display_coord = (event.x, event.y)
        ax_coord = self.ax.transAxes.inverted().transform(
            self.fig.transFigure.inverted().transform(
                self.canvas.get_tk_widget().winfo_rootx() + display_coord
            )
        )
        
        # Check if mouse is over any annotation
        for i, annotation in enumerate(self.root_annotations):
            # Get the annotation's bounding box
            bbox = annotation.get_bbox_patch()
            if bbox and bbox.contains_point(ax_coord):
                # Bring this annotation to front by increasing zorder
                annotation.set_zorder(100)  # High value to bring to front
                # Make the annotation more prominent
                bbox.set(boxstyle="round,pad=0.6", facecolor='yellow', alpha=0.9)
                # Update the canvas
                self.canvas.draw_idle()
            else:
                # Reset zorder for non-hovered annotations
                annotation.set_zorder(10 + i)  # Base zorder plus index
                # Reset the annotation style
                bg_color = '#3d3d3d' if self.use_dark_mode.get() else 'white'
                bbox.set(boxstyle="round,pad=0.5", facecolor=bg_color, alpha=0.8)

    def on_scroll(self, event):
        """Zoom in and out."""
        x_center, y_center = (self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2
        
        # Handle different event types for different platforms
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            # Scroll up - zoom in
            scale = 1 / self.zoom_factor
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Scroll down - zoom out
            scale = self.zoom_factor
        else:
            return
            
        width = (self.max_x - self.min_x) * scale
        height = (self.max_y - self.min_y) * scale

        self.min_x, self.max_x = x_center - width / 2, x_center + width / 2
        self.min_y, self.max_y = y_center - height / 2, y_center + height / 2

        self.update_graph()

    def on_press(self, event):
        """Start panning."""
        self.pan_start = (event.x, event.y)

    def on_release(self, event):
        """Stop panning."""
        self.pan_start = None

    def on_drag(self, event):
        """Pan the graph."""
        if self.pan_start is None:
            return

        dx = (event.x - self.pan_start[0]) * (self.max_x - self.min_x) / self.canvas.get_tk_widget().winfo_width()
        dy = (event.y - self.pan_start[1]) * (self.max_y - self.min_y) / self.canvas.get_tk_widget().winfo_height()

        self.min_x -= dx
        self.max_x -= dx
        self.min_y += dy
        self.max_y += dy

        self.pan_start = (event.x, event.y)
        self.update_graph()
    
    def create_empty_table(self):
        # Clear previous table if exists
        for widget in self.table_frame.winfo_children():
            if widget != self.precision_frame:  # Keep the precision toggle
                widget.destroy()
        
        # Create a frame for the table with scrollbars
        table_container = ttk.Frame(self.table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Add a canvas for scrolling
        canvas = tk.Canvas(table_container)
        if self.use_dark_mode.get():
            canvas.configure(bg='#2d2d2d')
            
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store the scrollable frame for later use
        self.table_scrollable_frame = scrollable_frame
    
    def format_number(self, value):
        """Format a number based on the precision setting"""
        if isinstance(value, (int, float)):
            if self.use_full_precision.get():
                return value  # Full precision
            else:
                # Round to 4 decimal places for readability
                if abs(value) < 0.0001:  # For very small numbers, use scientific notation
                    return f"{value:.4e}"
                else:
                    return round(value, 4)
        return value  # Return non-numeric values unchanged
    
    def parse_function(self):
        try:
            # Get function string from entry
            input_str = self.function_entry.get().strip()
            
            # Check if the input starts with "f(x) ="
            if not input_str.startswith("f(x) ="):
                messagebox.showerror("Error", "Function must start with 'f(x) ='")
                return False
                
            # Extract the equation part after f(x) =
            self.function_str = input_str[6:].strip()
            
            # Handle e^-x specifically
            if "e^-" in self.function_str:
                self.function_str = self.function_str.replace("e^-", "exp(-")
                # Add closing parenthesis
                parts = self.function_str.split("exp(-")
                if len(parts) > 1:
                    var_part = parts[1].split()[0].split('-')[0].split('+')[0].split('*')[0].split('/')[0]
                    self.function_str = self.function_str.replace(f"exp(-{var_part}", f"exp(-{var_part})")
            
            # Handle other e^ expressions
            elif "e^" in self.function_str:
                self.function_str = self.function_str.replace("e^", "exp(")
                # Add closing parenthesis
                parts = self.function_str.split("exp(")
                if len(parts) > 1:
                    var_part = parts[1].split()[0].split('-')[0].split('+')[0].split('*')[0].split('/')[0]
                    self.function_str = self.function_str.replace(f"exp({var_part}", f"exp({var_part})")
            
            # Replace ^ with ** for exponentiation
            self.function_str = self.function_str.replace("^", "**")
            
            # Add multiplication signs where needed
            self.function_str = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', self.function_str)
            self.function_str = re.sub(r'([a-zA-Z\)])(\d)', r'\1*\2', self.function_str)
            
            # Replace ln with log
            self.function_str = self.function_str.replace("ln(", "log(")
            
            print(f"Parsed equation: {self.function_str}")
            
            # Create a safe evaluation environment
            safe_env = {"x": self.x_sym, **allowed_functions}
            
            # Evaluate the expression
            f_expr = eval(self.function_str, safe_env)
            
            # Convert sympy expression to a callable function
            self.function = sp.lambdify(self.x_sym, f_expr, 'numpy')
            
            # Create derivative function
            self.derivative = sp.lambdify(self.x_sym, sp.diff(f_expr, self.x_sym), 'numpy')
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Invalid function: {str(e)}\n\nPlease check the syntax and try again.")
            return False
    
    def evaluate_function(self, x):
        try:
            return self.function(x)
        except Exception as e:
            messagebox.showerror("Error", f"Error evaluating function at x={x}: {str(e)}")
            return None
    
    def update_graph(self):
        # Clear previous figure
        self.ax.clear()
        self.root_annotations = []  # Clear stored annotations
        
        # Generate x values
        x = np.linspace(self.min_x, self.max_x, self.num_points)
        
        # Evaluate function
        try:
            y = self.function(x)
            
            # Plot function with improved styling
            self.ax.plot(x, y, linewidth=2.5, color='#1f77b4', label=f"f(x) = {self.function_str}")
            
            # Plot x and y axes
            self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
            # Set labels and title with improved styling
            self.ax.set_xlabel("x", fontsize=12)
            self.ax.set_ylabel("f(x)", fontsize=12)
            self.ax.set_title(f"Graph of f(x) = {self.function_str}", fontsize=14, fontweight='bold')
            
            # Set grid color based on dark mode
            grid_color = '#ffffff' if self.use_dark_mode.get() else '#b0b0b0'
            
            # Add grid
            self.ax.grid(True, linestyle='--', alpha=0.7, color=grid_color)
            
            # Set axis limits
            self.ax.set_xlim(self.min_x, self.max_x)
            self.ax.set_ylim(self.min_y, self.max_y)
            
            # Apply dark mode styling if enabled
            if self.use_dark_mode.get():
                self.ax.tick_params(colors='#ffffff')
                self.ax.xaxis.label.set_color('#ffffff')
                self.ax.yaxis.label.set_color('#ffffff')
                self.ax.title.set_color('#ffffff')
                
                # Update axes
                self.ax.spines['bottom'].set_color('#ffffff')
                self.ax.spines['top'].set_color('#ffffff')
                self.ax.spines['left'].set_color('#ffffff')
                self.ax.spines['right'].set_color('#ffffff')
            
            # Use a colormap for multiple roots
            cmap = get_cmap('tab10')
            
            # Mark roots on graph with plain titles above/below the root points
            for i, root in enumerate(self.roots):
                # Plot the root point with a distinct color
                color = cmap(i % 10)
                self.ax.plot(root, 0, 'o', markersize=10, color=color)
                
                # Calculate y-range to determine appropriate offset
                y_range = self.max_y - self.min_y
                
                # Position the annotation directly above or below the root point
                # Alternate between above and below to avoid overlaps
                if i % 2 == 0:
                    y_pos = y_range * 0.05  # 5% of y-axis range above
                else:
                    y_pos = -y_range * 0.05  # 5% of y-axis range below
                
                # Format the root value based on precision setting
                root_text = f"{root:.6f}" if self.use_full_precision.get() else f"{root:.4f}"
                
                # Set annotation background color based on dark mode
                bg_color = '#3d3d3d' if self.use_dark_mode.get() else 'white'
                fg_color = '#ffffff' if self.use_dark_mode.get() else 'black'
                
                # Create annotation with fancy box but no arrow
                annotation = self.ax.annotate(
                    f"Root {i+1}: {root_text}",
                    xy=(root, 0),  # Point to annotate
                    xytext=(root, y_pos),  # Position text directly above/below
                    bbox=dict(
                        boxstyle="round,pad=0.5",
                        facecolor=bg_color,
                        alpha=0.8,
                        edgecolor=color
                    ),
                    ha='center',
                    va='center' if i % 2 == 1 else 'bottom',
                    fontsize=10,
                    color=fg_color,
                    zorder=10 + i  # Base zorder plus index
                )
                
                # Add a subtle outline to make text more readable
                outline_color = 'black' if self.use_dark_mode.get() else 'white'
                annotation.set_path_effects([
                    path_effects.withStroke(linewidth=3, foreground=outline_color)
                ])
                
                # Store annotation for hover effects
                self.root_annotations.append(annotation)
            
            # Add legend with improved styling
            legend = self.ax.legend(loc='best', framealpha=0.9, fontsize=10)
            if self.use_dark_mode.get():
                legend.get_frame().set_facecolor('#3d3d3d')
                legend.get_frame().set_edgecolor('#ffffff')
                for text in legend.get_texts():
                    text.set_color('#ffffff')
            
            # Update canvas
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error plotting function: {str(e)}")
    
    def update_table(self):
        # Clear previous table
        for widget in self.table_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Check if we have iteration data
        if not self.iterations_data:
            no_data_label = ttk.Label(
                self.table_scrollable_frame, 
                text="No iteration data available",
                font=("Segoe UI", 12),
                padding=20
            )
            no_data_label.pack(pady=20)
            return
        
        # Create a section for each root
        for root_index, root_data in enumerate(self.iterations_data):
            # Format the root value based on precision setting
            root_value = root_data['root']
            root_text = f"{root_value:.6f}" if self.use_full_precision.get() else f"{root_value:.4f}"
            
            # Create a frame for this root section
            root_frame = ttk.LabelFrame(
                self.table_scrollable_frame, 
                text=f"Root {root_index+1}: x = {root_text}",
                padding=(10, 5)
            )
            root_frame.pack(fill="x", expand=True, pady=10, padx=5)
            
            # Get the data for this root
            data = root_data['data']
            
            if not data:
                ttk.Label(root_frame, text="No iteration data for this root").pack(pady=5)
                continue
                
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Format numeric values based on precision setting
            formatted_df = df.copy()
            for col in df.columns:
                formatted_df[col] = df[col].apply(self.format_number)
            
            # Create Treeview with full width
            columns = list(formatted_df.columns)
            tree = ttk.Treeview(root_frame, columns=columns, show="headings", height=min(10, len(formatted_df)))
            
            # Configure column widths to fill the available space
            total_width = self.table_frame.winfo_width() - 30  # Subtract some padding
            if total_width <= 0:  # If width not available yet, use a default
                total_width = 800
                
            col_width = total_width // len(columns)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=col_width, anchor=tk.CENTER, stretch=True)
            
            # Set row colors based on dark mode
            if self.use_dark_mode.get():
                tree.tag_configure("even", background="#3d3d3d", foreground="#ffffff")
                tree.tag_configure("odd", background="#2d2d2d", foreground="#ffffff")
            else:
                tree.tag_configure("even", background="#f0f0f0", foreground="#000000")
                tree.tag_configure("odd", background="#ffffff", foreground="#000000")
            
            # Insert data with alternating row colors for better readability
            for i, row in formatted_df.iterrows():
                values = [row[col] for col in columns]
                tag = "even" if i % 2 == 0 else "odd"
                tree.insert("", "end", values=values, tags=(tag,))
            
            # Add horizontal scrollbar
            h_scrollbar = ttk.Scrollbar(root_frame, orient="horizontal", command=tree.xview)
            tree.configure(xscrollcommand=h_scrollbar.set)
            h_scrollbar.pack(side="bottom", fill="x")
            
            # Pack the tree with full width
            tree.pack(fill="both", expand=True, pady=5)
    
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.create_empty_figure()
        self.create_empty_table()
        self.roots = []
        self.iterations_data = []
        self.root_annotations = []
    
    def find_roots(self):
        # Clear previous results
        self.clear_results()
        
        # Parse function
        if not self.parse_function():
            return
        
        # Get parameters
        try:
            x_min = float(self.x_min_var.get())
            x_max = float(self.x_max_var.get())
            tolerance = float(self.tolerance_var.get())
            max_iter = int(self.max_iter_var.get())
            
            # Update graph limits
            self.min_x = x_min
            self.max_x = x_max
            
            # Plot function
            self.update_graph()
            
            # Get selected method
            method = self.method_var.get()
            
            # Show a progress message
            self.results_text.insert(tk.END, f"Applying {method}...\n\n")
            self.master.update_idletasks()  # Update the UI
            
            # Apply selected method
            if method == "Graphical Method":
                self.graphical_method(x_min, x_max)
            elif method == "Incremental Method":
                step_size = float(self.step_size_var.get())
                self.incremental_method(x_min, x_max, step_size, tolerance, max_iter)
            elif method == "Bisection Method":
                self.bisection_method(x_min, x_max, tolerance, max_iter)
            elif method == "Regula Falsi Method":
                self.regula_falsi_method(x_min, x_max, tolerance, max_iter)
            elif method == "Newton-Raphson Method":
                initial_guess = float(self.initial_guess_var.get())
                self.newton_raphson_method(initial_guess, tolerance, max_iter)
            elif method == "Secant Method":
                initial_guess = float(self.initial_guess_var.get())
                second_guess = float(self.second_guess_var.get())
                self.secant_method(initial_guess, second_guess, tolerance, max_iter)
            
            # Update graph with roots
            self.update_graph()
            
            # Update table with iterations data
            self.update_table()
            
            # Switch to the graph tab
            self.tabs.select(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error finding roots: {str(e)}")
    
    def graphical_method(self, x_min, x_max):
        self.results_text.insert(tk.END, "Graphical Method\n")
        self.results_text.insert(tk.END, "----------------\n")
        
        # Generate x values
        x = np.linspace(x_min, x_max, 1000)
        y = self.function(x)
        
        # Find sign changes
        sign_changes = []
        for i in range(1, len(x)):
            if y[i-1] * y[i] <= 0:
                # Linear interpolation to find more accurate root
                root = x[i-1] - y[i-1] * (x[i] - x[i-1]) / (y[i] - y[i-1])
                sign_changes.append(root)
        
        # Display results
        if sign_changes:
            self.results_text.insert(tk.END, f"Found {len(sign_changes)} potential roots:\n")
            for i, root in enumerate(sign_changes):
                f_root = self.function(root)
                
                # Format based on precision setting
                root_text = f"{root:.6f}" if self.use_full_precision.get() else f"{root:.4f}"
                f_root_text = f"{f_root:.6e}" if self.use_full_precision.get() else f"{f_root:.4e}"
                
                self.results_text.insert(tk.END, f"Root {i+1}: x = {root_text}, f(x) = {f_root_text}\n")
                self.roots.append(root)
                # Add empty iteration data for this root
                self.iterations_data.append({
                    'root': root,
                    'data': []  # No iterations for graphical method
                })
        else:
            self.results_text.insert(tk.END, "No roots found in the given interval.\n")
    
    def incremental_method(self, x_min, x_max, step_size, tolerance, max_iter):
        self.results_text.insert(tk.END, "Incremental Method\n")
        self.results_text.insert(tk.END, "-----------------\n")
        
        # Initialize variables
        x = x_min
        roots_found = []
        all_iterations = []
        
        # Loop through the interval
        while x <= x_max:
            f_x = self.function(x)
            
            # Check if f(x) is close to zero
            if abs(f_x) < tolerance:
                roots_found.append(x)
                all_iterations.append({
                    'root': x,
                    'data': []  # No iterations for direct root
                })
                
                # Format based on precision setting
                x_text = f"{x:.6f}" if self.use_full_precision.get() else f"{x:.4f}"
                f_x_text = f"{f_x:.6e}" if self.use_full_precision.get() else f"{f_x:.4e}"
                
                self.results_text.insert(tk.END, f"Root found: x = {x_text}, f(x) = {f_x_text}\n")
                x += step_size
                continue
            
            # Check for sign change
            next_x = x + step_size
            if next_x <= x_max:
                f_next_x = self.function(next_x)
                
                if f_x * f_next_x < 0:
                    # Refine the root using smaller steps
                    x_l = x
                    x_r = next_x
                    
                    iter_data = []
                    iter_count = 0
                    
                    # Format: Iteration, xl, Δx, xu, f(xl), f(xu), f(xl)*f(xu), remarks
                    while iter_count < max_iter:
                        f_xl = self.function(x_l)
                        f_xu = self.function(x_r)
                        delta_x = x_r - x_l
                        product = f_xl * f_xu
                        
                        # Determine remarks
                        if abs(f_xl) < tolerance:
                            remarks = "Converged at xl"
                            break
                        elif abs(f_xu) < tolerance:
                            remarks = "Converged at xu"
                            break
                        elif delta_x < tolerance:
                            remarks = "Interval too small"
                            break
                        else:
                            remarks = ""
                        
                        # Store iteration data
                        iter_data.append({
                            "Iteration": iter_count,
                            "xl": x_l,
                            "Δx": delta_x,
                            "xu": x_r,
                            "f(xl)": f_xl,
                            "f(xu)": f_xu,
                            "f(xl)*f(xu)": product,
                            "Remarks": remarks
                        })
                        
                        # Reduce step size and update interval
                        smaller_step = delta_x / 10
                        
                        # Check where the sign change occurs in the smaller interval
                        x_mid = (x_l + x_r) / 2
                        f_mid = self.function(x_mid)
                        
                        if f_xl * f_mid < 0:
                            x_r = x_mid
                        else:
                            x_l = x_mid
                        
                        iter_count += 1
                        
                        # Check if we've converged
                        if abs(f_mid) < tolerance or delta_x < tolerance:
                            break
                    
                    # Add final iteration with remarks
                    f_xl = self.function(x_l)
                    f_xu = self.function(x_r)
                    delta_x = x_r - x_l
                    product = f_xl * f_xu
                    
                    if abs(f_xl) < tolerance:
                        root = x_l
                        remarks = "Converged at xl"
                    elif abs(f_xu) < tolerance:
                        root = x_r
                        remarks = "Converged at xu"
                    else:
                        root = (x_l + x_r) / 2
                        remarks = "Final approximation"
                    
                    iter_data.append({
                        "Iteration": iter_count,
                        "xl": x_l,
                        "Δx": delta_x,
                        "xu": x_r,
                        "f(xl)": f_xl,
                        "f(xu)": f_xu,
                        "f(xl)*f(xu)": product,
                        "Remarks": remarks
                    })
                    
                    # Add root to the list
                    roots_found.append(root)
                    all_iterations.append({
                        'root': root,
                        'data': iter_data
                    })
                    
                    # Format based on precision setting
                    root_text = f"{root:.6f}" if self.use_full_precision.get() else f"{root:.4f}"
                    f_root_text = f"{self.function(root):.6e}" if self.use_full_precision.get() else f"{self.function(root):.4e}"
                    
                    self.results_text.insert(tk.END, f"Root found: x = {root_text}, f(x) = {f_root_text}\n")
                    self.results_text.insert(tk.END, f"Iterations: {iter_count+1}\n")
            
            # Move to next point
            x += step_size
        
        # Display results
        if roots_found:
            self.results_text.insert(tk.END, f"\nTotal roots found: {len(roots_found)}\n")
            for i, root in enumerate(roots_found):
                # Format based on precision setting
                root_text = f"{root:.6f}" if self.use_full_precision.get() else f"{root:.4f}"
                f_root_text = f"{self.function(root):.6e}" if self.use_full_precision.get() else f"{self.function(root):.4e}"
                
                self.results_text.insert(tk.END, f"Root {i+1}: x = {root_text}, f(x) = {f_root_text}\n")
                self.roots.append(root)
            
            # Store iterations data
            self.iterations_data = all_iterations
        else:
            self.results_text.insert(tk.END, "No roots found in the given interval.\n")
    
    def bisection_method(self, x_min, x_max, tolerance, max_iter):
        self.results_text.insert(tk.END, "Bisection Method\n")
        self.results_text.insert(tk.END, "----------------\n")
        
        # Find intervals with sign changes
        intervals = self.find_sign_change_intervals(x_min, x_max)
        
        if not intervals:
            self.results_text.insert(tk.END, "Error: Function does not change sign in the given interval.\n")
            return
        
        # Process each interval with a sign change
        roots_found = []
        all_iterations = []
        
        for interval_idx, (a, b) in enumerate(intervals):
            # Format based on precision setting
            a_text = f"{a:.6f}" if self.use_full_precision.get() else f"{a:.4f}"
            b_text = f"{b:.6f}" if self.use_full_precision.get() else f"{b:.4f}"
            
            self.results_text.insert(tk.END, f"\nProcessing interval {interval_idx+1}: [{a_text}, {b_text}]\n")
            
            # Initialize variables for this interval
            iterations_data = []
            prev_c = None
            
            # Bisection algorithm
            # Format: Iteration, xl, xr, xu, f(xl), f(xu), |ϵa|,%, f(xl)*f(xu), remarks
            for i in range(max_iter):
                c = (a + b) / 2
                f_a = self.function(a)
                f_b = self.function(b)
                f_c = self.function(c)
                
                # Calculate error
                if prev_c is not None:
                    error = abs((c - prev_c) / c) * 100 if c != 0 else abs(c - prev_c) * 100
                else:
                    error = float('inf')
                
                # Determine remarks
                if abs(f_c) < tolerance:
                    remarks = "Converged by function value"
                elif prev_c is not None and error < tolerance:
                    remarks = "Converged by error tolerance"
                elif i == max_iter - 1:
                    remarks = "Max iterations reached"
                else:
                    remarks = ""
                
                # Store iteration data
                iterations_data.append({
                    "Iteration": i,
                    "xl": a,
                    "xr": c,
                    "xu": b,
                    "f(xl)": f_a,
                    "f(xu)": f_b,
                    "|ϵa|,%": error if prev_c is not None else "N/A",
                    "f(xl)*f(xu)": f_a * f_b,
                    "Remarks": remarks
                })
                
                # Check if we found the root
                if abs(f_c) < tolerance or (prev_c is not None and error < tolerance):
                    # Format based on precision setting
                    c_text = f"{c:.6f}" if self.use_full_precision.get() else f"{c:.4f}"
                    f_c_text = f"{f_c:.6e}" if self.use_full_precision.get() else f"{f_c:.4e}"
                    
                    self.results_text.insert(tk.END, f"Root found: x = {c_text}, f(x) = {f_c_text}\n")
                    self.results_text.insert(tk.END, f"Iterations: {i+1}\n")
                    roots_found.append(c)
                    all_iterations.append({
                        'root': c,
                        'data': iterations_data
                    })
                    break
                
                # Prepare for next iteration
                prev_c = c
                
                # Update interval
                if f_a * f_c < 0:
                    b = c
                else:
                    a = c
            else:
                # If we reach max iterations without convergence
                # Format based on precision setting
                c_text = f"{c:.6f}" if self.use_full_precision.get() else f"{c:.4f}"
                f_c_text = f"{f_c:.6e}" if self.use_full_precision.get() else f"{f_c:.4e}"
                
                self.results_text.insert(tk.END, f"Maximum iterations reached. Last approximation: x = {c_text}, f(x) = {f_c_text}\n")
                roots_found.append(c)
                all_iterations.append({
                    'root': c,
                    'data': iterations_data
                })
        
        # Display summary of results
        if roots_found:
            self.results_text.insert(tk.END, f"\nTotal roots found: {len(roots_found)}\n")
            for i, root in enumerate(roots_found):
                # Format based on precision setting
                root_text = f"{root:.6f}" if self.use_full_precision.get() else f"{root:.4f}"
                f_root_text = f"{self.function(root):.6e}" if self.use_full_precision.get() else f"{self.function(root):.4e}"
                
                self.results_text.insert(tk.END, f"Root {i+1}: x = {root_text}, f(x) = {f_root_text}\n")
                self.roots.append(root)
            
            # Store iterations data
            self.iterations_data = all_iterations
        else:
            self.results_text.insert(tk.END, "No roots found in the given interval.\n")
    
    def find_sign_change_intervals(self, x_min, x_max, num_points=100):
        """Find intervals where the function changes sign."""
        x = np.linspace(x_min, x_max, num_points)
        y = self.function(x)
        
        intervals = []
        for i in range(1, len(x)):
            if y[i-1] * y[i] <= 0:  # Sign change detected
                intervals.append((x[i-1], x[i]))
        
        return intervals
    
    def regula_falsi_method(self, x_min, x_max, tolerance, max_iter):
        self.results_text.insert(tk.END, "Regula Falsi Method (False Position)\n")
        self.results_text.insert(tk.END, "-----------------------------------\n")
        
        # Find intervals with sign changes
        intervals = self.find_sign_change_intervals(x_min, x_max)
        
        if not intervals:
            self.results_text.insert(tk.END, "Error: No sign changes found in the given interval.\n")
            return
        
        roots_found = []
        all_iterations = []
        
        # Process each interval with a sign change
        for interval_idx, (a, b) in enumerate(intervals):
            # Format based on precision setting
            a_text = f"{a:.6f}" if self.use_full_precision.get() else f"{a:.4f}"
            b_text = f"{b:.6f}" if self.use_full_precision.get() else f"{b:.4f}"
            
            self.results_text.insert(tk.END, f"\nProcessing interval {interval_idx+1}: [{a_text}, {b_text}]\n")
            
            # Initialize variables for this interval
            iterations_data = []
            prev_c = None
            
            # Regula Falsi algorithm
            # Format: Iteration, xl, xu, xr, ϵa, f(xl), f(xu), f(xr), f(xl)*f(xr), remarks
            for i in range(max_iter):
                # Calculate c using false position formula
                f_a = self.function(a)
                f_b = self.function(b)
                
                # Check for division by zero
                if abs(f_b - f_a) < 1e-10:
                    self.results_text.insert(tk.END, f"Warning: Division by near zero at iteration {i}. Stopping.\n")
                    break
                
                c = a - f_a * (b - a) / (f_b - f_a)
                f_c = self.function(c)
                
                # Calculate error
                if prev_c is not None:
                    error = abs((c - prev_c) / c) * 100 if c != 0 else abs(c - prev_c) * 100
                else:
                    error = float('inf')
                
                # Determine remarks
                if abs(f_c) < tolerance:
                    remarks = "Converged by function value"
                elif error < tolerance:
                    remarks = "Converged by error tolerance"
                elif i == max_iter - 1:
                    remarks = "Max iterations reached"
                else:
                    remarks = ""
                
                # Store iteration data
                iterations_data.append({
                    "Iteration": i,
                    "xl": a,
                    "xu": b,
                    "xr": c,
                    "ϵa": error if prev_c is not None else "N/A",
                    "f(xl)": f_a,
                    "f(xu)": f_b,
                    "f(xr)": f_c,
                    "f(xl)*f(xr)": f_a * f_c,
                    "Remarks": remarks
                })
                
                # Check if we found the root
                if abs(f_c) < tolerance or (prev_c is not None and error < tolerance):
                    # Format based on precision setting
                    c_text = f"{c:.6f}" if self.use_full_precision.get() else f"{c:.4f}"
                    f_c_text = f"{f_c:.6e}" if self.use_full_precision.get() else f"{f_c:.4e}"
                    
                    self.results_text.insert(tk.END, f"Root found: x = {c_text}, f(x) = {f_c_text}\n")
                    self.results_text.insert(tk.END, f"Iterations: {i+1}\n")
                    roots_found.append(c)
                    all_iterations.append({
                        'root': c,
                        'data': iterations_data
                    })
                    break
                
                # Prepare for next iteration
                prev_c = c
                
                # Update interval
                if f_a * f_c < 0:
                    b = c
                else:
                    a = c
            else:
                # If we reach max iterations without convergence
                # Format based on precision setting
                c_text = f"{c:.6f}" if self.use_full_precision.get() else f"{c:.4f}"
                f_c_text = f"{f_c:.6e}" if self.use_full_precision.get() else f"{f_c:.4e}"
                
                self.results_text.insert(tk.END, f"Maximum iterations reached. Last approximation: x = {c_text}, f(x) = {f_c_text}\n")
                roots_found.append(c)
                all_iterations.append({
                    'root': c,
                    'data': iterations_data
                })
        
        # Display summary of results
        if roots_found:
            self.results_text.insert(tk.END, f"\nTotal roots found: {len(roots_found)}\n")
            for i, root in enumerate(roots_found):
                # Format based on precision setting
                root_text = f"{root:.6f}" if self.use_full_precision.get() else f"{root:.4f}"
                f_root_text = f"{self.function(root):.6e}" if self.use_full_precision.get() else f"{self.function(root):.4e}"
                
                self.results_text.insert(tk.END, f"Root {i+1}: x = {root_text}, f(x) = {f_root_text}\n")
                self.roots.append(root)
            
            # Store iterations data
            self.iterations_data = all_iterations
        else:
            self.results_text.insert(tk.END, "No roots found in the given interval.\n")
    
    def newton_raphson_method(self, initial_guess, tolerance, max_iter):
        self.results_text.insert(tk.END, "Newton-Raphson Method\n")
        self.results_text.insert(tk.END, "---------------------\n")
        
        # Initialize variables
        x = initial_guess
        iterations_data = []
        
        # Newton-Raphson algorithm
        # Format: Iteration, xl, ϵa, f(x), f'(xu)
        for i in range(max_iter):
            f_x = self.function(x)
            f_prime_x = self.derivative(x)
            
            # Check if derivative is close to zero
            if abs(f_prime_x) < 1e-10:
                # Format based on precision setting
                x_text = f"{x:.6f}" if self.use_full_precision.get() else f"{x:.4f}"
                
                self.results_text.insert(tk.END, f"Error: Derivative is close to zero at x = {x_text}\n")
                break
            
            # Calculate next approximation
            next_x = x - f_x / f_prime_x
            
            # Calculate error
            error = abs((next_x - x) / next_x) * 100 if next_x != 0 else abs(next_x - x) * 100
            
            # Store iteration data
            iterations_data.append({
                "Iteration": i,
                "xl": x,
                "ϵa": error,
                "f(x)": f_x,
                "f'(xu)": f_prime_x
            })
            
            # Check if we found the root
            if abs(f_x) < tolerance or error < tolerance:
                # Format based on precision setting
                next_x_text = f"{next_x:.6f}" if self.use_full_precision.get() else f"{next_x:.4f}"
                f_next_x_text = f"{self.function(next_x):.6e}" if self.use_full_precision.get() else f"{self.function(next_x):.4e}"
                
                self.results_text.insert(tk.END, f"Root found: x = {next_x_text}, f(x) = {f_next_x_text}\n")
                self.results_text.insert(tk.END, f"Iterations: {i+1}\n")
                self.roots.append(next_x)
                self.iterations_data.append({
                    'root': next_x,
                    'data': iterations_data
                })
                break
            
            # Update x for next iteration
            x = next_x
        else:
            # Format based on precision setting
            x_text = f"{x:.6f}" if self.use_full_precision.get() else f"{x:.4f}"
            f_x_text = f"{self.function(x):.6e}" if self.use_full_precision.get() else f"{self.function(x):.4e}"
            
            self.results_text.insert(tk.END, f"Maximum iterations reached. Last approximation: x = {x_text}, f(x) = {f_x_text}\n")
            self.roots.append(x)
            self.iterations_data.append({
                'root': x,
                'data': iterations_data
            })
    
    def secant_method(self, x0, x1, tolerance, max_iter):
        self.results_text.insert(tk.END, "Secant Method\n")
        self.results_text.insert(tk.END, "-------------\n")
        
        # Initialize variables
        iterations_data = []
        
        # Secant algorithm
        # Format: Iteration, xi-1, xi, xi+1, ϵa, f(xi-1), f(xi), f(xi+1)
        for i in range(max_iter):
            f_x0 = self.function(x0)
            f_x1 = self.function(x1)
            
            # Check if denominator is close to zero
            if abs(f_x1 - f_x0) < 1e-10:
                self.results_text.insert(tk.END, f"Error: Division by near zero at iteration {i}\n")
                break
            
            # Calculate next approximation
            x2 = x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)
            f_x2 = self.function(x2)
            
            # Calculate error
            error = abs((x2 - x1) / x2) * 100 if x2 != 0 else abs(x2 - x1) * 100
            
            # Store iteration data
            iterations_data.append({
                "Iteration": i,
                "xi-1": x0,
                "xi": x1,
                "xi+1": x2,
                "ϵa": error,
                "f(xi-1)": f_x0,
                "f(xi)": f_x1,
                "f(xi+1)": f_x2
            })
            
            # Check if we found the root
            if abs(f_x2) < tolerance or error < tolerance:
                # Format based on precision setting
                x2_text = f"{x2:.6f}" if self.use_full_precision.get() else f"{x2:.4f}"
                f_x2_text = f"{f_x2:.6e}" if self.use_full_precision.get() else f"{f_x2:.4e}"
                
                self.results_text.insert(tk.END, f"Root found: x = {x2_text}, f(x) = {f_x2_text}\n")
                self.results_text.insert(tk.END, f"Iterations: {i+1}\n")
                self.roots.append(x2)
                self.iterations_data.append({
                    'root': x2,
                    'data': iterations_data
                })
                break
            
            # Update values for next iteration
            x0 = x1
            x1 = x2
        else:
            # Format based on precision setting
            x1_text = f"{x1:.6f}" if self.use_full_precision.get() else f"{x1:.4f}"
            f_x1_text = f"{self.function(x1):.6e}" if self.use_full_precision.get() else f"{self.function(x1):.4e}"
            
            self.results_text.insert(tk.END, f"Maximum iterations reached. Last approximation: x = {x1_text}, f(x) = {f_x1_text}\n")
            self.roots.append(x1)
            self.iterations_data.append({
                'root': x1,
                'data': iterations_data
            })

# Main function
def main():
    root = tk.Tk()
    app = NumericalMethods(root)
    root.mainloop()

if __name__ == "__main__":
    main()