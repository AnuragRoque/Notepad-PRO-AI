import wx

class FocusMode(wx.Frame):
    """Distraction-free focus mode for writing"""
    
    def __init__(self, parent, content="", theme="dark"):
        super().__init__(parent, title="Focus Mode", style=wx.DEFAULT_FRAME_STYLE)
        self.parent_frame = parent
        self.Maximize(True)
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour("#1e1e1e" if theme == "dark" else "#ffffff"))
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Add some top padding
        vbox.AddSpacer(50)
        
        # Create centered text area
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        
        # Text control with max width for better readability
        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.BORDER_NONE, size=(800, -1))
        
        # Set font
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI")
        self.text_ctrl.SetFont(font)
        
        # Set colors
        if theme == "dark":
            self.text_ctrl.SetBackgroundColour(wx.Colour("#1e1e1e"))
            self.text_ctrl.SetForegroundColour(wx.Colour("#cccccc"))
        else:
            self.text_ctrl.SetBackgroundColour(wx.Colour("#ffffff"))
            self.text_ctrl.SetForegroundColour(wx.Colour("#000000"))
        
        self.text_ctrl.SetValue(content)
        
        hbox.Add(self.text_ctrl, 0, wx.EXPAND)
        hbox.AddStretchSpacer(1)
        
        vbox.Add(hbox, 1, wx.EXPAND)
        
        panel.SetSizer(vbox)
        
        # Bind escape key to exit
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)
        
        # Show instructions
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Press ESC to exit focus mode | F11 for fullscreen")
        
        self.Show()
    
    def OnKeyPress(self, event):
        """Handle key presses"""
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            # Return content to parent
            if self.parent_frame:
                text_ctrl = self.parent_frame.GetCurrentTextCtrl()
                if text_ctrl:
                    text_ctrl.SetValue(self.text_ctrl.GetValue())
            self.Close()
        elif event.GetKeyCode() == wx.WXK_F11:
            # Toggle fullscreen
            self.ShowFullScreen(not self.IsFullScreen())
        else:
            event.Skip()
    
    def GetContent(self):
        """Get current content"""
        return self.text_ctrl.GetValue()
