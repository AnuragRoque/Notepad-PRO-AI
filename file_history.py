import json
import os
from pathlib import Path

class FileHistory:
    def __init__(self, max_files=10):
        self.max_files = max_files
        self.history_file = self._get_history_path()
        self.recent_files = self._load_history()
    
    def _get_history_path(self):
        """Get the path to store history file in user's AppData/Local"""
        if os.name == 'nt':  # Windows
            # Use USERPROFILE instead of LOCALAPPDATA to avoid sandboxing issues
            user_profile = os.path.expanduser('~')
            app_dir = os.path.join(user_profile, 'AppData', 'Local', 'NotepadAI')
        else:  # Linux/Mac
            app_data = os.path.expanduser('~/.local/share')
            app_dir = os.path.join(app_data, 'notepad-ai')
        
        # Create directory if it doesn't exist
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, 'recent_files.json')
    
    def _load_history(self):
        """Load file history from JSON"""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Filter out files that no longer exist
                return [path for path in data.get('recent_files', []) if os.path.exists(path)]
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save_history(self):
        """Save file history to JSON"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({'recent_files': self.recent_files}, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Silently fail if we can't save
    
    def add_file(self, file_path):
        """Add a file to the history"""
        if not file_path or not os.path.exists(file_path):
            return
        
        # Normalize the path
        file_path = os.path.abspath(file_path)
        
        # Remove if already exists (to move it to top)
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        # Add to the beginning
        self.recent_files.insert(0, file_path)
        
        # Keep only max_files
        self.recent_files = self.recent_files[:self.max_files]
        
        # Save to disk
        self._save_history()
    
    def get_recent_files(self):
        """Get list of recent files (only those that still exist)"""
        # Filter out non-existent files
        self.recent_files = [path for path in self.recent_files if os.path.exists(path)]
        self._save_history()
        return self.recent_files
    
    def clear_history(self):
        """Clear all history"""
        self.recent_files = []
        self._save_history()
    
    def remove_file(self, file_path):
        """Remove a specific file from history"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
            self._save_history()
