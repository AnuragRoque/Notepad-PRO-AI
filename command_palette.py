import wx

class CommandPalette(wx.Dialog):
    """Command palette for quick access to all features"""
    
    def __init__(self, parent):
        super().__init__(parent, title="Command Palette", size=(600, 400))
        self.parent_frame = parent
        self.CenterOnParent()
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Search box
        self.search_ctrl = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.search_ctrl.SetDescriptiveText("Type to search commands...")
        self.search_ctrl.Bind(wx.EVT_TEXT, self.OnSearch)
        self.search_ctrl.Bind(wx.EVT_TEXT_ENTER, self.OnExecute)
        vbox.Add(self.search_ctrl, 0, wx.EXPAND | wx.ALL, 10)
        
        # Command list
        self.command_list = wx.ListBox(panel)
        self.command_list.Bind(wx.EVT_LISTBOX_DCLICK, self.OnExecute)
        vbox.Add(self.command_list, 1, wx.EXPAND | wx.ALL, 10)
        
        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        
        execute_btn = wx.Button(panel, label="Execute")
        cancel_btn = wx.Button(panel, label="Cancel")
        
        execute_btn.Bind(wx.EVT_BUTTON, self.OnExecute)
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        btn_sizer.Add(execute_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        
        vbox.Add(btn_sizer, 0, wx.EXPAND)
        
        panel.SetSizer(vbox)
        
        # Define all commands
        self.commands = {
            "New Tab": lambda: parent.OnNewTab(None),
            "Close Tab": lambda: parent.OnCloseTab(None),
            "Next Tab": lambda: parent.OnNextTab(None),
            "Previous Tab": lambda: parent.OnPrevTab(None),
            "Open File": lambda: parent.OnOpen(None),
            "Save File": lambda: parent.OnSave(None),
            "Save As": lambda: parent.OnSaveAs(None),
            "Find": lambda: parent.OnFind(None),
            "Settings": lambda: parent.OnSettings(None),
            "About": lambda: parent.OnAbout(None),
            "Toggle File Explorer": lambda: parent.ToggleFileExplorer(),
            "Toggle AI Chat": lambda: parent.ToggleAIChat(),
            "Focus Mode": lambda: parent.EnterFocusMode(),
            "Toggle Line Numbers": lambda: parent.ToggleLineNumbers(),
            "Zoom In": lambda: parent.ZoomIn(),
            "Zoom Out": lambda: parent.ZoomOut(),
            "Zoom Reset": lambda: parent.ZoomReset(),
            "AI: Rewrite": lambda: parent.RunAI("rewrite_clear"),
            "AI: Summarize": lambda: parent.RunAI("summarise"),
            "AI: Make Shorter": lambda: parent.RunAI("shorter"),
            "AI: Make Longer": lambda: parent.RunAI("longer"),
            "AI: Formal Tone": lambda: parent.RunAI("tone_formal"),
            "AI: Casual Tone": lambda: parent.RunAI("tone_casual"),
            "Theme: Light": lambda: parent.ApplyTheme("light"),
            "Theme: Dark": lambda: parent.ApplyTheme("dark"),
            "Theme: Monokai": lambda: parent.ApplyTheme("monokai"),
            "Theme: Solarized": lambda: parent.ApplyTheme("solarized_dark"),
            "Theme: Nord": lambda: parent.ApplyTheme("nord"),
            "Theme: Dracula": lambda: parent.ApplyTheme("dracula"),
        }
        
        # Populate list
        self.all_commands = list(self.commands.keys())
        self.command_list.Set(self.all_commands)
        
        # Focus search
        self.search_ctrl.SetFocus()
    
    def OnSearch(self, event):
        """Filter commands based on search"""
        search_term = self.search_ctrl.GetValue().lower()
        
        if not search_term:
            filtered = self.all_commands
        else:
            filtered = [cmd for cmd in self.all_commands if search_term in cmd.lower()]
        
        self.command_list.Set(filtered)
        
        # Select first item
        if filtered:
            self.command_list.SetSelection(0)
    
    def OnExecute(self, event):
        """Execute selected command"""
        selection = self.command_list.GetSelection()
        if selection != wx.NOT_FOUND:
            command_name = self.command_list.GetString(selection)
            command = self.commands.get(command_name)
            
            if command:
                self.Close()
                wx.CallAfter(command)
