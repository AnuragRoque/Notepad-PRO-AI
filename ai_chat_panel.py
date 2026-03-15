import wx
import wx.richtext as rt
import threading
from ai import ask_ollama

class AIChatPanel(wx.Panel):
    """AI chat sidebar for interactive assistance"""
    
    def __init__(self, parent, main_frame):
        super().__init__(parent, size=(300, -1))
        self.main_frame = main_frame
        self.chat_history = []
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(self, label="AI Assistant")
        font = title.GetFont()
        font.SetPointSize(12)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        vbox.Add(title, 0, wx.ALL, 10)
        
        # Chat display
        self.chat_display = rt.RichTextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.chat_display.SetMinSize((280, 400))
        vbox.Add(self.chat_display, 1, wx.EXPAND | wx.ALL, 5)
        
        # Input area
        input_label = wx.StaticText(self, label="Ask AI:")
        vbox.Add(input_label, 0, wx.LEFT | wx.RIGHT, 10)
        
        self.input_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 80))
        vbox.Add(self.input_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.send_btn = wx.Button(self, label="Send")
        self.clear_btn = wx.Button(self, label="Clear")
        self.insert_btn = wx.Button(self, label="Insert to Doc")
        
        self.send_btn.Bind(wx.EVT_BUTTON, self.OnSend)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.OnClear)
        self.insert_btn.Bind(wx.EVT_BUTTON, self.OnInsert)
        
        btn_sizer.Add(self.send_btn, 0, wx.ALL, 2)
        btn_sizer.Add(self.clear_btn, 0, wx.ALL, 2)
        btn_sizer.Add(self.insert_btn, 0, wx.ALL, 2)
        
        vbox.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Quick actions
        quick_label = wx.StaticText(self, label="Quick Actions:")
        vbox.Add(quick_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        quick_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.explain_btn = wx.Button(self, label="Explain Selection")
        self.improve_btn = wx.Button(self, label="Improve Selection")
        self.translate_btn = wx.Button(self, label="Translate")
        
        self.explain_btn.Bind(wx.EVT_BUTTON, self.OnExplain)
        self.improve_btn.Bind(wx.EVT_BUTTON, self.OnImprove)
        self.translate_btn.Bind(wx.EVT_BUTTON, self.OnTranslate)
        
        quick_sizer.Add(self.explain_btn, 0, wx.EXPAND | wx.ALL, 2)
        quick_sizer.Add(self.improve_btn, 0, wx.EXPAND | wx.ALL, 2)
        quick_sizer.Add(self.translate_btn, 0, wx.EXPAND | wx.ALL, 2)
        
        vbox.Add(quick_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(vbox)
        
        # Add welcome message
        self.AddMessage("AI", "Hello! I'm your AI assistant. Ask me anything or use quick actions on your selected text.")
        
        self.last_response = ""
    
    def AddMessage(self, sender, message):
        """Add message to chat display"""
        self.chat_display.BeginBold()
        if sender == "You":
            self.chat_display.BeginTextColour(wx.Colour("#0078d4"))
        else:
            self.chat_display.BeginTextColour(wx.Colour("#16c60c"))
        
        self.chat_display.WriteText(f"{sender}: ")
        self.chat_display.EndTextColour()
        self.chat_display.EndBold()
        
        self.chat_display.WriteText(f"{message}\n\n")
        self.chat_display.ShowPosition(self.chat_display.GetLastPosition())
    
    def OnSend(self, event):
        """Send message to AI"""
        message = self.input_ctrl.GetValue().strip()
        if not message:
            return
        
        self.AddMessage("You", message)
        self.input_ctrl.Clear()
        self.send_btn.Enable(False)
        self.send_btn.SetLabel("Thinking...")
        
        def worker():
            response = ask_ollama(message)
            wx.CallAfter(self.OnAIResponse, response)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def OnAIResponse(self, response):
        """Handle AI response"""
        self.AddMessage("AI", response)
        self.last_response = response
        self.send_btn.Enable(True)
        self.send_btn.SetLabel("Send")
    
    def OnClear(self, event):
        """Clear chat history"""
        self.chat_display.Clear()
        self.chat_history = []
        self.AddMessage("AI", "Chat cleared. How can I help you?")
    
    def OnInsert(self, event):
        """Insert last AI response into document"""
        if self.last_response:
            text_ctrl = self.main_frame.GetCurrentTextCtrl()
            if text_ctrl:
                text_ctrl.WriteText(self.last_response)
    
    def OnExplain(self, event):
        """Explain selected text"""
        text = self.main_frame.GetSelectedOrAllText()
        if text.strip():
            self.input_ctrl.SetValue(f"Explain this:\n\n{text}")
            self.OnSend(None)
    
    def OnImprove(self, event):
        """Improve selected text"""
        text = self.main_frame.GetSelectedOrAllText()
        if text.strip():
            self.input_ctrl.SetValue(f"Improve this text:\n\n{text}")
            self.OnSend(None)
    
    def OnTranslate(self, event):
        """Translate selected text"""
        text = self.main_frame.GetSelectedOrAllText()
        if text.strip():
            # Ask for target language
            dlg = wx.TextEntryDialog(self, "Translate to which language?", "Translation", "Spanish")
            if dlg.ShowModal() == wx.ID_OK:
                language = dlg.GetValue()
                self.input_ctrl.SetValue(f"Translate this to {language}:\n\n{text}")
                self.OnSend(None)
            dlg.Destroy()
    
    def ApplyTheme(self, theme):
        """Apply theme to chat panel"""
        if theme == "dark":
            bg = "#1e1e1e"
            fg = "#cccccc"
        else:
            bg = "#f5f5f5"
            fg = "#000000"
        
        self.SetBackgroundColour(wx.Colour(bg))
        self.chat_display.SetBackgroundColour(wx.Colour(bg))
        self.chat_display.SetForegroundColour(wx.Colour(fg))
        self.Refresh()
