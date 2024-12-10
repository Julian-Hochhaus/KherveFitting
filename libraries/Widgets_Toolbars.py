# In libraries/Widgets_Toolbars.py
import os
import sys
import wx
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from libraries.Sheet_Operations import CheckboxRenderer
from libraries.Open import ExcelDropTarget, open_xlsx_file
from libraries.Plot_Operations import PlotManager
from Functions import toggle_Col_1
from libraries.Save import update_undo_redo_state
from libraries.Save import save_peaks_library, load_peaks_library
from libraries.Open import open_vamas_file_dialog, open_kal_file_dialog, import_mrs_file, open_spe_file_dialog
from libraries.Export import export_word_report
from libraries.Help import show_libraries_used
from Functions import (import_avantage_file, on_save, save_all_sheets_with_plots, save_results_table, open_avg_file,
                       import_multiple_avg_files, create_plot_script_from_excel, on_save_plot, \
    on_save_plot_pdf, on_save_plot_svg, on_exit, undo, redo, toggle_plot, show_shortcuts, show_mini_game, on_about)
from libraries.Utilities import add_draggable_text


from Functions import refresh_sheets, on_sheet_selected_wrapper, toggle_plot, on_save, on_save_plot, on_save_all_sheets, toggle_Col_1, undo, redo



def create_widgets(window):
    # Main sizer
    main_sizer = wx.BoxSizer(wx.HORIZONTAL)

    # Create the vertical toolbar as a child of the panel
    window.v_toolbar = create_vertical_toolbar(window.panel, window)

    # Content sizer (everything except vertical toolbar)
    content_sizer = wx.BoxSizer(wx.HORIZONTAL)

    # Create a splitter window
    window.splitter = wx.SplitterWindow(window.panel, style=wx.SP_LIVE_UPDATE)

    # Right frame for the plot
    window.right_frame = wx.Panel(window.splitter)
    window.right_frame.SetBackgroundColour(wx.Colour(255, 255, 255))
    right_frame_sizer = wx.BoxSizer(wx.VERTICAL)

    # Create the FigureCanvas
    window.canvas = FigureCanvas(window.right_frame, -1, window.figure)

    # Set up drag and drop for Excel files
    file_drop_target = ExcelDropTarget(window)
    window.canvas.SetDropTarget(file_drop_target)

    plt.tight_layout()
    right_frame_sizer.Add(window.canvas, 1, wx.EXPAND | wx.ALL, 0)

    # Initialize plot_manager
    window.plot_manager = PlotManager(window.ax, window.canvas)
    window.plot_manager.plot_initial_logo()

    # Update plot manager with loaded or default values
    window.update_plot_preferences()

    # Create a hidden NavigationToolbar
    window.navigation_toolbar = NavigationToolbar(window.canvas)
    window.navigation_toolbar.Hide()

    window.right_frame.SetSizer(right_frame_sizer)

    # Create grids panel
    grids_panel = create_grids_panel(window)

    # Set up the splitter
    window.splitter.SplitVertically(window.right_frame, grids_panel)
    window.splitter.SetMinimumPaneSize(0)
    window.splitter.SetSashGravity(0.5)

    # Set initial sash position
    window.initial_sash_position = 800
    window.splitter.SetSashPosition(window.initial_sash_position)

    # Add splitter to content sizer
    content_sizer.Add(window.splitter, 1, wx.EXPAND | wx.ALL, 5)

    # Add vertical toolbar and content sizer to main sizer
    main_sizer.Add(window.v_toolbar, 0, wx.EXPAND)
    main_sizer.Add(content_sizer, 1, wx.EXPAND)

    window.panel.SetSizer(main_sizer)

    # Create the horizontal toolbar
    window.toolbar = create_horizontal_toolbar(window)
    update_undo_redo_state(window)
    toggle_Col_1(window)

    # Bind events
    bind_events_widgets(window)


def create_grids_panel(window):
    grids_panel = wx.Panel(window.splitter)
    grids_sizer = wx.BoxSizer(wx.VERTICAL)

    # Create peak params grid
    peak_params_sizer = create_peak_params_grid(window, grids_panel)
    grids_sizer.Add(peak_params_sizer, 1, wx.EXPAND | wx.ALL, 5)

    # Create results grid
    results_sizer = create_results_grid(window, grids_panel)
    grids_sizer.Add(results_sizer, 1, wx.EXPAND | wx.ALL, 5)

    grids_panel.SetSizer(grids_sizer)
    return grids_panel


def create_peak_params_grid(window, parent):
    peak_params_frame_box = wx.StaticBox(parent, label="Peak Fitting Parameters")
    peak_params_sizer = wx.StaticBoxSizer(peak_params_frame_box, wx.VERTICAL)

    window.peak_params_frame = wx.Panel(peak_params_frame_box)
    window.peak_params_frame.SetBackgroundColour(wx.Colour(255, 255, 255))
    peak_params_sizer_inner = wx.BoxSizer(wx.VERTICAL)

    window.peak_params_grid = wx.grid.Grid(window.peak_params_frame)
    window.peak_params_grid.CreateGrid(0, 19)

    # Set column labels and sizes
    column_labels = ["ID", "Peak\nLabel", "Position\n(eV)", "Height\n(CPS)", "FWHM\n(eV)", "\u03c3/\u03b3 (%)\nL/G \n", "Area\n(CPS.eV)",
                     "\u03c3\nW_g", "\u03b3\nW_l", "W_g\nSkew",
                     "Conc.\n(%)", "A/A\u1D00", "Split\n(eV)", "Fitting Model", "Bkg Type", "Bkg Low\n(eV)",
                     "Bkg High\n(eV)", "Bkg Offset Low\n(CPS)", "Bkg Offset High\n(CPS)"]
    for i, label in enumerate(column_labels):
        window.peak_params_grid.SetColLabelValue(i, label)


    # Set grid properties
    default_row_size = 25
    window.peak_params_grid.SetDefaultRowSize(default_row_size)
    window.peak_params_grid.SetColLabelSize(35)
    window.peak_params_grid.SetDefaultColSize(60)
    # window.peak_params_grid.SetLabelBackgroundColour(wx.Colour(230, 250, 230))  # Green background for column labels
    window.peak_params_grid.SetDefaultCellBackgroundColour(wx.WHITE)  # White background for all cells
    window.peak_params_grid.SetRowLabelSize(25)

    # Ensure all cells have white background
    for row in range(window.peak_params_grid.GetNumberRows()):
        for col in range(window.peak_params_grid.GetNumberCols()):
            window.peak_params_grid.SetCellBackgroundColour(row, col, wx.WHITE)


    # Adjust individual column sizes
    col_sizes = [20, 90, 80, 80, 60, 50, 60, 60, 60, 60, 40, 40, 40, 130, 130, 80, 80, 100, 100]
    for i, size in enumerate(col_sizes):
        window.peak_params_grid.SetColSize(i, size)

    peak_params_sizer_inner.Add(window.peak_params_grid, 1, wx.EXPAND | wx.ALL, 5)
    window.peak_params_frame.SetSizer(peak_params_sizer_inner)
    peak_params_sizer.Add(window.peak_params_frame, 1, wx.EXPAND | wx.ALL, 5)

    return peak_params_sizer


def create_results_grid(window, parent):
    results_frame_box = wx.StaticBox(parent, label="Results")
    results_sizer = wx.StaticBoxSizer(results_frame_box, wx.VERTICAL)

    window.results_frame = wx.Panel(results_frame_box)
    results_sizer_inner = wx.BoxSizer(wx.VERTICAL)

    window.results_grid = wx.grid.Grid(window.results_frame)
    window.results_grid.CreateGrid(0, 29)

    # Set column labels and properties for results grid
    column_labels = ["Peak\nLabel", "Position\n(eV)", "Height\n(CPS)", "FWHM\n(eV)", "L/G \n\u03c3/\u03b3 (%)",
                     "Area\n(CPS.eV)", "Atomic\n(%)", " ", "RSF", "TXFN", "ECF", "Instr.","Fitting Model",
                     "Norm. Area\n An (a.u.)",
                     "\u03c3 or \u03B1\nW_g", "\u03b3 or \u03B2\nW_l", "Bkg Type", "Bkg Low\n(eV)", "Bkg High\n(eV)", "Bkg Offset Low\n(CPS)",
                     "Bkg Offset High\n(CPS)", "Sheetname", "Position\nConstraint", "Height\nConstraint",
                     "FWHM\nConstraint", "L/G\nConstraint", "Area\nConstraint", "\u03c3\nConstraint",
                     "\u03b3\nConstraint"]
    for i, label in enumerate(column_labels):
        window.results_grid.SetColLabelValue(i, label)

    window.results_grid.SetDefaultRowSize(25)
    window.results_grid.SetDefaultColSize(60)
    window.results_grid.SetRowLabelSize(25)
    window.results_grid.SetColLabelSize(35)
    # window.results_grid.SetLabelBackgroundColour(wx.Colour(255, 255, 255))
    window.results_grid.SetDefaultCellBackgroundColour(wx.WHITE)

    # Adjust specific column sizes
    col_sizes = [120, 70, 70, 70, 50, 80, 80, 20, 30, 40, 50, 80,120, 80, 80, 70, 70, 100, 100, 80, 80, 80, 120, 120,
                 120,
                 70,70,70]
    for i, size in enumerate(col_sizes):
        window.results_grid.SetColSize(i, size)

    # Set renderer for checkbox column
    checkbox_renderer = CheckboxRenderer()
    for row in range(window.results_grid.GetNumberRows()):
        window.results_grid.SetCellRenderer(row, 7, checkbox_renderer)

    results_sizer_inner.Add(window.results_grid, 1, wx.EXPAND | wx.ALL, 5)
    window.results_frame.SetSizer(results_sizer_inner)
    results_sizer.Add(window.results_frame, 1, wx.EXPAND | wx.ALL, 5)

    return results_sizer


def bind_events_widgets(window):
    window.results_grid.Bind(wx.EVT_KEY_DOWN, window.on_key_down)
    window.peak_params_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, window.on_grid_select)
    window.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, window.on_splitter_changed)
    window.results_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, window.on_checkbox_update)
    window.canvas.mpl_connect('button_release_event', window.on_plot_mouse_release)
    window.peak_params_grid.Bind(wx.EVT_LEFT_UP, window.on_peak_params_mouse_release)



def create_menu(window):
    menubar = wx.MenuBar()

    # Create menus
    file_menu = wx.Menu()
    import_menu = wx.Menu()
    export_menu = wx.Menu()
    edit_menu = wx.Menu()
    view_menu = wx.Menu()
    tools_menu = wx.Menu()
    help_menu = wx.Menu()
    save_menu = wx.Menu()

    # File menu items
    open_item = file_menu.Append(wx.ID_OPEN, "Open \tCtrl+O")
    window.Bind(wx.EVT_MENU, lambda event: open_xlsx_file(window), open_item)

    save_Excel_item = file_menu.Append(wx.ID_SAVE, "Save Sheet \tCtrl+S")
    window.Bind(wx.EVT_MENU, lambda event: on_save(window), save_Excel_item)

    # Save submenu items
    save_all_item = save_menu.Append(wx.NewId(), "Save All")
    window.Bind(wx.EVT_MENU, lambda event: save_all_sheets_with_plots(window), save_all_item)

    save_Excel_item2 = save_menu.Append(wx.NewId(), "Save Sheet")
    window.Bind(wx.EVT_MENU, lambda event: on_save(window), save_Excel_item2)

    save_Table_item = save_menu.Append(wx.NewId(), "Save Results Table")
    window.Bind(wx.EVT_MENU, lambda event: save_results_table(window), save_Table_item)

    file_menu.AppendSubMenu(save_menu, "Save")

    # Import submenu items
    import_vamas_item = import_menu.Append(wx.NewId(), "Import Vamas Data file (.vms)")
    window.Bind(wx.EVT_MENU, lambda event: open_vamas_file_dialog(window), import_vamas_item)

    import_avantage_item = import_menu.Append(wx.NewId(), "Import Avantage Data file (.xlsx)")
    window.Bind(wx.EVT_MENU, lambda event: import_avantage_file(window), import_avantage_item)

    import_kal_item = import_menu.Append(wx.NewId(), "Import Kratos Data file (.kal)")
    window.Bind(wx.EVT_MENU, lambda event: open_kal_file_dialog(window), import_kal_item)

    import_spe_item = import_menu.Append(wx.NewId(), "Import Phi Data file (.spe)")
    window.Bind(wx.EVT_MENU, lambda event: open_spe_file_dialog(window), import_spe_item)

    import_mrs_item = import_menu.Append(wx.NewId(), "Import MRS Data file (.mrs)")
    window.Bind(wx.EVT_MENU, lambda event: import_mrs_file(window), import_mrs_item)

    import_avg_item = import_menu.Append(wx.NewId(), "Import AVG file (.avg)")
    window.Bind(wx.EVT_MENU, lambda event: open_avg_file(window), import_avg_item)

    import_multiple_avg_item = import_menu.Append(wx.NewId(), "Import Multiple AVG files (folder)")
    window.Bind(wx.EVT_MENU, lambda event: import_multiple_avg_files(window), import_multiple_avg_item)

    # Export submenu items
    export_python_plot_item = export_menu.Append(wx.NewId(), "Python Plot")
    window.Bind(wx.EVT_MENU, lambda event: create_plot_script_from_excel(window), export_python_plot_item)

    save_plot_item = export_menu.Append(wx.NewId(), "Export as PNG")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot(window), save_plot_item)

    save_plot_item_pdf = export_menu.Append(wx.NewId(), "Export as PDF")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot_pdf(window), save_plot_item_pdf)

    save_plot_item_svg = export_menu.Append(wx.NewId(), "Export as SVG")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot_svg(window), save_plot_item_svg)

    export_menu.AppendSeparator()
    word_report_item = export_menu.Append(wx.NewId(), "Create Report (.docx)")
    window.Bind(wx.EVT_MENU, lambda event: export_word_report(window), word_report_item)

    # Recent files submenu
    window.recent_files_menu = wx.Menu()
    file_menu.AppendSubMenu(window.recent_files_menu, "Recent Files")

    # Append submenus to file menu
    file_menu.AppendSubMenu(import_menu, "Import")
    file_menu.AppendSubMenu(export_menu, "Export")

    # Exit item
    file_menu.AppendSeparator()
    exit_item = file_menu.Append(wx.ID_EXIT, "Exit\tCtrl+Q")
    window.Bind(wx.EVT_MENU, lambda event: on_exit(window, event), exit_item)

    # Edit menu items
    undo_item = edit_menu.Append(wx.ID_UNDO, "Undo\tCtrl+Z")
    redo_item = edit_menu.Append(wx.ID_REDO, "Redo\tCtrl+Y")
    window.Bind(wx.EVT_MENU, lambda event: undo(window), undo_item)
    window.Bind(wx.EVT_MENU, lambda event: redo(window), redo_item)
    edit_menu.AppendSeparator()

    preferences_item = edit_menu.Append(wx.ID_PREFERENCES, "Preferences")
    window.Bind(wx.EVT_MENU, window.on_preferences, preferences_item)

    # View menu items
    ToggleFitting_item = view_menu.Append(wx.NewId(), "Toggle Peak Fitting")
    window.Bind(wx.EVT_MENU, lambda event: toggle_plot(window), ToggleFitting_item)

    ToggleLegend_item = view_menu.Append(wx.NewId(), "Toggle Legend")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_legend(), ToggleLegend_item)

    ToggleFit_item = view_menu.Append(wx.NewId(), "Toggle Fit Results")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_fitting_results(), ToggleFit_item)

    ToggleRes_item = view_menu.Append(wx.NewId(), "Toggle Residuals")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_residuals(), ToggleRes_item)

    toggle_energy_item = view_menu.AppendCheckItem(wx.NewId(), "Show Kinetic Energy\tCtrl+B")
    window.Bind(wx.EVT_MENU, lambda event: window.toggle_energy_scale(), toggle_energy_item)
    window.toggle_energy_item = toggle_energy_item

    # Tools menu items
    Area_item = tools_menu.Append(wx.NewId(), "Calculate Area Under Curve\tCtrl+A")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_background_window(), Area_item)

    Fitting_item = tools_menu.Append(wx.NewId(), "Create Peak Model\tCtrl+P")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_fitting_window(), Fitting_item)

    Dparam_item = tools_menu.Append(wx.NewId(), "D-parameter\tCtrl+D")
    window.Bind(wx.EVT_MENU, window.on_differentiate, Dparam_item)

    ID_item = tools_menu.Append(wx.NewId(), "Element ID\tCtrl+I")
    window.Bind(wx.EVT_MENU, window.open_periodic_table, ID_item)

    Noise_item = tools_menu.Append(wx.NewId(), "Noise Analysis")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_noise_analysis_window, Noise_item)

    # Help menu items
    # mini_help_item = help_menu.Append(wx.NewId(), "Help")
    # window.Bind(wx.EVT_MENU, window.on_mini_help, mini_help_item)

    manual_item = help_menu.Append(wx.NewId(), "Open Manual\tCtrl+M")
    window.Bind(wx.EVT_MENU, lambda event: open_manual(window), manual_item)

    yt_videos_item = help_menu.Append(wx.NewId(), "KherveFitting Videos")
    window.Bind(wx.EVT_MENU, lambda event: webbrowser.open("https://www.youtube.com/@xpsexamples-imperialcolleg6571"),
                yt_videos_item)

    shortcuts_item = help_menu.Append(wx.NewId(), "List of Shortcuts\tCtrl+K")
    window.Bind(wx.EVT_MENU, lambda event: show_shortcuts(window), shortcuts_item)

    mini_game_item = help_menu.Append(wx.NewId(), "Mini Game")
    window.Bind(wx.EVT_MENU, lambda event: show_mini_game(window), mini_game_item)

    coffee_item = help_menu.Append(wx.NewId(), "Buy Me a Coffee")
    window.Bind(wx.EVT_MENU, lambda event: webbrowser.open("https://buymeacoffee.com/gkerherve"), coffee_item)

    libraries_item = help_menu.Append(wx.NewId(), "Libraries Used")
    window.Bind(wx.EVT_MENU, lambda event: show_libraries_used(window), libraries_item)

    about_item = help_menu.Append(wx.ID_ABOUT, "About")
    window.Bind(wx.EVT_MENU, lambda event: on_about(window, event), about_item)



    # Add menus to menubar
    menubar.Append(file_menu, "&File")
    menubar.Append(edit_menu, "&Edit")
    menubar.Append(view_menu, "&View")
    menubar.Append(tools_menu, "&Tools")
    menubar.Append(help_menu, "&Help")

    window.SetMenuBar(menubar)

def create_horizontal_toolbar(window):
    toolbar = window.CreateToolBar()
    toolbar.SetBackgroundColour(wx.Colour(220, 220, 220))
    toolbar.SetToolBitmapSize(wx.Size(25, 25))

    # # Determine the correct path for icons
    # if getattr(sys, 'frozen', False):
    #     application_path = sys._MEIPASS
    # else:
    #     application_path = os.path.dirname(os.path.abspath(__file__))
    # icon_path = os.path.join(application_path, "Icons")
    # Get the correct path for icons

    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "Icons")

    separators = []

    # File operations
    open_file_tool = toolbar.AddTool(wx.ID_ANY, 'Open File', wx.Bitmap(os.path.join(icon_path, "open-folder-25-green.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open File\tCtrl+O")
    refresh_folder_tool = toolbar.AddTool(wx.ID_ANY, 'Refresh Excel File', wx.Bitmap(os.path.join(icon_path, "refresh-96g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Refresh Excel File")
    save_tool = toolbar.AddTool(wx.ID_ANY, 'Save', wx.Bitmap(os.path.join(icon_path, "save-Excel-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save the Fitted Results to Excel for this Core Level \tCtrl+S")
    save_plot_tool = toolbar.AddTool(wx.ID_ANY, 'Save Plot', wx.Bitmap(os.path.join(icon_path, "save-PNG-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save this Figure to Excel")
    save_all_tool = toolbar.AddTool(wx.ID_ANY, 'Save All Sheets', wx.Bitmap(os.path.join(icon_path, "save-Multi-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save all sheets with plots")

    toolbar.AddSeparator()
    window.undo_tool = toolbar.AddTool(wx.ID_ANY, 'Undo', wx.Bitmap(os.path.join(icon_path, "undo-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Undo -- For peaks properties only")
    window.redo_tool = toolbar.AddTool(wx.ID_ANY, 'Redo', wx.Bitmap(os.path.join(icon_path, "redo-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Redo -- For peaks properties only")
    toolbar.AddSeparator()

    # Skip rows spinbox
    window.skip_rows_spinbox = wx.SpinCtrl(toolbar, min=0, max=200, initial=0, size=(60, -1))
    window.skip_rows_spinbox.SetToolTip("Set the number of rows to skip in the sheet of the Excel file")
    toolbar.AddControl(window.skip_rows_spinbox)

    # Sheet selection
    window.sheet_combobox = wx.ComboBox(toolbar, style=wx.CB_READONLY)
    window.sheet_combobox.SetToolTip("Select Sheet")
    toolbar.AddControl(window.sheet_combobox)
    window.sheet_combobox.Bind(wx.EVT_COMBOBOX, lambda event: on_sheet_selected(window, event))

    toolbar.AddSeparator()
    add_vertical_separator(toolbar, separators)
    toolbar.AddSeparator()

    # BE correction
    window.be_correction_spinbox = wx.SpinCtrlDouble(toolbar, value='0.00', min=-20.00, max=20.00, inc=0.01, size=(70, -1))
    window.be_correction_spinbox.SetDigits(2)
    window.be_correction_spinbox.SetToolTip("BE Correction")
    toolbar.AddControl(window.be_correction_spinbox)

    auto_be_button = toolbar.AddTool(wx.ID_ANY, 'Auto BE', wx.Bitmap(os.path.join(icon_path, "BEcorrect-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Automatic binding energy correction")

    toolbar.AddSeparator()
    add_vertical_separator(toolbar, separators)
    toolbar.AddSeparator()

    # Plot adjustment tools
    plot_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Plot', wx.Bitmap(os.path.join(icon_path, "scatter-plot-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle between Raw Data and Fit")
    toggle_peak_fill_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Peak Fill', wx.Bitmap(os.path.join(icon_path, "STO-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Peak Fill")
    toggle_y_axis_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Y Axis', wx.Bitmap(os.path.join(icon_path, "Y-25.png"),
                                                                               wx.BITMAP_TYPE_PNG), shortHelp="Toggle Y Axis Label and Values")
    toggle_legend_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Legend', wx.Bitmap(os.path.join(icon_path, "Legend-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Legend")
    toggle_fit_results_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Fit Results', wx.Bitmap(os.path.join(icon_path, "ToggleFit-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Fit Results")
    toggle_residuals_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Residuals', wx.Bitmap(os.path.join(icon_path, "Res-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Residuals")

    toolbar.AddSeparator()
    add_vertical_separator(toolbar, separators)
    toolbar.AddSeparator()

    # Analysis tools
    bkg_tool = toolbar.AddTool(wx.ID_ANY, 'Background', wx.Bitmap(os.path.join(icon_path, "BKG-25.png"),
                                                                  wx.BITMAP_TYPE_PNG), shortHelp="Calculate Area "
                                                                                                 "Under Curve\tCtrl+A")
    fitting_tool = toolbar.AddTool(wx.ID_ANY, 'Fitting', wx.Bitmap(os.path.join(icon_path, "C1s-25.png"),
                                                                   wx.BITMAP_TYPE_PNG), shortHelp="Create Peaks "
                                                                                                  "Model \tCtrl+P")

    diff_tool = toolbar.AddTool(wx.ID_ANY, 'Differentiate',
                                wx.Bitmap(os.path.join(icon_path, "Dpara-25.png"), wx.BITMAP_TYPE_PNG),
                                shortHelp="D-parameter Calculation")

    noise_analysis_tool = toolbar.AddTool(wx.ID_ANY, 'Noise Analysis', wx.Bitmap(os.path.join(icon_path, "Noise-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open Noise Analysis Window")

    # toolbar.AddSeparator()
    # add_vertical_separator(toolbar, separators)
    # toolbar.AddSeparator()

    id_tool = toolbar.AddTool(wx.ID_ANY, 'ID', wx.Bitmap(os.path.join(icon_path, "ID-25.png"), wx.BITMAP_TYPE_PNG),
                              shortHelp="Element identifications (ID)")



    window.Bind(wx.EVT_TOOL, window.on_differentiate, diff_tool)


    toolbar.AddStretchableSpace()

    # Export and toggle tools
    save_peaks_tool = toolbar.AddTool(wx.ID_ANY, 'Save Peaks Library',
                                      wx.Bitmap(os.path.join(icon_path, "LibSave.png"), wx.BITMAP_TYPE_PNG),
                                      shortHelp="Save peaks parameters to library")

    open_peaks_tool = toolbar.AddTool(wx.ID_ANY, 'Open Peaks Library',
                                      wx.Bitmap(os.path.join(icon_path, "LibOpen.png"), wx.BITMAP_TYPE_PNG),
                                      shortHelp="Load peaks parameters from library")
    export_tool = toolbar.AddTool(wx.ID_ANY, 'Export Results', wx.Bitmap(os.path.join(icon_path, "Export-25g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Export to Results Grid")
    toggle_Col_1_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Residuals', wx.Bitmap(os.path.join(icon_path, "HideColumn-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Columns Peak Fitting Parameters")
    window.toggle_right_panel_tool = window.add_toggle_tool(toolbar, "Toggle Right Panel", wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR))

    toolbar.Realize()

    # Bind events
    bind_toolbar_events(window, open_file_tool, refresh_folder_tool, plot_tool, bkg_tool, fitting_tool, noise_analysis_tool,
                        toggle_legend_tool, toggle_fit_results_tool, toggle_residuals_tool, save_tool, save_plot_tool,
                        save_all_tool, toggle_Col_1_tool, export_tool, auto_be_button, toggle_peak_fill_tool, id_tool)
    toolbar.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_y_axis(), toggle_y_axis_tool)
    window.Bind(wx.EVT_TOOL, lambda event: save_peaks_library(window), save_peaks_tool)
    window.Bind(wx.EVT_TOOL, lambda event: load_peaks_library(window), open_peaks_tool)

    return toolbar

def add_vertical_separator(toolbar, separators):
    separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    separators[-1].SetSize((2, 24))
    toolbar.AddControl(separators[-1])

def bind_toolbar_events(window, open_file_tool, refresh_folder_tool, plot_tool, bkg_tool, fitting_tool, noise_analysis_tool,
                        toggle_legend_tool, toggle_fit_results_tool, toggle_residuals_tool, save_tool, save_plot_tool,
                        save_all_tool, toggle_Col_1_tool, export_tool, auto_be_button, toggle_peak_fill_tool, id_tool):
    window.Bind(wx.EVT_TOOL, lambda event: open_xlsx_file(window), open_file_tool)
    window.Bind(wx.EVT_TOOL, lambda event: refresh_sheets(window, on_sheet_selected_wrapper), refresh_folder_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_plot(window), plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_background_window(), bkg_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_fitting_window(), fitting_tool)
    window.Bind(wx.EVT_TOOL, window.on_open_noise_analysis_window, noise_analysis_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_legend(), toggle_legend_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_fitting_results(), toggle_fit_results_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_residuals(), toggle_residuals_tool)
    window.sheet_combobox.Bind(wx.EVT_COMBOBOX, lambda event: on_sheet_selected_wrapper(window, event))
    window.Bind(wx.EVT_TOOL, lambda event: on_save(window), save_tool)
    window.Bind(wx.EVT_TOOL, lambda event: on_save_plot(window), save_plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: on_save_all_sheets(window, event), save_all_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_Col_1(window), toggle_Col_1_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.export_results(), export_tool)
    window.be_correction_spinbox.Bind(wx.EVT_SPINCTRLDOUBLE, window.on_be_correction_change)
    window.Bind(wx.EVT_TOOL, window.on_auto_be, auto_be_button)
    window.Bind(wx.EVT_TOOL, window.on_toggle_peak_fill, toggle_peak_fill_tool)
    window.Bind(wx.EVT_TOOL, lambda event: undo(window), window.undo_tool)
    window.Bind(wx.EVT_TOOL, lambda event: redo(window), window.redo_tool)
    window.Bind(wx.EVT_TOOL, window.open_periodic_table, id_tool)
    window.Bind(wx.EVT_TOOL, window.on_toggle_right_panel, window.toggle_right_panel_tool)


def create_vertical_toolbar(parent, frame):
    v_toolbar = wx.ToolBar(parent, style=wx.TB_VERTICAL | wx.TB_FLAT)
    v_toolbar.SetBackgroundColour(wx.Colour(220, 220, 220))
    v_toolbar.SetToolBitmapSize(wx.Size(25, 25))

    # Get the correct path for icons
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "Icons")

    # Zoom tools
    zoom_in_tool = v_toolbar.AddTool(wx.ID_ANY, 'Zoom In',
                                     wx.Bitmap(os.path.join(icon_path, "ZoomIN-25.png"), wx.BITMAP_TYPE_PNG),
                                     shortHelp="Zoom In")
    zoom_out_tool = v_toolbar.AddTool(wx.ID_ANY, 'Zoom Out',
                                      wx.Bitmap(os.path.join(icon_path, "ZoomOUT-25.png"), wx.BITMAP_TYPE_PNG),
                                      shortHelp="Zoom Out")
    drag_tool = v_toolbar.AddTool(wx.ID_ANY, 'Drag',
                                  wx.Bitmap(os.path.join(icon_path, "drag-25.png"), wx.BITMAP_TYPE_PNG),
                                  shortHelp="Drag Plot")

    v_toolbar.AddSeparator()

    # BE adjustment tools
    high_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE +',
                                              wx.Bitmap(os.path.join(icon_path, "Right-Red-25g.png"), wx.BITMAP_TYPE_PNG),
                                              shortHelp="Decrease High BE")
    high_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE -',
                                              wx.Bitmap(os.path.join(icon_path, "Left-Red-25g.png"), wx.BITMAP_TYPE_PNG),
                                              shortHelp="Increase High BE")

    v_toolbar.AddSeparator()

    low_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE +',
                                             wx.Bitmap(os.path.join(icon_path, "Left-Blue-25g.png"), wx.BITMAP_TYPE_PNG),
                                             shortHelp="Increase Low BE")
    low_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE -',
                                             wx.Bitmap(os.path.join(icon_path, "Right-Blue-25g.png"), wx.BITMAP_TYPE_PNG),
                                             shortHelp="Decrease Low BE")

    v_toolbar.AddSeparator()

    # Intensity adjustment tools
    high_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int +',
                                               wx.Bitmap(os.path.join(icon_path, "Up-Red-25g.png"), wx.BITMAP_TYPE_PNG),
                                               shortHelp="Increase High Intensity")
    high_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int -',
                                               wx.Bitmap(os.path.join(icon_path, "Down-Red-25g.png"), wx.BITMAP_TYPE_PNG),
                                               shortHelp="Decrease High Intensity")

    v_toolbar.AddSeparator()

    low_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low Int +',
                                              wx.Bitmap(os.path.join(icon_path, "Up-Blue-25g.png"), wx.BITMAP_TYPE_PNG),
                                              shortHelp="Increase Low Intensity")
    low_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low Int -',
                                              wx.Bitmap(os.path.join(icon_path, "Down-Blue-25g.png"), wx.BITMAP_TYPE_PNG),
                                              shortHelp="Decrease Low Intensity")
    v_toolbar.AddSeparator()



    # Add text size increase/decrease tools
    text_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Increase Font Size',
                                          wx.Bitmap(os.path.join(icon_path, "A+_25.png"), wx.BITMAP_TYPE_PNG),
                                          shortHelp="Increase All Font Sizes")
    text_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'Decrease Font Size',
                                          wx.Bitmap(os.path.join(icon_path, "A-_25.png"), wx.BITMAP_TYPE_PNG),
                                          shortHelp="Decrease All Font Sizes")

    v_toolbar.AddSeparator()

    # Add text annotation tool after other tools
    text_tool = v_toolbar.AddTool(wx.ID_ANY, 'Add Text',
        wx.Bitmap(os.path.join(icon_path, "AddText-25.png"), wx.BITMAP_TYPE_PNG),
        shortHelp="Add draggable text annotation")

    # Add to the binding section
    frame.Bind(wx.EVT_TOOL, lambda evt: add_draggable_text(frame), text_tool)

    labels_tool = v_toolbar.AddTool(wx.ID_ANY, 'Labels Manager',
                                    wx.Bitmap(os.path.join(icon_path, "ListText2-25.png"), wx.BITMAP_TYPE_PNG),
                                    # wx.Bitmap(os.path.join(icon_path, "AddText-25.png"), wx.BITMAP_TYPE_PNG),
                                    shortHelp="Open Labels Manager")
    frame.Bind(wx.EVT_TOOL, frame.open_labels_window, labels_tool)

    v_toolbar.AddSeparator()

    v_toolbar.Realize()

    # Bind events to the frame
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_be', 'increase'), high_be_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_be', 'decrease'), high_be_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_be', 'increase'), low_be_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_be', 'decrease'), low_be_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_int', 'increase'), high_int_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_int', 'decrease'), high_int_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_int', 'increase'), low_int_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_int', 'decrease'), low_int_decrease_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_text_size_increase, text_increase_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_text_size_decrease, text_decrease_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_zoom_in_tool, zoom_in_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_zoom_out, zoom_out_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_drag_tool, drag_tool)

    return v_toolbar


def create_statusbar(window):
    """
    Create a status bar for the main window.

    Args:
    window: The main application window.
    """
    # Create a status bar with two fields
    window.CreateStatusBar(2)

    # Set the widths of the status bar fields
    window.SetStatusWidths([-1, 200])

    # Set initial text for the status bar fields
    window.SetStatusText("Working Directory: " + window.Working_directory, 0)
    window.SetStatusText("BE: 0 eV, I: 0 CPS", 1)


def update_statusbar(window, message):
    """
    Update the first field of the status bar with a new message.

    Args:
    window: The main application window.
    message: The new message to display in the status bar.
    """
    window.SetStatusText("Working Directory: " + message)


def open_manual2(window):
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    manual_path = os.path.join(root_dir, "Manual.pdf")
    import webbrowser
    webbrowser.open(manual_path)

def open_manual(window):
    import os
    import sys
    import webbrowser

    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, get the path of the executable
        application_path = os.path.dirname(sys.executable)
    else:
        # If the application is run as a script, get the path of the script
        application_path = os.path.dirname(os.path.abspath(__file__))

    manual_path = os.path.join(application_path, "Manual.pdf")
    webbrowser.open(manual_path)

