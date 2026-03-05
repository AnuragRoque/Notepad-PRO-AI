import wx
import re

class FindReplaceDialog(wx.Dialog):
    """Advanced find and replace dialog with regex support"""
    
    def __init__(self, parent):
        super().__init__(parent, title="Find and Replace", size=(500, 350))
        self.parent_frame = parent
        self.CenterOnParent()
        
        # Search history
        self.find_history = []
        self.replace_history = []
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Find section
        find_box = wx.StaticBox(panel, label="Find")
        find_sizer = wx.StaticBoxSizer(find_box, wx.VERTICAL)
        
        self.find_ctrl = wx.ComboBox(panel, style=wx.CB_DROPDOWN)
        find_sizer.Add(self.find_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        
        vbox.Add(find_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Replace section
        replace_box = wx.StaticBox(panel, label="Replace with")
        replace_sizer = wx.StaticBoxSizer(replace_box, wx.VERTICAL)
        
        self.replace_ctrl = wx.ComboBox(panel, style=wx.CB_DROPDOWN)
        replace_sizer.Add(self.replace_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        
        vbox.Add(replace_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Options
        options_box = wx.StaticBox(panel, label="Options")
        options_sizer = wx.StaticBoxSizer(options_box, wx.VERTICAL)
        
        self.case_sensitive = wx.CheckBox(panel, label="Case sensitive")
        self.whole_word = wx.CheckBox(panel, label="Match whole word only")
        self.use_regex = wx.CheckBox(panel, label="Use regular expressions")
        self.wrap_around = wx.CheckBox(panel, label="Wrap around")
        self.wrap_around.SetValue(True)
        
        options_sizer.Add(self.case_sensitive, 0, wx.ALL, 3)
        options_sizer.Add(self.whole_word, 0, wx.ALL, 3)
        options_sizer.Add(self.use_regex, 0, wx.ALL, 3)
        options_sizer.Add(self.wrap_around, 0, wx.ALL, 3)
        
        vbox.Add(options_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.find_next_btn = wx.Button(panel, label="Find Next")
        self.find_prev_btn = wx.Button(panel, label="Find Previous")
        self.replace_btn = wx.Button(panel, label="Replace")
        self.replace_all_btn = wx.Button(panel, label="Replace All")
        self.close_btn = wx.Button(panel, label="Close")
        
        btn_sizer.Add(self.find_next_btn, 0, wx.ALL, 3)
        btn_sizer.Add(self.find_prev_btn, 0, wx.ALL, 3)
        btn_sizer.Add(self.replace_btn, 0, wx.ALL, 3)
        btn_sizer.Add(self.replace_all_btn, 0, wx.ALL, 3)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(self.close_btn, 0, wx.ALL, 3)
        
        vbox.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Result label
        self.result_label = wx.StaticText(panel, label="")
        vbox.Add(self.result_label, 0, wx.ALL, 5)
        
        panel.SetSizer(vbox)
        
        # Bind events
        self.find_next_btn.Bind(wx.EVT_BUTTON, self.OnFindNext)
        self.find_prev_btn.Bind(wx.EVT_BUTTON, self.OnFindPrevious)
        self.replace_btn.Bind(wx.EVT_BUTTON, self.OnReplace)
        self.replace_all_btn.Bind(wx.EVT_BUTTON, self.OnReplaceAll)
        self.close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        # Bind Enter key to find next
        self.find_ctrl.Bind(wx.EVT_TEXT_ENTER, self.OnFindNext)
    
    def GetSearchFlags(self):
        """Get search flags based on options"""
        flags = 0
        if not self.case_sensitive.GetValue():
            flags |= wx.FR_DOWN
        return flags
    
    def OnFindNext(self, event):
        """Find next occurrence"""
        find_text = self.find_ctrl.GetValue()
        if not find_text:
            self.result_label.SetLabel("Please enter text to find")
            return
        
        text_ctrl = self.parent_frame.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        
        # Get current text and position
        content = text_ctrl.GetValue()
        current_pos = text_ctrl.GetInsertionPoint()
        
        # Perform search
        pos = self._find_in_text(content, find_text, current_pos, forward=True)
        
        if pos != -1:
            # Select found text
            text_ctrl.SetSelection(pos, pos + len(find_text))
            text_ctrl.SetInsertionPoint(pos + len(find_text))
            text_ctrl.ShowPosition(pos)
            self.result_label.SetLabel(f"Found at position {pos}")
        else:
            if self.wrap_around.GetValue():
                # Try from beginning
                pos = self._find_in_text(content, find_text, 0, forward=True)
                if pos != -1 and pos < current_pos:
                    text_ctrl.SetSelection(pos, pos + len(find_text))
                    text_ctrl.SetInsertionPoint(pos + len(find_text))
                    text_ctrl.ShowPosition(pos)
                    self.result_label.SetLabel(f"Found at position {pos} (wrapped)")
                else:
                    self.result_label.SetLabel("Not found")
            else:
                self.result_label.SetLabel("Not found")
    
    def OnFindPrevious(self, event):
        """Find previous occurrence"""
        find_text = self.find_ctrl.GetValue()
        if not find_text:
            self.result_label.SetLabel("Please enter text to find")
            return
        
        text_ctrl = self.parent_frame.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        
        content = text_ctrl.GetValue()
        current_pos = text_ctrl.GetInsertionPoint()
        
        # Search backwards
        pos = self._find_in_text(content, find_text, current_pos - 1, forward=False)
        
        if pos != -1:
            text_ctrl.SetSelection(pos, pos + len(find_text))
            text_ctrl.SetInsertionPoint(pos)
            text_ctrl.ShowPosition(pos)
            self.result_label.SetLabel(f"Found at position {pos}")
        else:
            self.result_label.SetLabel("Not found")
    
    def OnReplace(self, event):
        """Replace current selection"""
        text_ctrl = self.parent_frame.GetCurrentTextCtrl()
        if not text_ctrl or not text_ctrl.HasSelection():
            self.result_label.SetLabel("No text selected")
            return
        
        replace_text = self.replace_ctrl.GetValue()
        
        # Replace selection
        sel_start, sel_end = text_ctrl.GetSelection()
        text_ctrl.Replace(sel_start, sel_end, replace_text)
        
        self.result_label.SetLabel("Replaced 1 occurrence")
        
        # Find next
        self.OnFindNext(None)
    
    def OnReplaceAll(self, event):
        """Replace all occurrences"""
        find_text = self.find_ctrl.GetValue()
        replace_text = self.replace_ctrl.GetValue()
        
        if not find_text:
            self.result_label.SetLabel("Please enter text to find")
            return
        
        text_ctrl = self.parent_frame.GetCurrentTextCtrl()
        if not text_ctrl:
            return
        
        content = text_ctrl.GetValue()
        count = 0
        
        if self.use_regex.GetValue():
            # Regex replace
            try:
                flags = 0 if self.case_sensitive.GetValue() else re.IGNORECASE
                new_content, count = re.subn(find_text, replace_text, content, flags=flags)
                text_ctrl.SetValue(new_content)
            except re.error as e:
                self.result_label.SetLabel(f"Regex error: {str(e)}")
                return
        else:
            # Simple replace
            if self.case_sensitive.GetValue():
                new_content = content.replace(find_text, replace_text)
                count = content.count(find_text)
            else:
                # Case-insensitive replace
                import re
                pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                new_content = pattern.sub(replace_text, content)
                count = len(pattern.findall(content))
            
            text_ctrl.SetValue(new_content)
        
        self.result_label.SetLabel(f"Replaced {count} occurrence(s)")
    
    def _find_in_text(self, content, find_text, start_pos, forward=True):
        """Find text in content"""
        if self.use_regex.GetValue():
            # Regex search
            try:
                flags = 0 if self.case_sensitive.GetValue() else re.IGNORECASE
                pattern = re.compile(find_text, flags)
                
                if forward:
                    match = pattern.search(content, start_pos)
                    return match.start() if match else -1
                else:
                    # Search backwards
                    matches = list(pattern.finditer(content[:start_pos]))
                    return matches[-1].start() if matches else -1
            except re.error:
                return -1
        else:
            # Simple search
            if self.whole_word.GetValue():
                # Word boundary search
                import re
                pattern = r'\b' + re.escape(find_text) + r'\b'
                flags = 0 if self.case_sensitive.GetValue() else re.IGNORECASE
                compiled = re.compile(pattern, flags)
                
                if forward:
                    match = compiled.search(content, start_pos)
                    return match.start() if match else -1
                else:
                    matches = list(compiled.finditer(content[:start_pos]))
                    return matches[-1].start() if matches else -1
            else:
                if forward:
                    if self.case_sensitive.GetValue():
                        return content.find(find_text, start_pos)
                    else:
                        return content.lower().find(find_text.lower(), start_pos)
                else:
                    if self.case_sensitive.GetValue():
                        return content.rfind(find_text, 0, start_pos)
                    else:
                        return content.lower().rfind(find_text.lower(), 0, start_pos)


class FindDialog(wx.Dialog):
    """Simple find dialog (legacy compatibility)"""
    
    def __init__(self, parent):
        # Use the advanced dialog
        self.advanced = FindReplaceDialog(parent)
    
    def ShowModal(self):
        return self.advanced.ShowModal()
    
    def Destroy(self):
        return self.advanced.Destroy()
