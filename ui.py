import wx

class NotepadAI(wx.Frame):
    def __init__(self, parent, title):
        super(NotepadAI, self).__init__(parent, title=title, size=(1000, 700))
        self.InitMenuBar()
        self.InitUI()
        self.Center()
        self.Show()

    def InitMenuBar(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New\tCtrl+N")
        file_menu.Append(wx.ID_OPEN, "&Open...\tCtrl+O")
        file_menu.Append(wx.ID_SAVE, "&Save\tCtrl+S")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4")
        
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_CUT, "Cu&t\tCtrl+X")
        edit_menu.Append(wx.ID_COPY, "&Copy\tCtrl+C")
        edit_menu.Append(wx.ID_PASTE, "&Paste\tCtrl+V")
        
        menubar.Append(file_menu, "&File")
        menubar.Append(edit_menu, "&Edit")
        self.SetMenuBar(menubar)

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        vbox.Add(self.text_ctrl, 1, wx.EXPAND)
        panel.SetSizer(vbox)
