import wx

class AboutDialog(wx.Dialog):
    """Professional About dialog with version and credits"""
    
    def __init__(self, parent):
        super().__init__(parent, title="About Notepad PRO", size=(450, 400))
        self.CenterOnParent()
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.AddSpacer(20)
        
        # App name
        app_name = wx.StaticText(panel, label="Notepad PRO")
        font = app_name.GetFont()
        font.SetPointSize(24)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        app_name.SetFont(font)
        vbox.Add(app_name, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(5)
        
        # Version
        version = wx.StaticText(panel, label="Version 2.0 PRO")
        font = version.GetFont()
        font.SetPointSize(10)
        version.SetFont(font)
        vbox.Add(version, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(20)
        
        # Description
        desc = wx.StaticText(panel, label="AI-Powered Professional Text Editor")
        font = desc.GetFont()
        font.SetPointSize(11)
        desc.SetFont(font)
        vbox.Add(desc, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(20)
        
        # Features
        features_box = wx.StaticBox(panel, label="Features")
        features_sizer = wx.StaticBoxSizer(features_box, wx.VERTICAL)
        
        features_text = """• 6 Professional Themes (Light, Dark, Monokai, Solarized, Nord, Dracula)
• Real-time Statistics (Words, Characters, Line/Column)
• Advanced Find & Replace with Regex Support
• AI-Powered Writing Assistance
• Multi-tab Document Management
• Session Persistence
• Rich Text Formatting
• Comprehensive Settings"""
        
        features_label = wx.StaticText(panel, label=features_text)
        font = features_label.GetFont()
        font.SetPointSize(9)
        features_label.SetFont(font)
        features_sizer.Add(features_label, 0, wx.ALL, 10)
        
        vbox.Add(features_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        
        vbox.AddSpacer(20)
        
        # Credits
        credits = wx.StaticText(panel, label="Built with wxPython • Powered by Ollama AI")
        font = credits.GetFont()
        font.SetPointSize(8)
        credits.SetFont(font)
        vbox.Add(credits, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(10)
        
        # Copyright
        copyright_text = wx.StaticText(panel, label="© 2024 Notepad PRO. All rights reserved.")
        font = copyright_text.GetFont()
        font.SetPointSize(8)
        copyright_text.SetFont(font)
        vbox.Add(copyright_text, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(20)
        
        # Close button
        close_btn = wx.Button(panel, label="Close")
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        vbox.Add(close_btn, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(20)
        
        panel.SetSizer(vbox)
