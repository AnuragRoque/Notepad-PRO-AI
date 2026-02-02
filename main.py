import wx
import sys
from ui import NotepadAI

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

if __name__ == "__main__":
    app = wx.App()
    frame = NotepadAI(None, "Notepad PRO")
    app.MainLoop()
