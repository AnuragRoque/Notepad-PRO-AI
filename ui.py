import wx
import wx.richtext as rt
import os
import threading
from ai import ask_ollama
from settings import SettingsDialog
from file_history import FileHistory
from tab_manager import TabManager
from status_bar import StatusBar
from theme_manager import ThemeManager
from find_replace_dialog import FindDialog
from about_dialog import AboutDialog

from focus_mode import FocusMode
from command_palette import CommandPalette

class NotepadAI(wx.Frame):
    def __init__(self, parent, title):
        super(NotepadAI, self).__init__(parent, title=title, size=(1400, 800))

        # Icon setup
        icon_path = r"C:\Users\anura\Documents\06 Project AI Models\08 AI Notepad\images\ai_img_notepad_ai_dark.png"
        if os.path.exists(icon_path):
            try:
                icon = wx.Icon(icon_path)
                self.SetIcon(icon)
            except:
                pass

        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.current_theme = self.theme_manager.current_theme
        
        self.file_history = FileHistory(max_files=10)
        self.tab_manager = TabManager()
        self.tabs_info = []  # Store info about each tab (file_path, modified, etc.)
        
        # Editor feature flags
        self.show_line_numbers = False
        self.word_wrap_enabled = True
        
        self.InitUI()
        self.ApplyTheme(self.current_theme)
        
        # Load previous session or create default tab
        self.LoadSession()
        
        self.Centre()
        self.Show()
        
        # Bind close event to save session
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Start cursor position timer
        self.cursor_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnCursorTimer, self.cursor_timer)
        self.cursor_timer.Start(100)  # Update every 100ms

    def InitUI(self):
        # Main container panel
        self.main_panel = wx.Panel(self)
        main_vbox = wx.BoxSizer(wx.VERTICAL)

        # --- TOOLBAR PANEL ---
        self.toolbar_panel = wx.Panel(self.main_panel)
        tb_sizer = wx.BoxSizer(wx.HORIZONTAL)

        tb_sizer.AddSpacer(10)

        # 1. Left Section (File/Edit/View)
        self.btn_file = self.CreateFlatButton(self.toolbar_panel, "File", self.OnFileMenu)
        self.btn_edit = self.CreateFlatButton(self.toolbar_panel, "Edit", self.OnEditMenu)
        self.btn_view = self.CreateFlatButton(self.toolbar_panel, "View", self.OnViewMenu)
        
        tb_sizer.Add(self.btn_file, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        tb_sizer.Add(self.btn_edit, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        tb_sizer.Add(self.btn_view, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        tb_sizer.AddSpacer(20)

        # 2. Center Section (Formatting)
        self.btn_h1 = self.CreateFlatButton(self.toolbar_panel, "H1", self.OnFormatH1)
        self.btn_bullet = self.CreateFlatButton(self.toolbar_panel, "•", self.OnFormatBullet)
        self.btn_bold = self.CreateFlatButton(self.toolbar_panel, "B", self.OnFormatBold, bold=True)
        self.btn_italic = self.CreateFlatButton(self.toolbar_panel, "I", self.OnFormatItalic, italic=True)

        tb_sizer.Add(self.btn_h1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        tb_sizer.Add(self.btn_bullet, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        tb_sizer.Add(self.btn_bold, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        tb_sizer.Add(self.btn_italic, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        tb_sizer.AddStretchSpacer(1)

        # 3. Right Section (AI + Settings + Help)
        self.btn_ai = self.CreateFlatButton(self.toolbar_panel, "✨", self.OnAIMenu)
        self.btn_settings = self.CreateFlatButton(self.toolbar_panel, "⚙", self.OnSettings)
        self.btn_help = self.CreateFlatButton(self.toolbar_panel, "?", self.OnHelpMenu)

        tb_sizer.Add(self.btn_ai, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        tb_sizer.Add(self.btn_settings, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        tb_sizer.Add(self.btn_help, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        tb_sizer.AddSpacer(10)

        self.toolbar_panel.SetSizer(tb_sizer)
        main_vbox.Add(self.toolbar_panel, 0, wx.EXPAND | wx.ALL, 0)

        # --- MAIN CONTENT AREA ---
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # CENTER - Notebook (Tabs)
        self.notebook = wx.Notebook(self.main_panel, style=wx.NB_TOP)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnTabChanged)
        self.notebook.Bind(wx.EVT_CONTEXT_MENU, self.OnTabContextMenu)
        
        # Bind keyboard shortcuts
        accel_entries = [
            (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('R'), 101),  # Rewrite
            (wx.ACCEL_CTRL, ord('F'), 102),  # Find
            (wx.ACCEL_CTRL, ord('N'), 103),  # New Tab
            (wx.ACCEL_CTRL, ord('W'), 104),  # Close Tab
            (wx.ACCEL_CTRL, ord('T'), 105),  # New Tab (alternative)
            (wx.ACCEL_CTRL, wx.WXK_TAB, 106),  # Next Tab
            (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, wx.WXK_TAB, 107),  # Previous Tab
            (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('P'), 108),  # Command Palette
            (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('F'), 109),  # Focus Mode
            (wx.ACCEL_CTRL, ord('='), 110),  # Zoom In
            (wx.ACCEL_CTRL, ord('-'), 111),  # Zoom Out
            (wx.ACCEL_CTRL, ord('0'), 112),  # Zoom Reset
            (wx.ACCEL_CTRL, ord('L'), 113),  # Toggle Line Numbers
            (wx.ACCEL_ALT, ord('Z'), 114),  # Toggle Word Wrap
        ]
        accel_tbl = wx.AcceleratorTable(accel_entries)
        self.SetAcceleratorTable(accel_tbl)
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("rewrite_prof"), id=101)
        self.Bind(wx.EVT_MENU, self.OnFind, id=102)
        self.Bind(wx.EVT_MENU, self.OnNewTab, id=103)
        self.Bind(wx.EVT_MENU, self.OnCloseTab, id=104)
        self.Bind(wx.EVT_MENU, self.OnNewTab, id=105)
        self.Bind(wx.EVT_MENU, self.OnNextTab, id=106)
        self.Bind(wx.EVT_MENU, self.OnPrevTab, id=107)
        self.Bind(wx.EVT_MENU, self.ShowCommandPalette, id=108)
        self.Bind(wx.EVT_MENU, self.EnterFocusMode, id=109)
        self.Bind(wx.EVT_MENU, self.ZoomIn, id=110)
        self.Bind(wx.EVT_MENU, self.ZoomOut, id=111)
        self.Bind(wx.EVT_MENU, self.ZoomReset, id=112)
        self.Bind(wx.EVT_MENU, lambda e: self.ToggleLineNumbers(), id=113)
        self.Bind(wx.EVT_MENU, lambda e: self.ToggleWordWrap(), id=114)

        content_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 0)
        
        main_vbox.Add(content_sizer, 1, wx.EXPAND)
        
        # Add status bar
        self.status_bar = StatusBar(self.main_panel)
        main_vbox.Add(self.status_bar, 0, wx.EXPAND)
        
        self.main_panel.SetSizer(main_vbox)

    def CreateTab(self, content="", file_path=None):
        """Create a new tab with a RichTextCtrl"""
        # Use BORDER_SIMPLE instead of BORDER_NONE to avoid white borders
        text_ctrl = rt.RichTextCtrl(self.notebook, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.BORDER_SIMPLE)
        
        # Set default font
        font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI")
        text_ctrl.SetFont(font)
        
        # Bind text change event
        text_ctrl.Bind(wx.EVT_TEXT, self.OnTextChange)
        text_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
        # Set content if provided
        if content:
            text_ctrl.SetValue(content)
            text_ctrl.SetModified(False)
        
        # Apply current theme
        self.ApplyThemeToTextCtrl(text_ctrl)
        
        # Determine tab label
        if file_path:
            label = os.path.basename(file_path)
        else:
            # Count untitled tabs
            untitled_count = sum(1 for info in self.tabs_info if info['path'] is None)
            label = f"Untitled {untitled_count + 1}" if untitled_count > 0 else "Untitled"
        
        # Add tab
        self.notebook.AddPage(text_ctrl, label)
        
        # Store tab info
        self.tabs_info.append({
            'path': file_path,
            'modified': False
        })
        
        # Switch to new tab
        self.notebook.SetSelection(self.notebook.GetPageCount() - 1)
        text_ctrl.SetFocus()
        
        return text_ctrl

    def CreateFlatButton(self, parent, label, handler, bold=False, italic=False):
        btn = wx.Button(parent, label=label, style=wx.BORDER_NONE)
        font = btn.GetFont()
        font.SetPointSize(10)
        if bold: font.SetWeight(wx.FONTWEIGHT_BOLD)
        if italic: font.SetStyle(wx.FONTSTYLE_ITALIC)
        font.SetFaceName("Segoe UI")
        btn.SetFont(font)
        
        if len(label) <= 2:
            btn.SetMinSize((35, 30))
        else:
            btn.SetMinSize((50, 30))
        
        btn.Bind(wx.EVT_BUTTON, handler)
        return btn

    def GetCurrentTextCtrl(self):
        """Get the text control of the current tab"""
        idx = self.notebook.GetSelection()
        if idx == -1:
            return None
        return self.notebook.GetPage(idx)
    
    def GetCurrentTabInfo(self):
        """Get info about current tab"""
        idx = self.notebook.GetSelection()
        if idx == -1 or idx >= len(self.tabs_info):
            return None
        return self.tabs_info[idx]

    # -----------------------------
    # TEXT HELPERS
    # -----------------------------
    def GetSelectedOrAllText(self):
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return ""
        txt = text_ctrl.GetStringSelection()
        if not txt:
            txt = text_ctrl.GetValue()
        return txt

    def ReplaceText(self, new_text):
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        
        # CRITICAL: Do NOT call SetStyle after Replace/SetValue - it breaks undo/redo!
        # Instead, ensure default style is set BEFORE modifying text
        fg_color = "#f1f1f1" if self.current_theme == "dark" else "#23272e"
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(fg_color))
        text_ctrl.SetDefaultStyle(attr)
        
        if text_ctrl.HasSelection():
            sel_range = text_ctrl.GetSelectionRange()
            start_pos = sel_range.GetStart()
            # Replace preserves undo/redo
            text_ctrl.Replace(sel_range.GetStart(), sel_range.GetEnd(), new_text)
            # Set cursor at end of replaced text
            text_ctrl.SetInsertionPoint(start_pos + len(new_text))
        else:
            # SetValue clears undo history, but that's expected for full replacement
            text_ctrl.SetValue(new_text)

    def EnsureTextColor(self, fg_color):
        """Apply correct text color to the most recently added text"""
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(fg_color))
        text_ctrl.SetDefaultStyle(attr)

    def OnTextChange(self, event):
        """Ensure newly typed/pasted text has the correct color"""
        event.Skip()
        theme = self.theme_manager.get_theme(self.current_theme)
        fg_color = theme['fg']
        
        # Mark tab as modified
        idx = self.notebook.GetSelection()
        if idx != -1 and idx < len(self.tabs_info):
            text_ctrl = self.GetCurrentTextCtrl()
            if text_ctrl and text_ctrl.IsModified():
                self.tabs_info[idx]['modified'] = True
                self.UpdateTabLabel(idx)
                self.UpdateStatusBar()
        
        wx.CallAfter(self.EnsureTextColor, fg_color)
    
    def UpdateTabLabel(self, idx):
        """Update tab label to show modified status"""
        if idx < 0 or idx >= len(self.tabs_info):
            return
        
        info = self.tabs_info[idx]
        if info['path']:
            label = os.path.basename(info['path'])
        else:
            untitled_num = idx + 1
            label = f"Untitled {untitled_num}" if untitled_num > 1 else "Untitled"
        
        if info['modified']:
            label = "● " + label
        
        self.notebook.SetPageText(idx, label)
    
    def OnTabChanged(self, event):
        """Handle tab change"""
        self.UpdateTitle()
        event.Skip()
    
    def UpdateTitle(self):
        """Update window title based on current tab"""
        info = self.GetCurrentTabInfo()
        if info and info['path']:
            self.SetTitle(f"Notepad PRO - {os.path.basename(info['path'])}")
        else:
            self.SetTitle("Notepad PRO")
    
    def UpdateStatusBar(self):
        """Update status bar with current document info"""
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        
        # Update stats
        text = text_ctrl.GetValue()
        self.status_bar.UpdateStats(text)
        
        # Update file info
        info = self.GetCurrentTabInfo()
        if info:
            self.status_bar.UpdateFileInfo(info['path'], info['modified'])
    
    def OnCursorTimer(self, event):
        """Update cursor position in status bar"""
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        
        # Get cursor position
        pos = text_ctrl.GetInsertionPoint()
        text = text_ctrl.GetValue()[:pos]
        
        # Calculate line and column
        line = text.count('\n') + 1
        last_newline = text.rfind('\n')
        col = pos - last_newline if last_newline != -1 else pos + 1
        
        self.status_bar.UpdatePosition(line, col)
    
    def OnNewTab(self, event):
        """Create a new empty tab"""
        self.CreateTab()
    
    def OnCloseTab(self, event):
        """Close current tab"""
        idx = self.notebook.GetSelection()
        if idx == -1:
            return
        
        self.CloseTabAtIndex(idx)
    
    def CloseTabAtIndex(self, idx):
        """Close tab at specific index"""
        if idx < 0 or idx >= self.notebook.GetPageCount():
            return
        
        # Check if modified
        if self.tabs_info[idx]['modified']:
            text_ctrl = self.notebook.GetPage(idx)
            label = self.notebook.GetPageText(idx).replace("● ", "")
            result = wx.MessageBox(
                f"Do you want to save changes to '{label}'?",
                "Unsaved Changes",
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
            )
            if result == wx.YES:
                self.SaveTabAtIndex(idx)
            elif result == wx.CANCEL:
                return
        
        # Remove tab
        self.notebook.DeletePage(idx)
        self.tabs_info.pop(idx)
        
        # Create new tab if all tabs are closed
        if self.notebook.GetPageCount() == 0:
            self.CreateTab()
    
    def OnNextTab(self, event):
        """Switch to next tab"""
        count = self.notebook.GetPageCount()
        if count > 1:
            current = self.notebook.GetSelection()
            next_tab = (current + 1) % count
            self.notebook.SetSelection(next_tab)
    
    def OnPrevTab(self, event):
        """Switch to previous tab"""
        count = self.notebook.GetPageCount()
        if count > 1:
            current = self.notebook.GetSelection()
            prev_tab = (current - 1) % count
            self.notebook.SetSelection(prev_tab)
    
    def OnTabContextMenu(self, event):
        """Show context menu for tabs"""
        menu = wx.Menu()
        
        item_new = menu.Append(wx.ID_ANY, "New Tab\tCtrl+N")
        item_close = menu.Append(wx.ID_ANY, "Close Tab\tCtrl+W")
        item_close_others = menu.Append(wx.ID_ANY, "Close Other Tabs")
        item_close_all = menu.Append(wx.ID_ANY, "Close All Tabs")
        
        self.Bind(wx.EVT_MENU, self.OnNewTab, item_new)
        self.Bind(wx.EVT_MENU, self.OnCloseTab, item_close)
        self.Bind(wx.EVT_MENU, self.OnCloseOtherTabs, item_close_others)
        self.Bind(wx.EVT_MENU, self.OnCloseAllTabs, item_close_all)
        
        self.PopupMenu(menu)
        menu.Destroy()
    
    def OnCloseOtherTabs(self, event):
        """Close all tabs except current"""
        current_idx = self.notebook.GetSelection()
        if current_idx == -1:
            return
        
        # Close tabs after current (in reverse to maintain indices)
        for i in range(self.notebook.GetPageCount() - 1, current_idx, -1):
            self.CloseTabAtIndex(i)
        
        # Close tabs before current (in reverse)
        for i in range(current_idx - 1, -1, -1):
            self.CloseTabAtIndex(i)
    
    def OnCloseAllTabs(self, event):
        """Close all tabs"""
        while self.notebook.GetPageCount() > 0:
            self.CloseTabAtIndex(0)

    # -----------------------------
    # AI FUNCTIONS
    # -----------------------------
    def RunAI(self, mode):
        content = self.GetSelectedOrAllText()
        if not content.strip():
            return

        prompt = ""
        # Quick Actions
        if mode == "write":
            prompt = f"Continue writing the following text. Only provide the continuation, do not repeat the original text:\n\n{content}"
        elif mode == "rewrite_prof":
            prompt = f"Rewrite the following text in a professional tone:\n\n{content}"
        elif mode == "rewrite_clear":
            prompt = f"Rewrite the following text to improve clarity and flow. Provide only the rewritten version:\n\n{content}"
        elif mode == "summarise":
            prompt = f"Summarize this text in 2-3 sentences:\n\n{content}"
        elif mode == "shorter":
            prompt = f"Condense the following text to be shorter while preserving all key information. Provide only the shortened version:\n\n{content}"
        elif mode == "longer":
            prompt = f"Expand the following text with additional relevant details and elaboration. Provide only the expanded version:\n\n{content}"
        
        # Smart Cleanup & Correction
        elif mode == "cleanup_grammar":
            prompt = f"Fix all grammar errors in the following text. Preserve the original meaning and style. Provide only the corrected version:\n\n{content}"
        elif mode == "cleanup_spelling":
            prompt = f"Fix all spelling mistakes in the following text. Preserve everything else exactly as is. Provide only the corrected version:\n\n{content}"
        elif mode == "cleanup_punctuation":
            prompt = f"Normalize and fix punctuation in the following text. Ensure proper use of commas, periods, quotes, etc. Provide only the corrected version:\n\n{content}"
        elif mode == "cleanup_casing":
            prompt = f"Fix capitalization issues in the following text. Ensure proper sentence case, title case where appropriate, and fix any ALL CAPS or inconsistent casing. Provide only the corrected version:\n\n{content}"
        elif mode == "cleanup_filler":
            prompt = f"Remove filler words (um, uh, like, you know, basically, actually, etc.) from the following text while maintaining natural flow. Provide only the cleaned version:\n\n{content}"
        elif mode == "cleanup_all":
            prompt = f"Clean and correct the following text by fixing: grammar errors, spelling mistakes, punctuation issues, capitalization problems, and removing filler words. Preserve the original meaning and tone. Provide only the cleaned version:\n\n{content}"
        elif mode == "cleanup_preserve_tone":
            prompt = f"Clean and correct the following text (fix grammar, spelling, punctuation) while carefully preserving the original tone, voice, and style. Provide only the cleaned version:\n\n{content}"
        
        # Structure from Messy Text
        elif mode == "structure_bullets":
            prompt = f"Convert the following messy notes into a clean, organized bullet point list. Extract key points and organize them logically:\n\n{content}"
        elif mode == "structure_numbered":
            prompt = f"Convert the following text into a numbered list. Organize items in a logical sequence:\n\n{content}"
        elif mode == "structure_actions":
            prompt = f"Extract action items from the following brain dump or notes. Format as a clear list of actionable tasks:\n\n{content}"
        elif mode == "structure_outline":
            prompt = f"Convert the following paragraph or text into a structured outline with main points and sub-points:\n\n{content}"
        elif mode == "structure_summary":
            prompt = f"Convert the following logs or verbose text into a clear, readable summary highlighting key information:\n\n{content}"
        elif mode == "structure_checklist":
            prompt = f"Convert the following free text into a checklist or to-do list format:\n\n{content}"
        
        # Tone Modes (existing + new)
        elif mode == "tone_formal":
            prompt = f"Rewrite the following text in a formal tone:\n\n{content}"
        elif mode == "tone_casual":
            prompt = f"Rewrite the following text in a casual, conversational tone:\n\n{content}"
        elif mode == "tone_inspirational":
            prompt = f"Rewrite the following text in an inspirational and motivational tone:\n\n{content}"
        elif mode == "tone_humor":
            prompt = f"Rewrite the following text with humor and wit:\n\n{content}"
        elif mode == "tone_corporate":
            prompt = f"Rewrite the following text in a corporate/professional business tone suitable for workplace communication:\n\n{content}"
        elif mode == "tone_technical":
            prompt = f"Rewrite the following text in a technical documentation style with precise, clear language:\n\n{content}"
        elif mode == "tone_legal":
            prompt = f"Rewrite the following text in legal-safe language, being careful with claims and using appropriate disclaimers:\n\n{content}"
        elif mode == "tone_resume":
            prompt = f"Rewrite the following text optimized for a resume or LinkedIn profile. Use action verbs and quantifiable achievements:\n\n{content}"
        elif mode == "tone_email":
            prompt = f"Rewrite the following text as a professional email with proper greeting, body, and closing:\n\n{content}"
        elif mode == "tone_creative":
            prompt = f"Rewrite the following text in a creative, lyrical style suitable for creative writing or lyrics:\n\n{content}"
        elif mode == "tone_commit":
            prompt = f"Rewrite the following text as a git commit message following best practices (imperative mood, concise, descriptive):\n\n{content}"
        elif mode == "tone_simplify":
            prompt = f"Simplify the following text. Use simple words, short sentences, and clear language that anyone can understand:\n\n{content}"
        elif mode == "tone_expand":
            prompt = f"Expand the following text with additional relevant details, examples, and elaboration:\n\n{content}"
        elif mode == "tone_condense":
            prompt = f"Condense the following text while keeping all key points and important information:\n\n{content}"
        
        # Format modes (existing)
        elif mode == "format_paragraph":
            prompt = f"Rewrite the following text as flowing paragraphs:\n\n{content}"
        elif mode == "format_list":
            prompt = f"Rewrite the following text as a bulleted or numbered list:\n\n{content}"
        elif mode == "format_business":
            prompt = f"Rewrite the following text in a business document format:\n\n{content}"
        elif mode == "format_academic":
            prompt = f"Rewrite the following text in an academic style with proper structure:\n\n{content}"
        elif mode == "format_marketing":
            prompt = f"Rewrite the following text as marketing copy with persuasive language:\n\n{content}"
        elif mode == "format_poetry":
            prompt = f"Rewrite the following text as poetry or verse:\n\n{content}"
        
        # Writing Pipelines
        elif mode == "pipeline_meeting_minutes":
            prompt = f"Convert the following meeting notes into formal Minutes of Meeting format with sections for attendees, agenda items, discussion points, decisions, and action items:\n\n{content}"
        elif mode == "pipeline_task_list":
            prompt = f"Convert the following brain dump into an organized task list with clear, actionable items:\n\n{content}"
        elif mode == "pipeline_corporate_email":
            prompt = f"Convert the following rough email draft into a polished corporate email with professional tone, proper structure, and clear call-to-action:\n\n{content}"
        elif mode == "pipeline_prd":
            prompt = f"Convert the following ideas into a Product Requirements Document (PRD) outline with sections for overview, objectives, features, user stories, and success criteria:\n\n{content}"
        elif mode == "pipeline_incident":
            prompt = f"Convert the following logs or notes into a formal Incident Report with sections for summary, timeline, impact, root cause, and resolution:\n\n{content}"
        elif mode == "pipeline_lyrics":
            prompt = f"Convert the following lyrics or text into structured verses with proper formatting, verse/chorus labels, and poetic structure:\n\n{content}"

        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
        self.status_bar.SetAIStatus("processing")
        
        def worker():
            result = ask_ollama(prompt)
            wx.CallAfter(self.OnAIResult, mode, result)

        threading.Thread(target=worker, daemon=True).start()

    def OnAIResult(self, mode, result):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.status_bar.SetAIStatus("ready")
        result = result.strip()
        theme = self.theme_manager.get_theme(self.current_theme)
        fg_color = theme['fg']
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        
        # Set default style BEFORE writing text to preserve undo/redo
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(fg_color))
        text_ctrl.SetDefaultStyle(attr)
        
        if mode == "write":
            # WriteText preserves undo/redo
            text_ctrl.WriteText("\n" + result)
        else:
            # ReplaceText now preserves undo/redo
            self.ReplaceText(result)

    # -----------------------------
    # MENUS
    # -----------------------------
    def OnFileMenu(self, event):
        menu = wx.Menu()
        item_new_tab = menu.Append(wx.ID_ANY, "New Tab\tCtrl+N")
        item_new = menu.Append(wx.ID_NEW, "New Window")
        item_open = menu.Append(wx.ID_OPEN, "Open\tCtrl+O")
        
        menu.AppendSeparator()
        
        # Recent Files submenu
        recent_menu = wx.Menu()
        recent_files = self.file_history.get_recent_files()
        
        if recent_files:
            for i, file_path in enumerate(recent_files):
                display_name = self._get_display_name(file_path)
                item = recent_menu.Append(wx.ID_ANY, f"{i+1}. {display_name}")
                self.Bind(wx.EVT_MENU, lambda e, path=file_path: self.OpenFile(path), item)
            
            recent_menu.AppendSeparator()
            clear_history = recent_menu.Append(wx.ID_ANY, "Clear Recent Files")
            self.Bind(wx.EVT_MENU, self.OnClearHistory, clear_history)
        else:
            empty_item = recent_menu.Append(wx.ID_ANY, "(No recent files)")
            empty_item.Enable(False)
        
        menu.AppendSubMenu(recent_menu, "Recent Files")
        
        menu.AppendSeparator()
        item_save = menu.Append(wx.ID_SAVE, "Save\tCtrl+S")
        item_save_as = menu.Append(wx.ID_SAVEAS, "Save As\tCtrl+Shift+S")
        item_close_tab = menu.Append(wx.ID_ANY, "Close Tab\tCtrl+W")
        menu.AppendSeparator()
        item_exit = menu.Append(wx.ID_EXIT, "Exit")

        self.Bind(wx.EVT_MENU, self.OnNewTab, item_new_tab)
        self.Bind(wx.EVT_MENU, self.OnNew, item_new)
        self.Bind(wx.EVT_MENU, self.OnOpen, item_open)
        self.Bind(wx.EVT_MENU, self.OnSave, item_save)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, item_save_as)
        self.Bind(wx.EVT_MENU, self.OnCloseTab, item_close_tab)
        self.Bind(wx.EVT_MENU, lambda e: self.Close(), item_exit)
        
        btn = event.GetEventObject()
        pos = btn.GetPosition()
        self.toolbar_panel.PopupMenu(menu, pos.x, pos.y + btn.GetSize().height)
        menu.Destroy()
    
    def _get_display_name(self, file_path):
        """Get a shortened display name for recent files"""
        try:
            parts = file_path.split(os.sep)
            if len(parts) > 2:
                return f"...{os.sep}{parts[-2]}{os.sep}{parts[-1]}"
            return os.path.basename(file_path)
        except:
            return os.path.basename(file_path)

    def OnEditMenu(self, event):
        menu = wx.Menu()
        text_ctrl = self.GetCurrentTextCtrl()
        
        item_cut = menu.Append(wx.ID_CUT, "Cut\tCtrl+X")
        item_copy = menu.Append(wx.ID_COPY, "Copy\tCtrl+C")
        item_paste = menu.Append(wx.ID_PASTE, "Paste\tCtrl+V")
        item_delete = menu.Append(wx.ID_DELETE, "Delete\tDel")
        menu.AppendSeparator()
        item_find = menu.Append(wx.ID_FIND, "Find\tCtrl+F")
        menu.AppendSeparator()
        item_undo = menu.Append(wx.ID_UNDO, "Undo\tCtrl+Z")
        item_redo = menu.Append(wx.ID_REDO, "Redo\tCtrl+Y")
        
        self.Bind(wx.EVT_MENU, lambda e: text_ctrl.Cut() if text_ctrl else None, item_cut)
        self.Bind(wx.EVT_MENU, lambda e: text_ctrl.Copy() if text_ctrl else None, item_copy)
        self.Bind(wx.EVT_MENU, lambda e: text_ctrl.Paste() if text_ctrl else None, item_paste)
        self.Bind(wx.EVT_MENU, self.OnDelete, item_delete)
        self.Bind(wx.EVT_MENU, self.OnFind, item_find)
        self.Bind(wx.EVT_MENU, lambda e: text_ctrl.Undo() if text_ctrl else None, item_undo)
        self.Bind(wx.EVT_MENU, lambda e: text_ctrl.Redo() if text_ctrl else None, item_redo)
        
        # Enable/disable based on state
        if text_ctrl:
            has_selection = text_ctrl.HasSelection()
            item_cut.Enable(has_selection)
            item_copy.Enable(has_selection)
            item_delete.Enable(has_selection)
            item_undo.Enable(text_ctrl.CanUndo())
            item_redo.Enable(text_ctrl.CanRedo())
        else:
            item_cut.Enable(False)
            item_copy.Enable(False)
            item_delete.Enable(False)
            item_undo.Enable(False)
            item_redo.Enable(False)
        
        btn = event.GetEventObject()
        pos = btn.GetPosition()
        self.toolbar_panel.PopupMenu(menu, pos.x, pos.y + btn.GetSize().height)
        menu.Destroy()

    def OnViewMenu(self, event):
        menu = wx.Menu()
        
        # Editor toggles
        item_line_numbers = menu.Append(wx.ID_ANY, "Toggle Line Numbers\tCtrl+L")
        item_word_wrap = menu.Append(wx.ID_ANY, "Toggle Word Wrap\tAlt+Z")
        
        menu.AppendSeparator()
        
        # View modes
        item_focus = menu.Append(wx.ID_ANY, "Focus Mode\\tCtrl+Shift+F")
        
        menu.AppendSeparator()
        
        # Zoom
        item_zoom_in = menu.Append(wx.ID_ANY, "Zoom In\\tCtrl++")
        item_zoom_out = menu.Append(wx.ID_ANY, "Zoom Out\\tCtrl+-")
        item_zoom_reset = menu.Append(wx.ID_ANY, "Reset Zoom\\tCtrl+0")
        
        menu.AppendSeparator()
        
        # Command Palette
        item_palette = menu.Append(wx.ID_ANY, "Command Palette\\tCtrl+Shift+P")
        
        self.Bind(wx.EVT_MENU, lambda e: self.ToggleLineNumbers(), item_line_numbers)
        self.Bind(wx.EVT_MENU, lambda e: self.ToggleWordWrap(), item_word_wrap)
        self.Bind(wx.EVT_MENU, lambda e: self.EnterFocusMode(), item_focus)
        self.Bind(wx.EVT_MENU, self.ZoomIn, item_zoom_in)
        self.Bind(wx.EVT_MENU, self.ZoomOut, item_zoom_out)
        self.Bind(wx.EVT_MENU, self.ZoomReset, item_zoom_reset)
        self.Bind(wx.EVT_MENU, self.ShowCommandPalette, item_palette)
        
        btn = event.GetEventObject()
        pos = btn.GetPosition()
        self.toolbar_panel.PopupMenu(menu, pos.x, pos.y + btn.GetSize().height)
        menu.Destroy()

    def OnAIMenu(self, event):
        menu = wx.Menu()
        
        # Quick Actions
        items = [
            ("Write", "write"),
            ("Rewrite", "rewrite_clear"),
            ("Summarise", "summarise"),
            ("Make shorter", "shorter"),
            ("Make longer", "longer")
        ]
        for label, mode in items:
            item = menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        menu.AppendSeparator()
        
        # Smart Cleanup submenu
        cleanup_menu = wx.Menu()
        cleanup_items = [
            ("Grammar correction", "cleanup_grammar"),
            ("Spelling correction", "cleanup_spelling"),
            ("Punctuation normalization", "cleanup_punctuation"),
            ("Casing fixes", "cleanup_casing"),
            ("Remove filler words", "cleanup_filler"),
        ]
        for label, mode in cleanup_items:
            item = cleanup_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        cleanup_menu.AppendSeparator()
        item_cleanup_all = cleanup_menu.Append(wx.ID_ANY, "Clean this text (All)")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("cleanup_all"), item_cleanup_all)
        item_cleanup_tone = cleanup_menu.Append(wx.ID_ANY, "Clean (Preserve tone)")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("cleanup_preserve_tone"), item_cleanup_tone)
        
        menu.AppendSubMenu(cleanup_menu, "Smart Cleanup")
        
        # Structure Text submenu
        structure_menu = wx.Menu()
        structure_items = [
            ("Messy notes → Bullets", "structure_bullets"),
            ("Bullets → Numbered list", "structure_numbered"),
            ("Brain dump → Action items", "structure_actions"),
            ("Paragraph → Outline", "structure_outline"),
            ("Logs → Summary", "structure_summary"),
            ("Free text → Checklist", "structure_checklist"),
        ]
        for label, mode in structure_items:
            item = structure_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        menu.AppendSubMenu(structure_menu, "Structure Text")
        
        # Change Tone submenu (expanded)
        tone_menu = wx.Menu()
        tone_items = [
            ("Corporate/Professional", "tone_corporate"),
            ("Casual", "tone_casual"),
            ("Technical", "tone_technical"),
            ("Legal-safe", "tone_legal"),
            ("Resume/LinkedIn", "tone_resume"),
            ("Email", "tone_email"),
            ("Creative/Lyrics", "tone_creative"),
            ("Commit message", "tone_commit"),
            ("Formal", "tone_formal"),
            ("Inspirational", "tone_inspirational"),
            ("Humor", "tone_humor"),
        ]
        for label, mode in tone_items:
            item = tone_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        tone_menu.AppendSeparator()
        tone_menu.Append(wx.ID_ANY, "─ Adjust Length ─").Enable(False)
        
        item_simplify = tone_menu.Append(wx.ID_ANY, "Simplify")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("tone_simplify"), item_simplify)
        item_expand = tone_menu.Append(wx.ID_ANY, "Expand")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("tone_expand"), item_expand)
        item_condense = tone_menu.Append(wx.ID_ANY, "Condense")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("tone_condense"), item_condense)
        
        menu.AppendSubMenu(tone_menu, "Change Tone")
        
        # Format submenu (existing)
        format_menu = wx.Menu()
        format_items = [
            ("Paragraph", "format_paragraph"),
            ("List", "format_list"),
            ("Business", "format_business"),
            ("Academic", "format_academic"),
            ("Marketing", "format_marketing"),
            ("Poetry", "format_poetry")
        ]
        for label, mode in format_items:
            item = format_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        menu.AppendSubMenu(format_menu, "Change Format")
        
        # Writing Pipelines submenu
        menu.AppendSeparator()
        pipeline_menu = wx.Menu()
        pipeline_items = [
            ("Meeting → Minutes", "pipeline_meeting_minutes"),
            ("Brain dump → Tasks", "pipeline_task_list"),
            ("Email → Corporate", "pipeline_corporate_email"),
            ("Ideas → PRD", "pipeline_prd"),
            ("Logs → Incident report", "pipeline_incident"),
            ("Lyrics → Structured", "pipeline_lyrics"),
        ]
        for label, mode in pipeline_items:
            item = pipeline_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        menu.AppendSubMenu(pipeline_menu, "Writing Pipelines")
        
        btn = event.GetEventObject()
        pos = btn.GetPosition()
        self.toolbar_panel.PopupMenu(menu, pos.x, pos.y + btn.GetSize().height)
        menu.Destroy()

    def OnContextMenu(self, event):
        menu = wx.Menu()
        text_ctrl = self.GetCurrentTextCtrl()
        
        item_cut = menu.Append(wx.ID_CUT, "Cut\tCtrl+X")
        item_copy = menu.Append(wx.ID_COPY, "Copy\tCtrl+C")
        item_paste = menu.Append(wx.ID_PASTE, "Paste\tCtrl+V")
        menu.AppendSeparator()
        item_select_all = menu.Append(wx.ID_SELECTALL, "Select All\tCtrl+A")
        
        self.Bind(wx.EVT_MENU, lambda e: text_ctrl.Cut() if text_ctrl else None, item_cut)
        self.Bind(wx.EVT_MENU, lambda e: text_ctrl.Copy() if text_ctrl else None, item_copy)
        self.Bind(wx.EVT_MENU, lambda e: text_ctrl.Paste() if text_ctrl else None, item_paste)
        self.Bind(wx.EVT_MENU, lambda e: text_ctrl.SelectAll() if text_ctrl else None, item_select_all)
        
        if text_ctrl:
            has_selection = text_ctrl.HasSelection()
            item_cut.Enable(has_selection)
            item_copy.Enable(has_selection)
        else:
            item_cut.Enable(False)
            item_copy.Enable(False)
        
        menu.AppendSeparator()
        
        # AI Features - Quick Actions
        items = [
            ("Write", "write"),
            ("Rewrite", "rewrite_clear"),
            ("Summarise", "summarise"),
            ("Make shorter", "shorter"),
            ("Make longer", "longer")
        ]
        for label, mode in items:
            item = menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        menu.AppendSeparator()
        
        # Smart Cleanup submenu
        cleanup_menu = wx.Menu()
        cleanup_items = [
            ("Grammar correction", "cleanup_grammar"),
            ("Spelling correction", "cleanup_spelling"),
            ("Punctuation normalization", "cleanup_punctuation"),
            ("Casing fixes", "cleanup_casing"),
            ("Remove filler words", "cleanup_filler"),
        ]
        for label, mode in cleanup_items:
            item = cleanup_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        cleanup_menu.AppendSeparator()
        item_cleanup_all = cleanup_menu.Append(wx.ID_ANY, "Clean this text (All)")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("cleanup_all"), item_cleanup_all)
        item_cleanup_tone = cleanup_menu.Append(wx.ID_ANY, "Clean (Preserve tone)")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("cleanup_preserve_tone"), item_cleanup_tone)
        
        menu.AppendSubMenu(cleanup_menu, "Smart Cleanup")
        
        # Structure Text submenu
        structure_menu = wx.Menu()
        structure_items = [
            ("Messy notes → Bullets", "structure_bullets"),
            ("Bullets → Numbered list", "structure_numbered"),
            ("Brain dump → Action items", "structure_actions"),
            ("Paragraph → Outline", "structure_outline"),
            ("Logs → Summary", "structure_summary"),
            ("Free text → Checklist", "structure_checklist"),
        ]
        for label, mode in structure_items:
            item = structure_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        menu.AppendSubMenu(structure_menu, "Structure Text")
        
        # Change Tone submenu
        tone_menu = wx.Menu()
        tone_items = [
            ("Corporate/Professional", "tone_corporate"),
            ("Casual", "tone_casual"),
            ("Technical", "tone_technical"),
            ("Legal-safe", "tone_legal"),
            ("Resume/LinkedIn", "tone_resume"),
            ("Email", "tone_email"),
            ("Creative/Lyrics", "tone_creative"),
            ("Commit message", "tone_commit"),
            ("Formal", "tone_formal"),
            ("Inspirational", "tone_inspirational"),
            ("Humor", "tone_humor"),
        ]
        for label, mode in tone_items:
            item = tone_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        tone_menu.AppendSeparator()
        tone_menu.Append(wx.ID_ANY, "─ Adjust Length ─").Enable(False)
        
        item_simplify = tone_menu.Append(wx.ID_ANY, "Simplify")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("tone_simplify"), item_simplify)
        item_expand = tone_menu.Append(wx.ID_ANY, "Expand")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("tone_expand"), item_expand)
        item_condense = tone_menu.Append(wx.ID_ANY, "Condense")
        self.Bind(wx.EVT_MENU, lambda e: self.RunAI("tone_condense"), item_condense)
        
        menu.AppendSubMenu(tone_menu, "Change Tone")
        
        # Format submenu
        format_menu = wx.Menu()
        format_items = [
            ("Paragraph", "format_paragraph"),
            ("List", "format_list"),
            ("Business", "format_business"),
            ("Academic", "format_academic"),
            ("Marketing", "format_marketing"),
            ("Poetry", "format_poetry")
        ]
        for label, mode in format_items:
            item = format_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        menu.AppendSubMenu(format_menu, "Change Format")
        
        # Writing Pipelines submenu
        pipeline_menu = wx.Menu()
        pipeline_items = [
            ("Meeting → Minutes", "pipeline_meeting_minutes"),
            ("Brain dump → Tasks", "pipeline_task_list"),
            ("Email → Corporate", "pipeline_corporate_email"),
            ("Ideas → PRD", "pipeline_prd"),
            ("Logs → Incident report", "pipeline_incident"),
            ("Lyrics → Structured", "pipeline_lyrics"),
        ]
        for label, mode in pipeline_items:
            item = pipeline_menu.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mode: self.RunAI(m), item)
        
        menu.AppendSubMenu(pipeline_menu, "Writing Pipelines")
        
        self.PopupMenu(menu)
        menu.Destroy()

    def OnSettings(self, event):
        dlg = SettingsDialog(self, self.current_theme)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnHelpMenu(self, event):
        """Show help menu"""
        menu = wx.Menu()
        
        item_about = menu.Append(wx.ID_ABOUT, "About Notepad PRO")
        item_shortcuts = menu.Append(wx.ID_ANY, "Keyboard Shortcuts")
        
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)
        self.Bind(wx.EVT_MENU, self.OnShowShortcuts, item_shortcuts)
        
        btn = event.GetEventObject()
        pos = btn.GetPosition()
        self.toolbar_panel.PopupMenu(menu, pos.x, pos.y + btn.GetSize().height)
        menu.Destroy()
    
    def OnAbout(self, event):
        """Show About dialog"""
        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnShowShortcuts(self, event):
        """Show keyboard shortcuts"""
        shortcuts = """Keyboard Shortcuts:

File Operations:
  Ctrl+N - New Tab
  Ctrl+O - Open File
  Ctrl+S - Save
  Ctrl+Shift+S - Save As
  Ctrl+W - Close Tab

Editing:
  Ctrl+Z - Undo
  Ctrl+Y - Redo
  Ctrl+X - Cut
  Ctrl+C - Copy
  Ctrl+V - Paste
  Ctrl+A - Select All
  Ctrl+F - Find
  Del - Delete

Tab Navigation:
  Ctrl+Tab - Next Tab
  Ctrl+Shift+Tab - Previous Tab

AI Features:
  Ctrl+Shift+R - AI Rewrite
"""
        wx.MessageBox(shortcuts, "Keyboard Shortcuts", wx.OK | wx.ICON_INFORMATION)

    # -----------------------------
    # EDIT MENU FUNCTIONS
    # -----------------------------
    def OnDelete(self, event):
        text_ctrl = self.GetCurrentTextCtrl()
        if text_ctrl and text_ctrl.HasSelection():
            sel_range = text_ctrl.GetSelectionRange()
            text_ctrl.Remove(sel_range.GetStart(), sel_range.GetEnd())

    def OnFind(self, event):
        dlg = FindDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    # -----------------------------
    # FILE OPERATIONS
    # -----------------------------
    def OnNew(self, event):
        """Create a new window"""
        import subprocess
        import sys
        subprocess.Popen([sys.executable, "main.py"])
    
    def SaveTabAtIndex(self, idx):
        """Save tab at specific index"""
        if idx < 0 or idx >= self.notebook.GetPageCount():
            return False
        
        info = self.tabs_info[idx]
        text_ctrl = self.notebook.GetPage(idx)
        
        if info['path']:
            try:
                with open(info['path'], "w", encoding="utf-8") as f:
                    f.write(text_ctrl.GetValue())
                text_ctrl.SetModified(False)
                info['modified'] = False
                self.UpdateTabLabel(idx)
                self.file_history.add_file(info['path'])
                return True
            except IOError as e:
                wx.LogError(f"Cannot save file '{info['path']}'.\n{str(e)}")
                return False
        else:
            return self.SaveAsTabAtIndex(idx)
    
    def SaveAsTabAtIndex(self, idx):
        """Save As for tab at specific index"""
        if idx < 0 or idx >= self.notebook.GetPageCount():
            return False
        
        text_ctrl = self.notebook.GetPage(idx)
        
        with wx.FileDialog(self, "Save file", wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return False
            
            path = fileDialog.GetPath()
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text_ctrl.GetValue())
                
                self.tabs_info[idx]['path'] = path
                self.tabs_info[idx]['modified'] = False
                text_ctrl.SetModified(False)
                self.file_history.add_file(path)
                self.UpdateTabLabel(idx)
                self.UpdateTitle()
                return True
            except IOError as e:
                wx.LogError(f"Cannot save file '{path}'.\n{str(e)}")
                return False
    
    def OpenFile(self, path):
        """Open a file in a new tab"""
        if not os.path.exists(path):
            wx.MessageBox(
                f"File not found:\n{path}\n\nIt may have been moved or deleted.",
                "File Not Found",
                wx.OK | wx.ICON_WARNING
            )
            self.file_history.remove_file(path)
            return
        
        # Check if file is already open in a tab
        for i, info in enumerate(self.tabs_info):
            if info['path'] == path:
                self.notebook.SetSelection(i)
                return
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.CreateTab(content=content, file_path=path)
            self.file_history.add_file(path)
            self.UpdateTitle()
        except IOError as e:
            wx.LogError(f"Cannot open file '{path}'.\n{str(e)}")

    def OnOpen(self, event):
        with wx.FileDialog(self, "Open file", wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            path = fileDialog.GetPath()
            self.OpenFile(path)

    def OnSave(self, event):
        idx = self.notebook.GetSelection()
        if idx != -1:
            self.SaveTabAtIndex(idx)

    def OnSaveAs(self, event):
        idx = self.notebook.GetSelection()
        if idx != -1:
            self.SaveAsTabAtIndex(idx)
    
    def OnClearHistory(self, event):
        """Clear the recent files history"""
        result = wx.MessageBox(
            "Are you sure you want to clear the recent files history?",
            "Clear History",
            wx.YES_NO | wx.ICON_QUESTION
        )
        if result == wx.YES:
            self.file_history.clear_history()
    
    def LoadSession(self):
        """Load previous tab session"""
        session = self.tab_manager.load_session()
        
        if session and session.get('tabs'):
            for tab_data in session['tabs']:
                path = tab_data.get('path')
                content = tab_data.get('content', '')
                
                if path and os.path.exists(path):
                    # Load file from disk (fresher content)
                    self.OpenFile(path)
                elif content:
                    # Restore unsaved content
                    self.CreateTab(content=content, file_path=None)
        
        # Create default tab if no tabs were loaded
        if self.notebook.GetPageCount() == 0:
            self.CreateTab()
    
    def SaveSession(self):
        """Save current tab session"""
        tabs = []
        for i in range(self.notebook.GetPageCount()):
            text_ctrl = self.notebook.GetPage(i)
            info = self.tabs_info[i]
            
            tab_data = {
                'path': info['path'],
                'content': text_ctrl.GetValue() if not info['path'] else ''
            }
            tabs.append(tab_data)
        
        self.tab_manager.save_session(tabs)
    
    def OnClose(self, event):
        """Handle window close"""
        # Check for unsaved changes
        modified_tabs = [i for i, info in enumerate(self.tabs_info) if info['modified']]
        
        if modified_tabs:
            result = wx.MessageBox(
                f"You have {len(modified_tabs)} unsaved tab(s). Do you want to save them?",
                "Unsaved Changes",
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
            )
            if result == wx.YES:
                for idx in modified_tabs:
                    if not self.SaveTabAtIndex(idx):
                        return  # Cancel close if save failed
            elif result == wx.CANCEL:
                return
        
        # Save session before closing
        self.SaveSession()
        event.Skip()
    
    # -----------------------------
    # FORMATTING
    # -----------------------------
    def OnFormatH1(self, event):
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        attr = wx.TextAttr()
        fg_color = "#f1f1f1" if self.current_theme == "dark" else "#23272e"
        attr.SetTextColour(wx.Colour(fg_color))
        attr.SetFontSize(16)
        attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
        text_ctrl.SetStyle(text_ctrl.GetSelectionRange(), attr)

    def OnFormatBullet(self, event):
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        if text_ctrl.HasSelection():
            txt = text_ctrl.GetStringSelection()
            lines = txt.splitlines()
            new_lines = ["• " + l if not l.strip().startswith("•") else l for l in lines]
            sel_range = text_ctrl.GetSelectionRange()
            text_ctrl.Replace(sel_range.GetStart(), sel_range.GetEnd(), "\n".join(new_lines))
        else:
            text_ctrl.WriteText("• ")

    def OnFormatBold(self, event):
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        attr = wx.TextAttr()
        fg_color = "#f1f1f1" if self.current_theme == "dark" else "#23272e"
        attr.SetTextColour(wx.Colour(fg_color))
        attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
        text_ctrl.SetStyle(text_ctrl.GetSelectionRange(), attr)

    def OnFormatItalic(self, event):
        text_ctrl = self.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        attr = wx.TextAttr()
        fg_color = "#f1f1f1" if self.current_theme == "dark" else "#23272e"
        attr.SetTextColour(wx.Colour(fg_color))
        attr.SetFontStyle(wx.FONTSTYLE_ITALIC)
        text_ctrl.SetStyle(text_ctrl.GetSelectionRange(), attr)

    # -----------------------------
    # THEMING
    # -----------------------------
    def ApplyThemeToTextCtrl(self, text_ctrl):
        """Apply current theme to a specific text control WITHOUT breaking undo/redo"""
        theme = self.theme_manager.get_theme(self.current_theme)
        
        txt_bg = theme['bg']
        fg = theme['fg']
        
        # Set widget colors
        text_ctrl.SetBackgroundColour(wx.Colour(txt_bg))
        text_ctrl.SetForegroundColour(wx.Colour(fg))
        
        # Set default style for NEW text
        default_attr = wx.TextAttr()
        default_attr.SetTextColour(wx.Colour(fg))
        default_attr.SetBackgroundColour(wx.Colour(txt_bg))
        default_attr.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI"))
        text_ctrl.SetDefaultStyle(default_attr)
        
        # Set basic style for the control
        basic_attr = rt.RichTextAttr()
        basic_attr.SetTextColour(wx.Colour(fg))
        basic_attr.SetBackgroundColour(wx.Colour(txt_bg))
        basic_attr.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI"))
        text_ctrl.SetBasicStyle(basic_attr)
        
        # CRITICAL: DO NOT CALL SetStyle ON EXISTING TEXT!
        # It breaks undo/redo. The background/foreground colors above are sufficient.
        # Existing text will update when the widget refreshes.
        
        # Refresh to apply colors
        text_ctrl.Refresh()

    def ApplyTheme(self, mode):
        """Apply theme to all UI elements"""
        self.current_theme = mode
        self.theme_manager.set_theme(mode)
        
        theme = self.theme_manager.get_theme(mode)
        
        bg = theme['bg']
        fg = theme['fg']
        tb_bg = theme['toolbar_bg']
        tb_fg = theme['toolbar_fg']
        txt_bg = theme['bg']
        nb_bg = theme['toolbar_bg']

        self.toolbar_panel.SetBackgroundColour(wx.Colour(tb_bg))
        
        buttons = [self.btn_file, self.btn_edit, self.btn_view, 
                   self.btn_h1, self.btn_bullet, self.btn_bold, self.btn_italic,
                   self.btn_ai, self.btn_settings, self.btn_help]
        
        for btn in buttons:
            btn.SetBackgroundColour(wx.Colour(tb_bg))
            btn.SetForegroundColour(wx.Colour(tb_fg))

        self.main_panel.SetBackgroundColour(wx.Colour(bg))
        self.notebook.SetBackgroundColour(wx.Colour(nb_bg))
        self.notebook.SetForegroundColour(wx.Colour(tb_fg))
        
        # Apply theme to status bar
        self.status_bar.ApplyTheme(mode)
        
        # Apply theme to all tabs
        for i in range(self.notebook.GetPageCount()):
            text_ctrl = self.notebook.GetPage(i)
            self.ApplyThemeToTextCtrl(text_ctrl)
        
        # Force complete refresh
        self.main_panel.Refresh()
        self.notebook.Refresh()
        self.toolbar_panel.Refresh()
        self.Refresh()

    # -----------------------------
    # EDITOR FEATURES
    # -----------------------------
    def ToggleLineNumbers(self):
        """Toggle line numbers visibility"""
        self.show_line_numbers = not self.show_line_numbers
        # Note: RichTextCtrl doesn't support line numbers natively
        # This would require custom drawing or switching to StyledTextCtrl
        status = "enabled" if self.show_line_numbers else "disabled"
        wx.MessageBox(f"Line numbers {status}.\n\nNote: This feature requires a code editor control.\nCurrently using RichTextCtrl for rich formatting.", 
                      "Line Numbers", wx.OK | wx.ICON_INFORMATION)
    
    def ToggleWordWrap(self):
        """Toggle word wrap"""
        self.word_wrap_enabled = not self.word_wrap_enabled
        # Apply to current tab
        text_ctrl = self.GetCurrentTextCtrl()
        if text_ctrl:
            # RichTextCtrl doesn't have direct word wrap toggle
            # This is a placeholder - would need implementation
            status = "enabled" if self.word_wrap_enabled else "disabled"
            wx.MessageBox(f"Word wrap {status}.", "Word Wrap", wx.OK | wx.ICON_INFORMATION)
    
    def EnterFocusMode(self):
        """Enter distraction-free focus mode"""
        text_ctrl = self.GetCurrentTextCtrl()
        if text_ctrl:
            content = text_ctrl.GetValue()
            focus = FocusMode(self, content, self.current_theme)
    
    def ShowCommandPalette(self, event=None):
        """Show command palette"""
        dlg = CommandPalette(self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def ToggleLineNumbers(self):
        """Toggle line numbers (for future syntax editor)"""
        wx.MessageBox("Line numbers toggle - Feature coming soon!", "Info", wx.OK | wx.ICON_INFORMATION)
    
    def ZoomIn(self, event=None):
        """Zoom in text"""
        text_ctrl = self.GetCurrentTextCtrl()
        if text_ctrl:
            font = text_ctrl.GetFont()
            size = font.GetPointSize()
            if size < 72:
                font.SetPointSize(size + 1)
                text_ctrl.SetFont(font)
    
    def ZoomOut(self, event=None):
        """Zoom out text"""
        text_ctrl = self.GetCurrentTextCtrl()
        if text_ctrl:
            font = text_ctrl.GetFont()
            size = font.GetPointSize()
            if size > 6:
                font.SetPointSize(size - 1)
                text_ctrl.SetFont(font)
    
    def ZoomReset(self, event=None):
        """Reset zoom to default"""
        text_ctrl = self.GetCurrentTextCtrl()
        if text_ctrl:
            font = text_ctrl.GetFont()
            font.SetPointSize(11)
            text_ctrl.SetFont(font)


    # -----------------------------
    # FIND DIALOG
    # -----------------------------
class FindDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Find", size=(400, 150))
        self.parent_frame = parent
        self.search_pos = 0
        self.CenterOnParent()

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(panel, label="Find:")
        hbox1.Add(lbl, flag=wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=8)
        self.search_input = wx.TextCtrl(panel, size=(250, -1), style=wx.TE_PROCESS_ENTER)
        hbox1.Add(self.search_input, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.find_next_btn = wx.Button(panel, label="Find Next")
        self.find_prev_btn = wx.Button(panel, label="Find Previous")
        close_btn = wx.Button(panel, label="Close")
        
        self.find_next_btn.Bind(wx.EVT_BUTTON, self.OnFindNext)
        self.find_prev_btn.Bind(wx.EVT_BUTTON, self.OnFindPrevious)
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        hbox2.Add(self.find_next_btn, flag=wx.RIGHT, border=5)
        hbox2.Add(self.find_prev_btn, flag=wx.RIGHT, border=5)
        hbox2.Add(close_btn)
        vbox.Add(hbox2, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)

        panel.SetSizer(vbox)
        self.search_input.Bind(wx.EVT_TEXT_ENTER, self.OnFindNext)

    def OnFindNext(self, event):
        text_ctrl = self.parent_frame.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        
        text = text_ctrl.GetValue()
        search_term = self.search_input.GetValue()
        
        if not search_term:
            return
        
        pos = text.lower().find(search_term.lower(), self.search_pos)
        
        if pos != -1:
            text_ctrl.SetSelection(pos, pos + len(search_term))
            text_ctrl.SetFocus()
            self.search_pos = pos + 1
        else:
            self.search_pos = 0
            pos = text.lower().find(search_term.lower(), 0)
            if pos != -1:
                text_ctrl.SetSelection(pos, pos + len(search_term))
                text_ctrl.SetFocus()
                self.search_pos = pos + 1
            else:
                wx.MessageBox("Text not found", "Find", wx.OK | wx.ICON_INFORMATION)

    def OnFindPrevious(self, event):
        text_ctrl = self.parent_frame.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        
        text = text_ctrl.GetValue()
        search_term = self.search_input.GetValue()
        
        if not search_term:
            return
        
        if self.search_pos > 0:
            search_start = max(0, self.search_pos - 2)
        else:
            search_start = len(text)
        
        pos = text.lower().rfind(search_term.lower(), 0, search_start)
        
        if pos != -1:
            text_ctrl.SetSelection(pos, pos + len(search_term))
            text_ctrl.SetFocus()
            self.search_pos = pos
        else:
            wx.MessageBox("Text not found", "Find", wx.OK | wx.ICON_INFORMATION)