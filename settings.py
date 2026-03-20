import wx
from theme_manager import ThemeManager

class SettingsDialog(wx.Dialog):
    """Comprehensive settings dialog with tabbed interface"""
    
    def __init__(self, parent, current_theme):
        super().__init__(parent, title="Notepad PRO Settings", size=(600, 500))
        self.parent_frame = parent
        self.current_theme = current_theme
        self.CenterOnParent()
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Create notebook for tabs
        notebook = wx.Notebook(panel)
        
        # Appearance tab
        appearance_panel = self.CreateAppearancePanel(notebook)
        notebook.AddPage(appearance_panel, "Appearance")
        
        # Editor tab
        editor_panel = self.CreateEditorPanel(notebook)
        notebook.AddPage(editor_panel, "Editor")
        
        # AI tab
        ai_panel = self.CreateAIPanel(notebook)
        notebook.AddPage(ai_panel, "AI Settings")
        
        # Behavior tab
        behavior_panel = self.CreateBehaviorPanel(notebook)
        notebook.AddPage(behavior_panel, "Behavior")
        
        vbox.Add(notebook, 1, wx.EXPAND | wx.ALL, 10)
        
        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        
        apply_btn = wx.Button(panel, label="Apply")
        ok_btn = wx.Button(panel, label="OK")
        cancel_btn = wx.Button(panel, label="Cancel")
        
        apply_btn.Bind(wx.EVT_BUTTON, self.OnApply)
        ok_btn.Bind(wx.EVT_BUTTON, self.OnOK)
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        btn_sizer.Add(apply_btn, 0, wx.ALL, 5)
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        
        vbox.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(vbox)
    
    def CreateAppearancePanel(self, parent):
        """Create appearance settings panel"""
        panel = wx.Panel(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Theme selection
        theme_box = wx.StaticBox(panel, label="Theme")
        theme_sizer = wx.StaticBoxSizer(theme_box, wx.VERTICAL)
        
        # Get available themes
        theme_mgr = ThemeManager()
        themes = theme_mgr.get_all_themes()
        
        self.theme_choice = wx.Choice(panel, choices=[name for _, name in themes])
        
        # Set current theme
        for i, (key, name) in enumerate(themes):
            if key == self.current_theme:
                self.theme_choice.SetSelection(i)
                break
        
        self.theme_choice.Bind(wx.EVT_CHOICE, self.OnThemeChange)
        
        theme_sizer.Add(wx.StaticText(panel, label="Select theme:"), 0, wx.ALL, 5)
        theme_sizer.Add(self.theme_choice, 0, wx.EXPAND | wx.ALL, 5)
        
        vbox.Add(theme_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Font settings
        font_box = wx.StaticBox(panel, label="Font")
        font_sizer = wx.StaticBoxSizer(font_box, wx.VERTICAL)
        
        # Font size
        size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        size_sizer.Add(wx.StaticText(panel, label="Font size:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.font_size = wx.SpinCtrl(panel, value="11", min=8, max=72)
        size_sizer.Add(self.font_size, 0, wx.ALL, 5)
        
        font_sizer.Add(size_sizer, 0, wx.EXPAND)
        
        # Font family
        family_sizer = wx.BoxSizer(wx.HORIZONTAL)
        family_sizer.Add(wx.StaticText(panel, label="Font family:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.font_family = wx.Choice(panel, choices=["Segoe UI", "Consolas", "Courier New", "Arial", "Times New Roman"])
        self.font_family.SetSelection(0)
        family_sizer.Add(self.font_family, 1, wx.EXPAND | wx.ALL, 5)
        
        font_sizer.Add(family_sizer, 0, wx.EXPAND)
        
        vbox.Add(font_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(vbox)
        return panel
    
    def CreateEditorPanel(self, parent):
        """Create editor settings panel"""
        panel = wx.Panel(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Tab settings
        tab_box = wx.StaticBox(panel, label="Indentation")
        tab_sizer = wx.StaticBoxSizer(tab_box, wx.VERTICAL)
        
        tab_size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tab_size_sizer.Add(wx.StaticText(panel, label="Tab size:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.tab_size = wx.SpinCtrl(panel, value="4", min=1, max=16)
        tab_size_sizer.Add(self.tab_size, 0, wx.ALL, 5)
        
        tab_sizer.Add(tab_size_sizer, 0, wx.EXPAND)
        
        self.use_spaces = wx.CheckBox(panel, label="Insert spaces instead of tabs")
        self.use_spaces.SetValue(True)
        tab_sizer.Add(self.use_spaces, 0, wx.ALL, 5)
        
        vbox.Add(tab_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Display options
        display_box = wx.StaticBox(panel, label="Display")
        display_sizer = wx.StaticBoxSizer(display_box, wx.VERTICAL)
        
        self.show_line_numbers = wx.CheckBox(panel, label="Show line numbers")
        self.show_line_numbers.SetValue(True)
        display_sizer.Add(self.show_line_numbers, 0, wx.ALL, 5)
        
        self.highlight_current_line = wx.CheckBox(panel, label="Highlight current line")
        self.highlight_current_line.SetValue(True)
        display_sizer.Add(self.highlight_current_line, 0, wx.ALL, 5)
        
        self.show_whitespace = wx.CheckBox(panel, label="Show whitespace characters")
        display_sizer.Add(self.show_whitespace, 0, wx.ALL, 5)
        
        vbox.Add(display_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(vbox)
        return panel
    
    def CreateAIPanel(self, parent):
        """Create AI settings panel"""
        panel = wx.Panel(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Model selection
        model_box = wx.StaticBox(panel, label="AI Model")
        model_sizer = wx.StaticBoxSizer(model_box, wx.VERTICAL)
        
        model_sizer.Add(wx.StaticText(panel, label="Select AI model:"), 0, wx.ALL, 5)
        self.ai_model = wx.Choice(panel, choices=["gemma3:1b", "llama2:7b", "mistral:7b", "codellama:7b"])
        self.ai_model.SetSelection(0)
        model_sizer.Add(self.ai_model, 0, wx.EXPAND | wx.ALL, 5)
        
        vbox.Add(model_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # AI features
        features_box = wx.StaticBox(panel, label="Features")
        features_sizer = wx.StaticBoxSizer(features_box, wx.VERTICAL)
        
        self.enable_autocomplete = wx.CheckBox(panel, label="Enable AI auto-complete")
        features_sizer.Add(self.enable_autocomplete, 0, wx.ALL, 5)
        
        self.enable_grammar_check = wx.CheckBox(panel, label="Enable grammar checking")
        features_sizer.Add(self.enable_grammar_check, 0, wx.ALL, 5)
        
        vbox.Add(features_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(vbox)
        return panel
    
    def CreateBehaviorPanel(self, parent):
        """Create behavior settings panel"""
        panel = wx.Panel(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Auto-save
        autosave_box = wx.StaticBox(panel, label="Auto-save")
        autosave_sizer = wx.StaticBoxSizer(autosave_box, wx.VERTICAL)
        
        self.enable_autosave = wx.CheckBox(panel, label="Enable auto-save")
        autosave_sizer.Add(self.enable_autosave, 0, wx.ALL, 5)
        
        interval_sizer = wx.BoxSizer(wx.HORIZONTAL)
        interval_sizer.Add(wx.StaticText(panel, label="Interval (seconds):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.autosave_interval = wx.SpinCtrl(panel, value="60", min=10, max=600)
        interval_sizer.Add(self.autosave_interval, 0, wx.ALL, 5)
        
        autosave_sizer.Add(interval_sizer, 0, wx.EXPAND)
        
        vbox.Add(autosave_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Session
        session_box = wx.StaticBox(panel, label="Session")
        session_sizer = wx.StaticBoxSizer(session_box, wx.VERTICAL)
        
        self.restore_session = wx.CheckBox(panel, label="Restore tabs on startup")
        self.restore_session.SetValue(True)
        session_sizer.Add(self.restore_session, 0, wx.ALL, 5)
        
        vbox.Add(session_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(vbox)
        return panel
    
    def OnThemeChange(self, event):
        """Handle theme change"""
        theme_mgr = ThemeManager()
        themes = theme_mgr.get_all_themes()
        selection = self.theme_choice.GetSelection()
        
        if selection >= 0:
            theme_key = themes[selection][0]
            self.current_theme = theme_key
            self.parent_frame.ApplyTheme(theme_key)
    
    def OnApply(self, event):
        """Apply settings without closing"""
        # Apply theme
        self.OnThemeChange(None)
        
        # Apply other settings (to be implemented in parent frame)
        # self.parent_frame.ApplySettings(...)
    
    def OnOK(self, event):
        """Apply and close"""
        self.OnApply(None)
        self.Close()