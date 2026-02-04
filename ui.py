import wx
import os

class NotepadAI(wx.Frame):
    def __init__(self, parent, title):
        super(NotepadAI, self).__init__(parent, title=title, size=(1000, 700))
        self.current_file = None
        self.is_modified = False
        self.InitMenuBar()
        self.InitUI()
        self.BindEvents()
        self.Center()
        self.Show()

    def InitMenuBar(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New\tCtrl+N")
        file_menu.Append(wx.ID_OPEN, "&Open...\tCtrl+O")
        file_menu.Append(wx.ID_SAVE, "&Save\tCtrl+S")
        file_menu.Append(wx.ID_SAVEAS, "Save &As...\tCtrl+Shift+S")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4")
        menubar.Append(file_menu, "&File")
        self.SetMenuBar(menubar)

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_RICH2)
        font = wx.Font(11, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.text_ctrl.SetFont(font)
        vbox.Add(self.text_ctrl, 1, wx.EXPAND)
        panel.SetSizer(vbox)

    def BindEvents(self):
        self.Bind(wx.EVT_MENU, self.OnNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)

    def OnNew(self, event):
        self.text_ctrl.Clear()
        self.current_file = None
        self.SetTitle("Untitled - Notepad PRO")

    def OnOpen(self, event):
        with wx.FileDialog(self, "Open", wildcard="*.*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    self.text_ctrl.SetValue(f.read())
                self.current_file = path
                self.SetTitle(f"{os.path.basename(path)} - Notepad PRO")
