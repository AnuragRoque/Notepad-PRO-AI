import wx

class StatusBar(wx.StatusBar):
    """Professional status bar with real-time document statistics and indicators"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Create 6 fields: [File Info | Line:Col | Words | Chars | Encoding | AI Status]
        self.SetFieldsCount(6)
        self.SetStatusWidths([-2, 100, 100, 100, 80, 120])
        
        # Initialize values
        self.SetStatusText("Ready", 0)
        self.SetStatusText("Ln 1, Col 1", 1)
        self.SetStatusText("Words: 0", 2)
        self.SetStatusText("Chars: 0", 3)
        self.SetStatusText("UTF-8", 4)
        self.SetStatusText("AI: Ready", 5)
        
        # Store current theme for styling
        self.current_theme = "light"
        
    def UpdatePosition(self, line, col):
        """Update line and column position"""
        self.SetStatusText(f"Ln {line}, Col {col}", 1)
    
    def UpdateStats(self, text):
        """Update word count and character count"""
        if not text:
            words = 0
            chars = 0
        else:
            # Count words (split by whitespace)
            words = len(text.split())
            # Count characters (including spaces)
            chars = len(text)
        
        self.SetStatusText(f"Words: {words}", 2)
        self.SetStatusText(f"Chars: {chars}", 3)
    
    def UpdateFileInfo(self, file_path=None, modified=False):
        """Update file information in status bar"""
        if file_path:
            import os
            filename = os.path.basename(file_path)
            status = f"{'● ' if modified else ''}{filename}"
        else:
            status = f"{'● ' if modified else ''}Untitled"
        
        self.SetStatusText(status, 0)
    
    def UpdateEncoding(self, encoding="UTF-8"):
        """Update file encoding display"""
        self.SetStatusText(encoding, 4)
    
    def SetAIStatus(self, status):
        """Update AI status (Ready, Processing, Error)"""
        if status == "processing":
            self.SetStatusText("AI: Processing...", 5)
        elif status == "error":
            self.SetStatusText("AI: Error", 5)
        else:
            self.SetStatusText("AI: Ready", 5)
    
    def ApplyTheme(self, theme):
        """Apply theme colors to status bar"""
        self.current_theme = theme
        
        if theme == "dark":
            bg_color = wx.Colour("#1e1e1e")
            fg_color = wx.Colour("#cccccc")
        else:
            bg_color = wx.Colour("#f0f0f0")
            fg_color = wx.Colour("#333333")
        
        self.SetBackgroundColour(bg_color)
        self.SetForegroundColour(fg_color)
        
        # Force update all status text to apply new foreground color
        for i in range(self.GetFieldsCount()):
            text = self.GetStatusText(i)
            self.SetStatusText(text, i)
        
        self.Refresh()
        self.Update()
