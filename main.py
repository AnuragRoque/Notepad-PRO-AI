import wx
import sys

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None, title="Notepad PRO", size=(900, 650))
    frame.Show()
    app.MainLoop()
