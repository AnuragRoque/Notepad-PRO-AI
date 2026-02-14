import wx
import wx.stc as stc
import os

class SyntaxEditor(stc.StyledTextCtrl):
    """Advanced code editor with syntax highlighting and line numbers"""
    
    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_language = "text"
        
        # Configure editor
        self.SetupEditor()
        self.SetupLineNumbers()
        self.SetupMargins()
        
    def SetupEditor(self):
        """Configure basic editor settings"""
        # Use monospace font
        font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Consolas")
        self.StyleSetFont(stc.STC_STYLE_DEFAULT, font)
        
        # Set tab width
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        self.SetIndent(4)
        self.SetBackSpaceUnIndents(True)
        
        # Enable auto-indent
        self.SetProperty("tab.timmy.whinge.level", "1")
        
        # Show whitespace
        self.SetViewWhiteSpace(False)
        
        # Enable line wrapping
        self.SetWrapMode(stc.STC_WRAP_WORD)
        
        # Current line highlighting
        self.SetCaretLineVisible(True)
        
        # Bracket matching
        self.SetProperty("fold", "1")
        
    def SetupLineNumbers(self):
        """Setup line number margin"""
        self.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(0, 40)
        
    def SetupMargins(self):
        """Setup folding margin"""
        self.SetMarginType(1, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(1, stc.STC_MASK_FOLDERS)
        self.SetMarginWidth(1, 16)
        self.SetMarginSensitive(1, True)
        
        # Folding markers
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER)
        
    def SetLanguage(self, language):
        """Set syntax highlighting for language"""
        self.current_language = language.lower()
        
        if language == "python":
            self.SetLexer(stc.STC_LEX_PYTHON)
            self.SetKeyWords(0, "and as assert break class continue def del elif else except exec finally for from global if import in is lambda not or pass print raise return try while with yield")
        elif language == "javascript":
            self.SetLexer(stc.STC_LEX_CPP)
            self.SetKeyWords(0, "break case catch continue debugger default delete do else finally for function if in instanceof new return switch this throw try typeof var void while with let const class extends super")
        elif language == "html":
            self.SetLexer(stc.STC_LEX_HTML)
        elif language == "css":
            self.SetLexer(stc.STC_LEX_CSS)
        elif language == "markdown":
            self.SetLexer(stc.STC_LEX_MARKDOWN)
        elif language == "json":
            self.SetLexer(stc.STC_LEX_JSON)
        else:
            self.SetLexer(stc.STC_LEX_NULL)
        
        self.ApplyTheme()
    
    def ApplyTheme(self, theme_name=None):
        """Apply theme colors to editor"""
        if theme_name:
            theme = self.theme_manager.get_theme(theme_name)
        else:
            theme = self.theme_manager.get_theme()
        
        # Background and foreground
        self.StyleSetBackground(stc.STC_STYLE_DEFAULT, theme['bg'])
        self.StyleSetForeground(stc.STC_STYLE_DEFAULT, theme['fg'])
        
        # Line numbers
        self.StyleSetBackground(stc.STC_STYLE_LINENUMBER, theme['line_number_bg'])
        self.StyleSetForeground(stc.STC_STYLE_LINENUMBER, theme['line_number_fg'])
        
        # Current line
        self.SetCaretLineBackground(theme['current_line'])
        
        # Selection
        self.SetSelBackground(True, theme['selection_bg'])
        self.SetSelForeground(True, theme['selection_fg'])
        
        # Syntax highlighting colors (Python example)
        if self.current_language == "python":
            # Comments
            self.StyleSetForeground(stc.STC_P_COMMENTLINE, "#6A9955")
            self.StyleSetForeground(stc.STC_P_COMMENTBLOCK, "#6A9955")
            
            # Strings
            self.StyleSetForeground(stc.STC_P_STRING, "#CE9178")
            self.StyleSetForeground(stc.STC_P_CHARACTER, "#CE9178")
            self.StyleSetForeground(stc.STC_P_TRIPLE, "#CE9178")
            self.StyleSetForeground(stc.STC_P_TRIPLEDOUBLE, "#CE9178")
            
            # Keywords
            self.StyleSetForeground(stc.STC_P_WORD, "#569CD6")
            self.StyleSetBold(stc.STC_P_WORD, True)
            
            # Numbers
            self.StyleSetForeground(stc.STC_P_NUMBER, "#B5CEA8")
            
            # Operators
            self.StyleSetForeground(stc.STC_P_OPERATOR, "#D4D4D4")
            
            # Class names
            self.StyleSetForeground(stc.STC_P_CLASSNAME, "#4EC9B0")
            
            # Function names
            self.StyleSetForeground(stc.STC_P_DEFNAME, "#DCDCAA")
        
        self.StyleClearAll()
        self.Colourise(0, -1)
    
    def DetectLanguageFromExtension(self, filename):
        """Auto-detect language from file extension"""
        if not filename:
            return "text"
        
        ext = os.path.splitext(filename)[1].lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.md': 'markdown',
            '.json': 'json',
            '.txt': 'text'
        }
        
        return language_map.get(ext, 'text')
    
    def ToggleLineNumbers(self):
        """Toggle line number visibility"""
        if self.GetMarginWidth(0) > 0:
            self.SetMarginWidth(0, 0)
        else:
            self.SetMarginWidth(0, 40)
    
    def ZoomIn(self):
        """Increase font size"""
        self.CmdKeyExecute(stc.STC_CMD_ZOOMIN)
    
    def ZoomOut(self):
        """Decrease font size"""
        self.CmdKeyExecute(stc.STC_CMD_ZOOMOUT)
    
    def ZoomReset(self):
        """Reset zoom to default"""
        self.SetZoom(0)
