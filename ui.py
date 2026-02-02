import wx

class NotepadAI(wx.Frame):
    def __init__(self, parent, title):
        super(NotepadAI, self).__init__(parent, title=title, size=(1000, 700))
        self.Center()
        self.InitUI()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        vbox.Add(self.text_ctrl, 1, wx.EXPAND)
        panel.SetSizer(vbox)
