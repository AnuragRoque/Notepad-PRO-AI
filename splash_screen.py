import wx
import wx.lib.agw.shapedbutton as SB

class SplashScreen(wx.Frame):
    """Professional splash screen with fade animation"""
    
    def __init__(self):
        super().__init__(None, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.FRAME_SHAPED)
        
        self.SetSize((500, 300))
        self.CenterOnScreen()
        
        # Create panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour("#1e1e1e"))
        
        # Main sizer
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Add spacing
        vbox.AddSpacer(40)
        
        # App name
        app_name = wx.StaticText(panel, label="Notepad PRO")
        font = app_name.GetFont()
        font.SetPointSize(32)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        app_name.SetFont(font)
        app_name.SetForegroundColour(wx.Colour("#ffffff"))
        vbox.Add(app_name, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(10)
        
        # Tagline
        tagline = wx.StaticText(panel, label="AI-Powered Professional Text Editor")
        font = tagline.GetFont()
        font.SetPointSize(11)
        tagline.SetFont(font)
        tagline.SetForegroundColour(wx.Colour("#cccccc"))
        vbox.Add(tagline, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(30)
        
        # Loading animation (gauge)
        self.gauge = wx.Gauge(panel, range=100, size=(300, 8))
        self.gauge.SetBackgroundColour(wx.Colour("#2d2d30"))
        self.gauge.SetForegroundColour(wx.Colour("#0078d4"))
        vbox.Add(self.gauge, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(10)
        
        # Loading text
        self.loading_text = wx.StaticText(panel, label="Loading...")
        font = self.loading_text.GetFont()
        font.SetPointSize(9)
        self.loading_text.SetFont(font)
        self.loading_text.SetForegroundColour(wx.Colour("#999999"))
        vbox.Add(self.loading_text, 0, wx.ALIGN_CENTER)
        
        vbox.AddSpacer(40)
        
        # Version
        version = wx.StaticText(panel, label="Version 2.0 PRO")
        font = version.GetFont()
        font.SetPointSize(8)
        version.SetFont(font)
        version.SetForegroundColour(wx.Colour("#666666"))
        vbox.Add(version, 0, wx.ALIGN_CENTER)
        
        panel.SetSizer(vbox)
        
        # Timer for progress animation
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.progress = 0
        
        # Opacity for fade effect
        self.opacity = 0
        self.fade_in = True
        
    def Start(self, duration=2000):
        """Start the splash screen with animation"""
        self.Show()
        
        # Start fade in
        self.fade_timer = wx.Timer(self)
        self.fade_timer.Bind(wx.EVT_TIMER, self.OnFadeTimer)
        self.fade_timer.Start(20)
        
        # Start progress
        self.timer.Start(duration // 100)
        
        # Auto close after duration
        wx.CallLater(duration, self.Close)
    
    def OnTimer(self, event):
        """Update progress bar"""
        self.progress += 2
        if self.progress <= 100:
            self.gauge.SetValue(self.progress)
            
            # Update loading text
            if self.progress < 30:
                self.loading_text.SetLabel("Initializing...")
            elif self.progress < 60:
                self.loading_text.SetLabel("Loading AI models...")
            elif self.progress < 90:
                self.loading_text.SetLabel("Preparing workspace...")
            else:
                self.loading_text.SetLabel("Almost ready...")
        else:
            self.timer.Stop()
    
    def OnFadeTimer(self, event):
        """Handle fade in/out animation"""
        if self.fade_in:
            self.opacity += 15
            if self.opacity >= 255:
                self.opacity = 255
                self.fade_timer.Stop()
        else:
            self.opacity -= 15
            if self.opacity <= 0:
                self.opacity = 0
                self.fade_timer.Stop()
                self.Destroy()
        
        # Note: SetTransparent is Windows-specific
        try:
            self.SetTransparent(self.opacity)
        except:
            pass
    
    def Close(self):
        """Close with fade out"""
        self.fade_in = False
        self.fade_timer.Start(20)
