import wx
import json
import os

class ThemeManager:
    """Advanced theme management with multiple professional themes"""
    
    THEMES = {
        "light": {
            "name": "Light",
            "bg": "#ffffff",
            "fg": "#23272e",
            "toolbar_bg": "#f5f5f5",
            "toolbar_fg": "#23272e",
            "selection_bg": "#0078d4",
            "selection_fg": "#ffffff",
            "line_number_bg": "#f0f0f0",
            "line_number_fg": "#858585",
            "current_line": "#f0f0f0",
            "status_bar_bg": "#f0f0f0",
            "status_bar_fg": "#333333",
        },
        "dark": {
            "name": "Dark",
            "bg": "#1e1e1e",
            "fg": "#d4d4d4",
            "toolbar_bg": "#2d2d30",
            "toolbar_fg": "#cccccc",
            "selection_bg": "#264f78",
            "selection_fg": "#ffffff",
            "line_number_bg": "#1e1e1e",
            "line_number_fg": "#858585",
            "current_line": "#2a2a2a",
            "status_bar_bg": "#1e1e1e",
            "status_bar_fg": "#cccccc",
        },
        "monokai": {
            "name": "Monokai",
            "bg": "#272822",
            "fg": "#f8f8f2",
            "toolbar_bg": "#3e3d32",
            "toolbar_fg": "#f8f8f2",
            "selection_bg": "#49483e",
            "selection_fg": "#f8f8f2",
            "line_number_bg": "#272822",
            "line_number_fg": "#90908a",
            "current_line": "#3e3d32",
            "status_bar_bg": "#1e1e1e",
            "status_bar_fg": "#f8f8f2",
        },
        "solarized_dark": {
            "name": "Solarized Dark",
            "bg": "#002b36",
            "fg": "#839496",
            "toolbar_bg": "#073642",
            "toolbar_fg": "#93a1a1",
            "selection_bg": "#073642",
            "selection_fg": "#eee8d5",
            "line_number_bg": "#002b36",
            "line_number_fg": "#586e75",
            "current_line": "#073642",
            "status_bar_bg": "#073642",
            "status_bar_fg": "#93a1a1",
        },
        "nord": {
            "name": "Nord",
            "bg": "#2e3440",
            "fg": "#d8dee9",
            "toolbar_bg": "#3b4252",
            "toolbar_fg": "#eceff4",
            "selection_bg": "#434c5e",
            "selection_fg": "#eceff4",
            "line_number_bg": "#2e3440",
            "line_number_fg": "#4c566a",
            "current_line": "#3b4252",
            "status_bar_bg": "#3b4252",
            "status_bar_fg": "#d8dee9",
        },
        "dracula": {
            "name": "Dracula",
            "bg": "#282a36",
            "fg": "#f8f8f2",
            "toolbar_bg": "#44475a",
            "toolbar_fg": "#f8f8f2",
            "selection_bg": "#44475a",
            "selection_fg": "#f8f8f2",
            "line_number_bg": "#282a36",
            "line_number_fg": "#6272a4",
            "current_line": "#44475a",
            "status_bar_bg": "#21222c",
            "status_bar_fg": "#f8f8f2",
        },
    }
    
    def __init__(self):
        self.current_theme = "light"
        self.config_path = self._get_config_path()
        self.load_theme_preference()
    
    def _get_config_path(self):
        """Get path to theme config file"""
        user_profile = os.path.expanduser('~')
        app_dir = os.path.join(user_profile, 'AppData', 'Local', 'NotepadAI')
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, 'theme_config.json')
    
    def load_theme_preference(self):
        """Load saved theme preference"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    theme = data.get('theme', 'light')
                    if theme in self.THEMES:
                        self.current_theme = theme
            except:
                pass
    
    def save_theme_preference(self, theme):
        """Save theme preference"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump({'theme': theme}, f)
        except:
            pass
    
    def get_theme(self, theme_name=None):
        """Get theme colors"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.THEMES.get(theme_name, self.THEMES["light"])
    
    def set_theme(self, theme_name):
        """Set current theme"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.save_theme_preference(theme_name)
            return True
        return False
    
    def get_all_themes(self):
        """Get list of all available themes"""
        return [(key, value["name"]) for key, value in self.THEMES.items()]
    
    def is_dark_theme(self, theme_name=None):
        """Check if theme is dark"""
        if theme_name is None:
            theme_name = self.current_theme
        dark_themes = ["dark", "monokai", "solarized_dark", "nord", "dracula"]
        return theme_name in dark_themes
