import wx
import json


class PreferenceWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, style=wx.DEFAULT_FRAME_STYLE & ~(
                wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU) | wx.STAY_ON_TOP)
        self.parent = parent

        self.SetTitle("Preferences")
        self.SetSize((520, 740))
        self.SetMinSize((520, 740))
        self.SetMaxSize((520, 740))

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create notebook
        self.notebook = wx.Notebook(panel)

        # Create tabs
        self.plot_tab = wx.Panel(self.notebook)
        self.text_tab = wx.Panel(self.notebook)
        self.save_tab = wx.Panel(self.notebook)
        self.instrument_tab = wx.Panel(self.notebook)

        # Add tabs to notebook
        self.notebook.AddPage(self.plot_tab, "Plot Settings")
        self.notebook.AddPage(self.text_tab, "Text/Axis Settings")
        self.notebook.AddPage(self.save_tab, "Save Settings")
        self.notebook.AddPage(self.instrument_tab, "Instrument Settings")

        # Add notebook to sizer
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        # Create button grid with 4 columns
        button_grid = wx.GridBagSizer(2, 2)

        # Create save button below notebook
        save_button = wx.Button(panel, label="Save")
        save_button.SetMinSize((110, 40))
        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        button_grid.Add(save_button, pos=(0, 0), flag=wx.ALL, border=5)

        cancel_button = wx.Button(panel, label="Cancel")
        cancel_button.SetMinSize((110, 40))
        cancel_button.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
        button_grid.Add(cancel_button, pos=(0, 1), flag=wx.ALL, border=5)

        main_sizer.Add(button_grid, 0, wx.LEFT, 5)

        panel.SetSizer(main_sizer)

        self.temp_peak_colors = self.parent.peak_colors.copy()

        self.InitUI()
        self.init_instrument_tab()
        self.init_text_tab()
        self.init_save_settings_tab()
        self.LoadSettings()

    def init_text_tab(self):
        text_sizer = wx.GridBagSizer(5, 5)

        fonts = ['DejaVu Sans','Arial', 'Times New Roman', 'Calibri', 'Verdana',
                 'Tahoma', 'Georgia', 'Cambria', 'Century Gothic', 'Garamond',
                 'Book Antiqua', 'Palatino', 'Franklin Gothic', 'Trebuchet MS',
                 'Segoe UI']
        font_label = wx.StaticText(self.text_tab, label="Font:")
        self.font_combo = wx.ComboBox(self.text_tab, choices=fonts, style=wx.CB_READONLY)
        self.font_combo.Bind(wx.EVT_COMBOBOX, self.on_text_change)
        text_sizer.Add(font_label, pos=(0, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        text_sizer.Add(self.font_combo, pos=(0, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # Core level name font size
        core_level_label = wx.StaticText(self.text_tab, label="Title Font Size:")
        self.core_level_spin = wx.SpinCtrl(self.text_tab, min=8, max=24, initial=15)
        self.core_level_spin.Bind(wx.EVT_SPINCTRL, self.on_text_change)
        text_sizer.Add(core_level_label, pos=(1, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        text_sizer.Add(self.core_level_spin, pos=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # Legend font size
        legend_size_label = wx.StaticText(self.text_tab, label="Legend Font Size:")
        self.legend_size_spin = wx.SpinCtrl(self.text_tab, min=6, max=16, initial=8)
        self.legend_size_spin.Bind(wx.EVT_SPINCTRL, self.on_text_change)
        text_sizer.Add(legend_size_label, pos=(2, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        text_sizer.Add(self.legend_size_spin, pos=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # Axis title font size
        axis_title_label = wx.StaticText(self.text_tab, label="Axis Title Font Size:")
        self.axis_title_spin = wx.SpinCtrl(self.text_tab, min=8, max=20, initial=12)
        self.axis_title_spin.Bind(wx.EVT_SPINCTRL, self.on_text_change)
        text_sizer.Add(axis_title_label, pos=(3, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        text_sizer.Add(self.axis_title_spin, pos=(3, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # Axis numbers font size
        axis_num_label = wx.StaticText(self.text_tab, label="Axis Numbers Font Size:")
        self.axis_num_spin = wx.SpinCtrl(self.text_tab, min=8, max=20, initial=10)
        self.axis_num_spin.Bind(wx.EVT_SPINCTRL, self.on_text_change)
        text_sizer.Add(axis_num_label, pos=(4, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        text_sizer.Add(self.axis_num_spin, pos=(4, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # X-axis sublines
        x_sublines_label = wx.StaticText(self.text_tab, label="Number of X-axis Sublines:")
        self.x_sublines_spin = wx.SpinCtrl(self.text_tab, min=0, max=10, initial=5)
        self.x_sublines_spin.Bind(wx.EVT_SPINCTRL, self.on_text_change)
        text_sizer.Add(x_sublines_label, pos=(5, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        text_sizer.Add(self.x_sublines_spin, pos=(5, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # Y-axis sublines
        y_sublines_label = wx.StaticText(self.text_tab, label="Number of Y-axis Sublines:")
        self.y_sublines_spin = wx.SpinCtrl(self.text_tab, min=0, max=10, initial=5)
        self.y_sublines_spin.Bind(wx.EVT_SPINCTRL, self.on_text_change)
        text_sizer.Add(y_sublines_label, pos=(6, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        text_sizer.Add(self.y_sublines_spin, pos=(6, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # X-axis label
        x_label_text = wx.StaticText(self.text_tab, label="X-axis Label:")
        self.x_label_ctrl = wx.TextCtrl(self.text_tab, value="Binding Energy (eV)")
        self.x_label_ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
        text_sizer.Add(x_label_text, pos=(7, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        text_sizer.Add(self.x_label_ctrl, pos=(7, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # Y-axis label
        y_label_text = wx.StaticText(self.text_tab, label="Y-axis Label:")
        self.y_label_ctrl = wx.TextCtrl(self.text_tab, value="Intensity (CPS)")
        self.y_label_ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
        text_sizer.Add(y_label_text, pos=(8, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        text_sizer.Add(self.y_label_ctrl, pos=(8, 1), flag=wx.EXPAND | wx.ALL, border=5)

        self.text_tab.SetSizer(text_sizer)

    def on_text_change(self, event):
        # Update parent window properties
        self.parent.plot_font = self.font_combo.GetValue()
        self.parent.axis_title_size = self.axis_title_spin.GetValue()
        self.parent.axis_number_size = self.axis_num_spin.GetValue()
        self.parent.x_sublines = self.x_sublines_spin.GetValue()
        self.parent.y_sublines = self.y_sublines_spin.GetValue()
        self.parent.legend_font_size = self.legend_size_spin.GetValue()
        self.parent.core_level_text_size = self.core_level_spin.GetValue()

        # Update the plot
        self.parent.update_plot_preferences()
        self.parent.clear_and_replot()

    def init_save_settings_tab(self):
        save_sizer = wx.BoxSizer(wx.VERTICAL)

        # Excel File Settings
        excel_box = wx.StaticBox(self.save_tab, label="Excel File Settings")
        excel_sizer = wx.StaticBoxSizer(excel_box, wx.VERTICAL)
        excel_grid = wx.GridBagSizer(5, 5)

        # Core Level settings
        excel_grid.Add(wx.StaticText(self.save_tab, label="Core Level:"), pos=(0, 0), span=(1, 2))
        excel_grid.Add(wx.StaticText(self.save_tab, label="Width (inches):     "), pos=(1, 0))
        excel_grid.Add(wx.StaticText(self.save_tab, label="Height (inches):"), pos=(2, 0))
        excel_grid.Add(wx.StaticText(self.save_tab, label="DPI:"), pos=(3, 0))

        self.excel_width = wx.SpinCtrlDouble(self.save_tab, value='5.2', min=1, max=20, inc=0.1)
        self.excel_width.SetMinSize((100, -1))
        self.excel_height = wx.SpinCtrlDouble(self.save_tab, value='5.2', min=1, max=20, inc=0.1)
        self.excel_height.SetMinSize((100, -1))
        self.excel_dpi = wx.SpinCtrl(self.save_tab, value='100', min=50, max=1200)
        self.excel_dpi.SetMinSize((100, -1))

        excel_grid.Add(self.excel_width, pos=(1, 1))
        excel_grid.Add(self.excel_height, pos=(2, 1))
        excel_grid.Add(self.excel_dpi, pos=(3, 1))

        # Survey settings
        excel_grid.Add(wx.StaticText(self.save_tab, label="Survey:"), pos=(0, 4), span=(1, 2))
        excel_grid.Add(wx.StaticText(self.save_tab, label="Width (inches):     "), pos=(1, 4))
        excel_grid.Add(wx.StaticText(self.save_tab, label="Height (inches):"), pos=(2, 4))
        excel_grid.Add(wx.StaticText(self.save_tab, label="DPI:"), pos=(3, 4))

        self.survey_excel_width = wx.SpinCtrlDouble(self.save_tab, value='8', min=1, max=20, inc=0.1)
        self.survey_excel_width.SetMinSize((100, -1))
        self.survey_excel_height = wx.SpinCtrlDouble(self.save_tab, value='4', min=1, max=20, inc=0.1)
        self.survey_excel_height.SetMinSize((100, -1))
        self.survey_excel_dpi = wx.SpinCtrl(self.save_tab, value='100', min=50, max=1200)
        self.survey_excel_dpi.SetMinSize((100, -1))

        excel_grid.Add(self.survey_excel_width, pos=(1, 5))
        excel_grid.Add(self.survey_excel_height, pos=(2, 5))
        excel_grid.Add(self.survey_excel_dpi, pos=(3, 5))

        excel_sizer.Add(excel_grid, 5, wx.ALL, 5)

        # Word Report Settings
        word_box = wx.StaticBox(self.save_tab, label="Word Report Settings")
        word_sizer = wx.StaticBoxSizer(word_box, wx.VERTICAL)
        word_grid = wx.GridBagSizer(5, 5)

        # Core Level settings
        word_grid.Add(wx.StaticText(self.save_tab, label="Core Level:"), pos=(0, 0), span=(1, 2))
        word_grid.Add(wx.StaticText(self.save_tab, label="Width (inches):     "), pos=(1, 0))
        word_grid.Add(wx.StaticText(self.save_tab, label="Height (inches):"), pos=(2, 0))
        word_grid.Add(wx.StaticText(self.save_tab, label="DPI:"), pos=(3, 0))

        self.word_width = wx.SpinCtrlDouble(self.save_tab, value='5', min=1, max=20, inc=0.1)
        self.word_width.SetMinSize((100, -1))
        self.word_height = wx.SpinCtrlDouble(self.save_tab, value='5', min=1, max=20, inc=0.1)
        self.word_height.SetMinSize((100, -1))
        self.word_dpi = wx.SpinCtrl(self.save_tab, value='300', min=50, max=1200)
        self.word_dpi.SetMinSize((100, -1))

        word_grid.Add(self.word_width, pos=(1, 1))
        word_grid.Add(self.word_height, pos=(2, 1))
        word_grid.Add(self.word_dpi, pos=(3, 1))

        # Survey settings
        word_grid.Add(wx.StaticText(self.save_tab, label="Survey:"), pos=(0, 4), span=(1, 2))
        word_grid.Add(wx.StaticText(self.save_tab, label="Width (inches):     "), pos=(1, 4))
        word_grid.Add(wx.StaticText(self.save_tab, label="Height (inches):"), pos=(2, 4))
        word_grid.Add(wx.StaticText(self.save_tab, label="DPI:"), pos=(3, 4))

        self.survey_word_width = wx.SpinCtrlDouble(self.save_tab, value='8', min=1, max=20, inc=0.1)
        self.survey_word_width.SetMinSize((100, -1))
        self.survey_word_height = wx.SpinCtrlDouble(self.save_tab, value='4', min=1, max=20, inc=0.1)
        self.survey_word_height.SetMinSize((100, -1))
        self.survey_word_dpi = wx.SpinCtrl(self.save_tab, value='300', min=50, max=1200)
        self.survey_word_dpi.SetMinSize((100, -1))

        word_grid.Add(self.survey_word_width, pos=(1, 5))
        word_grid.Add(self.survey_word_height, pos=(2, 5))
        word_grid.Add(self.survey_word_dpi, pos=(3, 5))

        word_sizer.Add(word_grid, 5, wx.ALL, 5)

        # Export Settings
        other_box = wx.StaticBox(self.save_tab, label="PNG/SVG/PDF Export Settings")
        other_sizer = wx.StaticBoxSizer(other_box, wx.VERTICAL)
        other_grid = wx.GridBagSizer(5, 5)

        other_grid.Add(wx.StaticText(self.save_tab, label="Width (inches):     "), pos=(0, 0))
        other_grid.Add(wx.StaticText(self.save_tab, label="Height (inches):"), pos=(1, 0))
        other_grid.Add(wx.StaticText(self.save_tab, label="DPI:"), pos=(2, 0))

        self.export_width = wx.SpinCtrlDouble(self.save_tab, value='8', min=1, max=20, inc=0.1)
        self.export_width.SetMinSize((100, -1))
        self.export_height = wx.SpinCtrlDouble(self.save_tab, value='6', min=1, max=20, inc=0.1)
        self.export_height.SetMinSize((100, -1))
        self.export_dpi = wx.SpinCtrl(self.save_tab, value='300', min=50, max=1200)
        self.export_dpi.SetMinSize((100, -1))

        other_grid.Add(self.export_width, pos=(0, 1))
        other_grid.Add(self.export_height, pos=(1, 1))
        other_grid.Add(self.export_dpi, pos=(2, 1))


        other_sizer.Add(other_grid, 5, wx.ALL, 5)

        save_sizer.Add(excel_sizer, 0, wx.EXPAND | wx.ALL, 5)
        save_sizer.Add(word_sizer, 0, wx.EXPAND | wx.ALL, 5)
        save_sizer.Add(other_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.save_tab.SetSizer(save_sizer)


    def init_instrument_tab(self):
        sizer = wx.GridBagSizer(5, 5)

        instruments = sorted(list(set(instr for data in self.parent.library_data.values() for instr in data.keys())))
        self.instrument_combo = wx.ComboBox(self.instrument_tab, choices=instruments, style=wx.CB_READONLY)
        self.instrument_combo.Bind(wx.EVT_COMBOBOX, self.on_instrument_change)

        # Add instrument selection
        sizer.Add(wx.StaticText(self.instrument_tab, label="Current Instrument:"), pos=(0, 0),
                  flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.instrument_combo, pos=(0, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # Add ECF method selection
        self.library_type_label = wx.StaticText(self.instrument_tab, label="ECF Method:")
        self.library_type_combo = wx.ComboBox(self.instrument_tab,
                                              choices=["Scofield", "Wagner", "TPP-2M","EAL", "None"],
                                              style=wx.CB_READONLY)
        current_type = self.parent.library_type
        selection_index = self.library_type_combo.FindString(current_type)
        if selection_index != wx.NOT_FOUND:
            self.library_type_combo.SetSelection(selection_index)
        else:
            self.library_type_combo.SetSelection(2)  # TPP-2M as fallback
        sizer.Add(self.library_type_label, pos=(1, 0), flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.library_type_combo, pos=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # Add Transmission
        self.use_transmission = wx.CheckBox(self.instrument_tab, label="Use Transmission")
        sizer.Add(self.use_transmission, pos=(2, 0), flag=wx.EXPAND | wx.ALL, border=5)

        # Add angular correction controls
        self.use_angular_correction = wx.CheckBox(self.instrument_tab, label="Use Angular Correction")
        sizer.Add(self.use_angular_correction, pos=(3, 0), flag=wx.EXPAND | wx.ALL, border=5)

        angle_label = wx.StaticText(self.instrument_tab, label="Analysis Angle (°):")
        self.angle_spin = wx.SpinCtrlDouble(self.instrument_tab, value='54.7', min=0, max=90, inc=0.1)
        sizer.Add(angle_label, pos=(4, 0), flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.angle_spin, pos=(4, 1), flag=wx.EXPAND | wx.ALL, border=5)

        self.instrument_tab.SetSizer(sizer)

    def on_instrument_change(self, event):
        selected_instrument = self.instrument_combo.GetValue()
        self.parent.update_instrument(selected_instrument)

    def InitUI(self):
        # panel = wx.Panel(self)
        sizer = wx.GridBagSizer(2, 2)
        # self.plot_tab.SetSizer(sizer)

        # Plot style
        plot_style_label = wx.StaticText(self.plot_tab, label="Plot Style:")
        self.plot_style = wx.Choice(self.plot_tab, choices=["Scatter", "Line"])
        self.plot_style.SetMinSize((100,30))
        self.plot_style.Bind(wx.EVT_CHOICE, self.OnPlotStyleChange)
        sizer.Add(plot_style_label, pos=(0, 0), flag=wx.ALL, border=5)
        sizer.Add(self.plot_style, pos=(0, 1), flag=wx.ALL, border=5)



        # Point size (for scatter)
        self.point_size_label = wx.StaticText(self.plot_tab, label="Scatter Size:")
        self.point_size_spin = wx.SpinCtrl(self.plot_tab, value="20", min=1, max=50)
        self.point_size_spin.SetMinSize((100,-1))
        sizer.Add(self.point_size_label, pos=(1, 0), flag=wx.ALL, border=5)
        sizer.Add(self.point_size_spin, pos=(1, 1), flag=wx.ALL, border=5)

        # Scatter marker
        marker_label = wx.StaticText(self.plot_tab, label="Scatter Marker:")
        self.marker_choice = wx.Choice(self.plot_tab, choices=["o", "s", "^", "D", "*"])
        self.marker_choice.SetMinSize((100, -1))
        sizer.Add(marker_label, pos=(2, 0), flag=wx.ALL, border=5)
        sizer.Add(self.marker_choice, pos=(2, 1), flag=wx.ALL, border=5)

        # Scatter color
        scatter_color_label = wx.StaticText(self.plot_tab, label="Scatter Color:")
        self.scatter_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.scatter_color_picker.SetMinSize((100, -1))
        sizer.Add(scatter_color_label, pos=(3, 0), flag=wx.ALL, border=5)
        sizer.Add(self.scatter_color_picker, pos=(3, 1), flag=wx.ALL, border=5)

        # Raw data linestyle
        self.raw_data_linestyle_label = wx.StaticText(self.plot_tab, label="Raw Data Line:")
        self.raw_data_linestyle = wx.Choice(self.plot_tab, choices=["-", "--", "-.", ":"])
        self.raw_data_linestyle.SetMinSize((100, -1))
        sizer.Add(self.raw_data_linestyle_label, pos=(5, 0), flag=wx.ALL, border=5)
        sizer.Add(self.raw_data_linestyle, pos=(5, 1), flag=wx.ALL, border=5)

        # Line width (for line)
        self.line_width_label = wx.StaticText(self.plot_tab, label="Line Width:")
        self.line_width_spin = wx.SpinCtrl(self.plot_tab, value="1", min=1, max=10)
        self.line_width_spin.SetMinSize((100, -1))
        sizer.Add(self.line_width_label, pos=(6, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_width_spin, pos=(6, 1), flag=wx.ALL, border=5)

        # Line alpha (for line)
        self.line_alpha_label = wx.StaticText(self.plot_tab, label="Line Alpha:")
        self.line_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.7", min=0, max=1, inc=0.1)
        self.line_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.line_alpha_label, pos=(7, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_alpha_spin, pos=(7, 1), flag=wx.ALL, border=5)

        # Line color
        line_color_label = wx.StaticText(self.plot_tab, label="Line Color:")
        self.line_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.line_color_picker.SetMinSize((100, -1))
        sizer.Add(line_color_label, pos=(8, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_color_picker, pos=(8, 1), flag=wx.ALL, border=5)

        # Residual options
        self.residual_linestyle_label = wx.StaticText(self.plot_tab, label="Residual Line:")
        self.residual_linestyle = wx.Choice(self.plot_tab, choices=["-", "--", "-.", ":"])
        self.residual_linestyle.SetMinSize((100, -1))
        sizer.Add(self.residual_linestyle_label, pos=(10, 0), flag=wx.ALL, border=5)
        sizer.Add(self.residual_linestyle, pos=(10, 1), flag=wx.ALL, border=5)

        self.residual_alpha_label = wx.StaticText(self.plot_tab, label="Residual Alpha:")
        self.residual_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.4", min=0, max=1, inc=0.1)
        self.residual_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.residual_alpha_label, pos=(11, 0), flag=wx.ALL, border=5)
        sizer.Add(self.residual_alpha_spin, pos=(11, 1), flag=wx.ALL, border=5)

        residual_label = wx.StaticText(self.plot_tab, label="Residual:")
        self.residual_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.residual_color_picker.SetMinSize((100, -1))
        sizer.Add(residual_label, pos=(12, 0), flag=wx.ALL, border=5)
        sizer.Add(self.residual_color_picker, pos=(12, 1), flag=wx.ALL, border=5)

        # Background options
        self.background_linestyle_label = wx.StaticText(self.plot_tab, label="Background Line:")
        self.background_linestyle = wx.Choice(self.plot_tab, choices=["-", "--", "-.", ":"])
        self.background_linestyle.SetMinSize((100, -1))
        sizer.Add(self.background_linestyle_label, pos=(14, 0), flag=wx.ALL, border=5)
        sizer.Add(self.background_linestyle, pos=(14, 1), flag=wx.ALL, border=5)

        self.background_alpha_label = wx.StaticText(self.plot_tab, label="Background Alpha:")
        self.background_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.5", min=0, max=1, inc=0.1)
        self.background_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.background_alpha_label, pos=(15, 0), flag=wx.ALL, border=5)
        sizer.Add(self.background_alpha_spin, pos=(15, 1), flag=wx.ALL, border=5)

        background_label = wx.StaticText(self.plot_tab, label="Background:")
        self.background_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.background_color_picker.SetMinSize((100, -1))
        sizer.Add(background_label, pos=(16, 0), flag=wx.ALL, border=5)
        sizer.Add(self.background_color_picker, pos=(16, 1), flag=wx.ALL, border=5)

        # Envelope options
        self.envelope_linestyle_label = wx.StaticText(self.plot_tab, label="Envelope Line:")
        self.envelope_linestyle = wx.Choice(self.plot_tab, choices=["-", "--", "-.", ":"])
        self.envelope_linestyle.SetMinSize((100, -1))
        sizer.Add(self.envelope_linestyle_label, pos=(0, 4), flag=wx.ALL, border=5)
        sizer.Add(self.envelope_linestyle, pos=(0, 5), flag=wx.ALL, border=5)

        self.envelope_alpha_label = wx.StaticText(self.plot_tab, label="Envelope Alpha:")
        self.envelope_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.6", min=0, max=1, inc=0.1)
        self.envelope_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.envelope_alpha_label, pos=(1, 4), flag=wx.ALL, border=5)
        sizer.Add(self.envelope_alpha_spin, pos=(1, 5), flag=wx.ALL, border=5)

        envelope_label = wx.StaticText(self.plot_tab, label="Envelope:")
        self.envelope_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.envelope_color_picker.SetMinSize((100, -1))
        sizer.Add(envelope_label, pos=(2, 4), flag=wx.ALL, border=5)
        sizer.Add(self.envelope_color_picker, pos=(2, 5), flag=wx.ALL, border=5)

        # Peak number selection
        self.peak_number_spin_label = wx.StaticText(self.plot_tab, label="Peak Number:")
        self.peak_number_spin = wx.SpinCtrl(self.plot_tab, min=1, max=15, initial=1)
        self.peak_number_spin.SetMinSize((100, -1))
        sizer.Add(self.peak_number_spin_label, pos=(4, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_number_spin, pos=(4, 5), flag=wx.ALL, border=5)

        # Peak fill type
        peak_fill_type_label = wx.StaticText(self.plot_tab, label="Peak Fill Type:")
        self.peak_fill_type_combo = wx.ComboBox(self.plot_tab, choices=["Solid Fill", "Hatch"], style=wx.CB_READONLY)
        self.peak_fill_type_combo.SetMinSize((100, -1))
        sizer.Add(peak_fill_type_label, pos=(5, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_fill_type_combo, pos=(5, 5), flag=wx.ALL, border=5)

        # Peak hatch pattern
        peak_hatch_label = wx.StaticText(self.plot_tab, label="Hatch Pattern:")
        self.peak_hatch_combo = wx.ComboBox(self.plot_tab,
                                            choices=[
                                                '/', '\\', '|', '-',  # Simple lines
                                                '+', 'x',  # Crosses
                                                'o', 'O',  # Small/large circles
                                                '.', '*',  # Dots/stars
                                                '//', '\\\\', '||', '--',  # Double density
                                                '///', '\\\\\\', '|||', '---',  # Triple density
                                                '/o', '\\o', '|o', '-o',  # Lines with circles
                                                '/O', '\\O', '|O', '-O',  # Lines with large circles
                                                '//', '\\\\', '||', '--',  # Denser lines
                                                'x/', 'x\\', 'x|', 'x-',  # Crosses with lines
                                                '+/', '+\\', '+|', '+-',  # Plus with lines
                                                '*/', '*\\', '*|', '*-'  # Stars with lines
                                                ],
                                            style=wx.CB_READONLY)
        self.peak_hatch_combo.SetMinSize((100, -1))
        sizer.Add(peak_hatch_label, pos=(6, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_hatch_combo, pos=(6, 5), flag=wx.ALL, border=5)

        hatch_density_label = wx.StaticText(self.plot_tab, label="Hatch Density:")
        self.hatch_density_spin = wx.SpinCtrl(self.plot_tab, value="2", min=1, max=10)
        self.hatch_density_spin.SetMinSize((100, -1))
        sizer.Add(hatch_density_label, pos=(7, 4), flag=wx.ALL, border=5)
        sizer.Add(self.hatch_density_spin, pos=(7, 5), flag=wx.ALL, border=5)

        self.peak_fill_type_combo.Bind(wx.EVT_COMBOBOX, self.OnFillTypeChange)
        self.peak_hatch_combo.Bind(wx.EVT_COMBOBOX, self.OnHatchChange)


        # Peak color selection
        peak_color_label = wx.StaticText(self.plot_tab, label="Peak Color:")
        self.peak_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.peak_color_picker.SetMinSize((100, -1))
        sizer.Add(peak_color_label, pos=(8, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_color_picker, pos=(8, 5), flag=wx.ALL, border=5)

        # Peak alpha
        self.peak_alpha_label = wx.StaticText(self.plot_tab, label="Peak Alpha:")
        self.peak_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.3", min=0, max=1, inc=0.1)
        self.peak_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.peak_alpha_label, pos=(9, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_alpha_spin, pos=(9, 5), flag=wx.ALL, border=5)

        # Peak line style
        peak_line_style_label = wx.StaticText(self.plot_tab, label="Peak Line Style:")
        self.peak_line_style_combo = wx.ComboBox(self.plot_tab,
                                                 choices=["No Line", "Black", "Same Color", "Grey", "Yellow"],
                                                 style=wx.CB_READONLY)
        self.peak_line_style_combo.SetMinSize((100, -1))
        sizer.Add(peak_line_style_label, pos=(10, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_line_style_combo, pos=(10, 5), flag=wx.ALL, border=5)

        # Peak line thickness
        self.peak_line_thickness_label = wx.StaticText(self.plot_tab, label="Peak Line Thickness:")
        self.peak_line_thickness_spin = wx.SpinCtrl(self.plot_tab, value="1", min=1, max=5)
        self.peak_line_thickness_spin.SetMinSize((100, -1))
        sizer.Add(self.peak_line_thickness_label, pos=(11, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_line_thickness_spin, pos=(11, 5), flag=wx.ALL, border=5)

        # Peak line alpha
        self.peak_line_alpha_label = wx.StaticText(self.plot_tab, label="Peak Line Alpha:")
        self.peak_line_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.7", min=0, max=1, inc=0.1)
        self.peak_line_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.peak_line_alpha_label, pos=(12, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_line_alpha_spin, pos=(12, 5), flag=wx.ALL, border=5)


        # # Save button (moved to the bottom)
        # save_button = wx.Button(self.plot_tab, label="Save")
        # save_button.SetMinSize((190, 40))
        # save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        # sizer.Add(save_button, pos=(15, 0), span=(2, 2), flag=wx.ALL | wx.ALIGN_CENTER, border=5)

        # Bind the spin control to update the color picker
        self.peak_number_spin.Bind(wx.EVT_SPINCTRL, self.OnPeakNumberChange)
        self.peak_color_picker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnColorChange)
        self.point_size_spin.Bind(wx.EVT_SPINCTRL, self.OnPointSizeChange)
        self.marker_choice.Bind(wx.EVT_CHOICE, self.OnMarkerChange)
        self.scatter_color_picker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnScatterColorChange)
        self.raw_data_linestyle.Bind(wx.EVT_CHOICE, self.OnRawDataLineStyleChange)
        self.line_width_spin.Bind(wx.EVT_SPINCTRL, self.OnLineWidthChange)
        self.line_alpha_spin.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnLineAlphaChange)
        self.line_color_picker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnLineColorChange)
        self.residual_linestyle.Bind(wx.EVT_CHOICE, self.OnResidualLineStyleChange)
        self.residual_alpha_spin.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnResidualAlphaChange)
        self.residual_color_picker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnResidualColorChange)
        self.background_linestyle.Bind(wx.EVT_CHOICE, self.OnBackgroundLineStyleChange)
        self.background_alpha_spin.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnBackgroundAlphaChange)
        self.background_color_picker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnBackgroundColorChange)
        self.envelope_linestyle.Bind(wx.EVT_CHOICE, self.OnEnvelopeLineStyleChange)
        self.envelope_alpha_spin.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnEnvelopeAlphaChange)
        self.envelope_color_picker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnEnvelopeColorChange)
        self.peak_alpha_spin.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnPeakAlphaChange)
        self.peak_line_style_combo.Bind(wx.EVT_COMBOBOX, self.OnPeakLineStyleChange)
        self.peak_line_thickness_spin.Bind(wx.EVT_SPINCTRL, self.OnPeakLineThicknessChange)
        self.peak_line_alpha_spin.Bind(wx.EVT_SPINCTRLDOUBLE, self.OnPeakLineAlphaChange)
        self.hatch_density_spin.Bind(wx.EVT_SPINCTRL, self.OnHatchDensityChange)

        self.plot_tab.SetSizer(sizer)
        self.Centre()

        # Load current settings
        # self.LoadSettings()

    def OnHatchDensityChange(self, event):
        self.parent.hatch_density = self.hatch_density_spin.GetValue()
        self.update_plot()

    def OnPointSizeChange(self, event):
        self.parent.scatter_size = self.point_size_spin.GetValue()
        self.update_plot()

    def OnMarkerChange(self, event):
        self.parent.scatter_marker = self.marker_choice.GetString(self.marker_choice.GetSelection())
        self.update_plot()

    def OnPlotStyleChange(self, event):
        self.parent.plot_style = "scatter" if self.plot_style.GetSelection() == 0 else "line"
        self.update_plot()

    def OnPointSizeChange(self, event):
        self.parent.scatter_size = self.point_size_spin.GetValue()
        self.update_plot()

    def OnMarkerChange(self, event):
        self.parent.scatter_marker = self.marker_choice.GetString(self.marker_choice.GetSelection())
        self.update_plot()

    def OnScatterColorChange(self, event):
        self.parent.scatter_color = event.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.update_plot()

    def OnRawDataLineStyleChange(self, event):
        self.parent.raw_data_linestyle = self.raw_data_linestyle.GetString(self.raw_data_linestyle.GetSelection())
        self.update_plot()

    def OnLineWidthChange(self, event):
        self.parent.line_width = self.line_width_spin.GetValue()
        self.update_plot()

    def OnLineAlphaChange(self, event):
        self.parent.line_alpha = self.line_alpha_spin.GetValue()
        self.update_plot()

    def OnLineColorChange(self, event):
        self.parent.line_color = event.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.update_plot()

    def OnResidualLineStyleChange(self, event):
        self.parent.residual_linestyle = self.residual_linestyle.GetString(self.residual_linestyle.GetSelection())
        self.update_plot()

    def OnResidualAlphaChange(self, event):
        self.parent.residual_alpha = self.residual_alpha_spin.GetValue()
        self.update_plot()

    def OnResidualColorChange(self, event):
        self.parent.residual_color = event.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.update_plot()

    def OnBackgroundLineStyleChange(self, event):
        self.parent.background_linestyle = self.background_linestyle.GetString(self.background_linestyle.GetSelection())
        self.update_plot()

    def OnBackgroundAlphaChange(self, event):
        self.parent.background_alpha = self.background_alpha_spin.GetValue()
        self.update_plot()

    def OnBackgroundColorChange(self, event):
        self.parent.background_color = event.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.update_plot()

    def OnEnvelopeLineStyleChange(self, event):
        self.parent.envelope_linestyle = self.envelope_linestyle.GetString(self.envelope_linestyle.GetSelection())
        self.update_plot()

    def OnEnvelopeAlphaChange(self, event):
        self.parent.envelope_alpha = self.envelope_alpha_spin.GetValue()
        self.update_plot()

    def OnEnvelopeColorChange(self, event):
        self.parent.envelope_color = event.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.update_plot()

    def OnPeakAlphaChange(self, event):
        self.parent.peak_alpha = self.peak_alpha_spin.GetValue()
        self.update_plot()

    def OnPeakLineStyleChange(self, event):
        self.parent.peak_line_style = self.peak_line_style_combo.GetValue()
        self.update_plot()

    def OnPeakLineThicknessChange(self, event):
        self.parent.peak_line_thickness = self.peak_line_thickness_spin.GetValue()
        self.update_plot()

    def OnPeakLineAlphaChange(self, event):
        self.parent.peak_line_alpha = self.peak_line_alpha_spin.GetValue()
        self.update_plot()

    def LoadSettings(self):
        self.plot_style.SetSelection(0 if self.parent.plot_style == "scatter" else 1)
        self.point_size_spin.SetValue(self.parent.scatter_size)
        self.marker_choice.SetSelection(["o", "s", "^", "D", "*"].index(self.parent.scatter_marker))
        self.scatter_color_picker.SetColour(self.parent.scatter_color)
        self.line_width_spin.SetValue(self.parent.line_width)
        self.line_alpha_spin.SetValue(self.parent.line_alpha)
        self.line_color_picker.SetColour(self.parent.line_color)

        self.background_color_picker.SetColour(self.parent.background_color)
        self.background_alpha_spin.SetValue(self.parent.background_alpha)
        self.background_linestyle.SetSelection(["", "-", "--", "-.", ":"].index(self.parent.background_linestyle))
        self.envelope_color_picker.SetColour(self.parent.envelope_color)
        self.envelope_alpha_spin.SetValue(self.parent.envelope_alpha)
        self.envelope_linestyle.SetSelection(["", "-", "--", "-.", ":"].index(self.parent.envelope_linestyle))
        self.residual_color_picker.SetColour(self.parent.residual_color)
        self.residual_alpha_spin.SetValue(self.parent.residual_alpha)
        self.residual_linestyle.SetSelection(["", "-", "--", "-.", ":"].index(self.parent.residual_linestyle))
        self.raw_data_linestyle.SetSelection(["", "-", "--", "-.", ":"].index(self.parent.raw_data_linestyle))

        self.peak_line_style_combo.SetValue(self.parent.peak_line_style)
        self.peak_line_alpha_spin.SetValue(self.parent.peak_line_alpha)
        self.peak_line_thickness_spin.SetValue(self.parent.peak_line_thickness)
        # self.peak_line_pattern_combo.SetValue(self.parent.peak_line_pattern)
        self.hatch_density_spin.SetValue(self.parent.hatch_density)

        # Add loading of text settings
        self.font_combo.SetValue(self.parent.plot_font)
        self.axis_title_spin.SetValue(self.parent.axis_title_size)
        self.axis_num_spin.SetValue(self.parent.axis_number_size)
        self.x_sublines_spin.SetValue(self.parent.x_sublines)
        self.y_sublines_spin.SetValue(self.parent.y_sublines)
        self.legend_size_spin.SetValue(self.parent.legend_font_size)
        self.core_level_spin.SetValue(self.parent.core_level_text_size)
        if hasattr(self.parent, 'x_axis_label'):
            self.x_label_ctrl.SetValue(self.parent.x_axis_label)
        if hasattr(self.parent, 'y_axis_label'):
            self.y_label_ctrl.SetValue(self.parent.y_axis_label)

        # Load the first peak color
        self.temp_peak_colors = self.parent.peak_colors.copy()
        if self.parent.peak_colors:
            self.peak_color_picker.SetColour(self.parent.peak_colors[0])

        self.peak_alpha_spin.SetValue(self.parent.peak_alpha)

        current_peak = self.peak_number_spin.GetValue() - 1
        self.peak_fill_type_combo.SetValue(self.parent.peak_fill_types[current_peak])
        self.peak_hatch_combo.SetValue(self.parent.peak_hatch_patterns[current_peak])

        # Add save settings
        self.excel_width.SetValue(self.parent.excel_width)
        self.excel_height.SetValue(self.parent.excel_height)
        self.excel_dpi.SetValue(self.parent.excel_dpi)
        self.survey_excel_width.SetValue(self.parent.survey_excel_width)
        self.survey_excel_height.SetValue(self.parent.survey_excel_height)
        self.survey_excel_dpi.SetValue(self.parent.survey_excel_dpi)
        self.word_width.SetValue(self.parent.word_width)
        self.word_height.SetValue(self.parent.word_height)
        self.word_dpi.SetValue(self.parent.word_dpi)
        self.export_width.SetValue(self.parent.export_width)
        self.export_height.SetValue(self.parent.export_height)
        self.export_dpi.SetValue(self.parent.export_dpi)

        if hasattr(self.parent, 'current_instrument'):
            self.instrument_combo.SetValue(self.parent.current_instrument)
        if hasattr(self.parent, 'library_type'):
            self.library_type_combo.SetValue(self.parent.library_type +
                                             (" (KE^0.6)" if self.parent.library_type == "Scofield" else
                                              " (KE^1.0)" if self.parent.library_type == "Wagner" else "None"))

        if hasattr(self.parent, 'use_angular_correction'):
            self.use_angular_correction.SetValue(self.parent.use_angular_correction)
        if hasattr(self.parent, 'analysis_angle'):
            self.angle_spin.SetValue(self.parent.analysis_angle)

    def OnPeakNumberChange(self, event):
        current_peak = event.GetPosition() - 1
        if current_peak < len(self.temp_peak_colors):
            color = wx.Colour(self.temp_peak_colors[current_peak])
        else:
            color = wx.Colour(128, 128, 128)
            self.temp_peak_colors.append(color.GetAsString(wx.C2S_HTML_SYNTAX))

        self.peak_color_picker.SetColour(color)

        # Update fill type and hatch pattern for current peak
        self.peak_fill_type_combo.SetValue(self.parent.peak_fill_types[current_peak])
        self.peak_hatch_combo.SetValue(self.parent.peak_hatch_patterns[current_peak])
        self.update_plot()

    def OnFillTypeChange(self, event):
        current_peak = self.peak_number_spin.GetValue() - 1
        new_value = self.peak_fill_type_combo.GetValue()
        self.parent.peak_fill_types[current_peak] = new_value
        self.update_plot()

    def OnHatchChange(self, event):
        current_peak = self.peak_number_spin.GetValue() - 1
        new_value = self.peak_hatch_combo.GetValue()
        self.parent.peak_hatch_patterns[current_peak] = new_value
        self.update_plot()

    def OnColorChange(self, event):
        current_peak = self.peak_number_spin.GetValue() - 1
        new_color = event.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        if current_peak < len(self.temp_peak_colors):
            self.temp_peak_colors[current_peak] = new_color

            # Update hatch pattern based on peak number
            hatch_patterns = ["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]
            self.peak_hatch_combo.SetValue(hatch_patterns[current_peak % len(hatch_patterns)])
        else:
            self.temp_peak_colors.append(new_color)

        self.parent.peak_colors = self.temp_peak_colors.copy()
        self.update_plot()

    def OnPlotStyleChange(self, event):
        self.parent.plot_style = "scatter" if self.plot_style.GetSelection() == 0 else "line"
        self.update_plot()

    def update_plot(self):
        self.parent.update_plot_preferences()
        self.parent.clear_and_replot()

    def OnSave(self, event):
        self.parent.plot_style = "scatter" if self.plot_style.GetSelection() == 0 else "line"
        self.parent.scatter_size = self.point_size_spin.GetValue()
        self.parent.scatter_marker = self.marker_choice.GetString(self.marker_choice.GetSelection())
        self.parent.scatter_color = self.scatter_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.line_width = self.line_width_spin.GetValue()
        self.parent.line_alpha = self.line_alpha_spin.GetValue()
        self.parent.line_color = self.line_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)

        self.parent.background_color = self.background_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.background_alpha = self.background_alpha_spin.GetValue()
        self.parent.background_linestyle = ["", "-", "--", "-.", ":"][self.background_linestyle.GetSelection()]

        self.parent.envelope_color = self.envelope_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.envelope_alpha = self.envelope_alpha_spin.GetValue()
        self.parent.envelope_linestyle = ["", "-", "--", "-.", ":"][self.envelope_linestyle.GetSelection()]

        self.parent.residual_color = self.residual_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.residual_alpha = self.residual_alpha_spin.GetValue()
        self.parent.residual_linestyle = ["", "-", "--", "-.", ":"][self.residual_linestyle.GetSelection()]

        self.parent.raw_data_linestyle = ["", "-", "--", "-.", ":"][self.raw_data_linestyle.GetSelection()]

        self.parent.peak_line_style = self.peak_line_style_combo.GetValue()
        self.parent.peak_line_alpha = self.peak_line_alpha_spin.GetValue()
        self.parent.peak_line_thickness = self.peak_line_thickness_spin.GetValue()
        # self.parent.peak_line_pattern = self.peak_line_pattern_combo.GetValue()

        # Save the current color of the selected peak
        current_peak = self.peak_number_spin.GetValue() - 1
        self.temp_peak_colors[current_peak] = self.peak_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)

        # Update parent's peak_colors with temp_peak_colors
        self.parent.peak_colors = self.temp_peak_colors.copy()

        self.parent.peak_alpha = self.peak_alpha_spin.GetValue()

        self.parent.current_instrument = self.instrument_combo.GetValue()

        current_peak = self.peak_number_spin.GetValue() - 1
        self.parent.peak_fill_types[current_peak] = self.peak_fill_type_combo.GetValue()
        self.parent.peak_hatch_patterns[current_peak] = self.peak_hatch_combo.GetValue()
        self.parent.hatch_density = self.hatch_density_spin.GetValue()

        self.parent.use_transmission = self.use_transmission.GetValue()

        # Save text settings
        self.parent.plot_font = self.font_combo.GetValue()
        self.parent.axis_title_size = self.axis_title_spin.GetValue()
        self.parent.axis_number_size = self.axis_num_spin.GetValue()
        self.parent.x_sublines = self.x_sublines_spin.GetValue()
        self.parent.y_sublines = self.y_sublines_spin.GetValue()
        self.parent.legend_font_size = self.legend_size_spin.GetValue()
        self.parent.x_axis_label = self.x_label_ctrl.GetValue()
        self.parent.y_axis_label = self.y_label_ctrl.GetValue()

        # Update plot axis labels
        self.parent.ax.set_xlabel(self.parent.x_axis_label)
        self.parent.ax.set_ylabel(self.parent.y_axis_label)
        self.parent.canvas.draw_idle()

        # Update the files plot settingg
        self.parent.excel_width = self.excel_width.GetValue()
        self.parent.excel_height = self.excel_height.GetValue()
        self.parent.excel_dpi = self.excel_dpi.GetValue()
        self.parent.survey_excel_width = self.survey_excel_width.GetValue()
        self.parent.survey_excel_height = self.survey_excel_height.GetValue()
        self.parent.survey_excel_dpi = self.survey_excel_dpi.GetValue()

        self.parent.word_width = self.word_width.GetValue()
        self.parent.word_height = self.word_height.GetValue()
        self.parent.word_dpi = self.word_dpi.GetValue()
        self.parent.survey_word_width = self.survey_word_width.GetValue()
        self.parent.survey_word_height = self.survey_word_height.GetValue()
        self.parent.survey_word_dpi = self.survey_word_dpi.GetValue()

        self.parent.export_width = self.export_width.GetValue()
        self.parent.export_height = self.export_height.GetValue()
        self.parent.export_dpi = self.export_dpi.GetValue()


        self.parent.current_instrument = self.instrument_combo.GetValue()

        value = self.library_type_combo.GetValue()
        self.parent.library_type = value.split()[0] if value else "ALTHERMO01"
        self.parent.use_transmission = self.use_transmission.GetValue()

        self.parent.use_angular_correction = self.use_angular_correction.GetValue()
        self.parent.analysis_angle = self.angle_spin.GetValue()

        # Save the configuration
        self.parent.save_config()

        # Update the plot preferences
        self.parent.update_plot_preferences()

        # Close the preference window
        self.Close()

