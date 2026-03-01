import wx
import os

class FileExplorer(wx.Panel):
    """File explorer sidebar for quick file navigation"""
    
    def __init__(self, parent, main_frame):
        super().__init__(parent)
        self.main_frame = main_frame
        self.current_directory = os.path.expanduser("~\\Documents")
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Toolbar
        toolbar = wx.Panel(self)
        tb_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.refresh_btn = wx.Button(toolbar, label="↻", size=(30, 25))
        self.home_btn = wx.Button(toolbar, label="🏠", size=(30, 25))
        self.up_btn = wx.Button(toolbar, label="↑", size=(30, 25))
        
        self.refresh_btn.Bind(wx.EVT_BUTTON, self.OnRefresh)
        self.home_btn.Bind(wx.EVT_BUTTON, self.OnHome)
        self.up_btn.Bind(wx.EVT_BUTTON, self.OnUp)
        
        tb_sizer.Add(self.refresh_btn, 0, wx.ALL, 2)
        tb_sizer.Add(self.home_btn, 0, wx.ALL, 2)
        tb_sizer.Add(self.up_btn, 0, wx.ALL, 2)
        
        toolbar.SetSizer(tb_sizer)
        vbox.Add(toolbar, 0, wx.EXPAND | wx.ALL, 2)
        
        # Path display
        self.path_text = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.path_text.SetValue(self.current_directory)
        vbox.Add(self.path_text, 0, wx.EXPAND | wx.ALL, 2)
        
        # File tree
        self.tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)
        
        vbox.Add(self.tree, 1, wx.EXPAND | wx.ALL, 2)
        
        self.SetSizer(vbox)
        
        # Populate tree
        self.PopulateTree()
    
    def PopulateTree(self):
        """Populate tree with files and folders"""
        self.tree.DeleteAllItems()
        root = self.tree.AddRoot(self.current_directory)
        
        try:
            items = os.listdir(self.current_directory)
            
            # Separate folders and files
            folders = []
            files = []
            
            for item in items:
                full_path = os.path.join(self.current_directory, item)
                if os.path.isdir(full_path):
                    folders.append(item)
                else:
                    files.append(item)
            
            # Add folders first
            for folder in sorted(folders):
                item = self.tree.AppendItem(root, f"📁 {folder}")
                self.tree.SetItemData(item, os.path.join(self.current_directory, folder))
            
            # Add files
            for file in sorted(files):
                icon = self.GetFileIcon(file)
                item = self.tree.AppendItem(root, f"{icon} {file}")
                self.tree.SetItemData(item, os.path.join(self.current_directory, file))
            
            # Don't expand hidden root - it causes assertion error
            # self.tree.Expand(root)
        except PermissionError:
            pass
    
    def GetFileIcon(self, filename):
        """Get icon for file type"""
        ext = os.path.splitext(filename)[1].lower()
        
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.md': '📝',
            '.txt': '📄',
            '.json': '📋',
            '.xml': '📋',
            '.jpg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.pdf': '📕',
            '.zip': '📦',
        }
        
        return icons.get(ext, '📄')
    
    def OnItemActivated(self, event):
        """Handle double-click on item"""
        item = event.GetItem()
        path = self.tree.GetItemData(item)
        
        if os.path.isdir(path):
            # Navigate to directory
            self.current_directory = path
            self.path_text.SetValue(path)
            self.PopulateTree()
        else:
            # Open file
            self.main_frame.OpenFile(path)
    
    def OnSelectionChanged(self, event):
        """Handle selection change"""
        pass
    
    def OnRefresh(self, event):
        """Refresh file list"""
        self.PopulateTree()
    
    def OnHome(self, event):
        """Go to home directory"""
        self.current_directory = os.path.expanduser("~\\Documents")
        self.path_text.SetValue(self.current_directory)
        self.PopulateTree()
    
    def OnUp(self, event):
        """Go up one directory"""
        parent = os.path.dirname(self.current_directory)
        if parent and parent != self.current_directory:
            self.current_directory = parent
            self.path_text.SetValue(self.current_directory)
            self.PopulateTree()
    
    def SetDirectory(self, directory):
        """Set current directory"""
        if os.path.isdir(directory):
            self.current_directory = directory
            self.path_text.SetValue(directory)
            self.PopulateTree()
    
    def ApplyTheme(self, theme):
        """Apply theme to explorer"""
        if theme == "dark":
            bg = "#1e1e1e"
            fg = "#cccccc"
        else:
            bg = "#ffffff"
            fg = "#000000"
        
        self.SetBackgroundColour(wx.Colour(bg))
        self.tree.SetBackgroundColour(wx.Colour(bg))
        self.tree.SetForegroundColour(wx.Colour(fg))
        self.Refresh()
