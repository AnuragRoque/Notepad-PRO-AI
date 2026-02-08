import json
import os

class TabManager:
    def __init__(self):
        self.session_file = self._get_session_path()
    
    def _get_session_path(self):
        """Get the path to store tab session file"""
        user_profile = os.path.expanduser('~')
        app_dir = os.path.join(user_profile, 'AppData', 'Local', 'NotepadAI')
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, 'tab_session.json')
    
    def save_session(self, tabs):
        """Save current tab session
        tabs: list of dicts with 'path' (or None for untitled) and 'content'
        """
        try:
            session_data = {
                'tabs': tabs,
                'active_tab': 0
            }
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def load_session(self):
        """Load previous tab session"""
        if not os.path.exists(self.session_file):
            return None
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def clear_session(self):
        """Clear saved session"""
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
            except OSError:
                pass
