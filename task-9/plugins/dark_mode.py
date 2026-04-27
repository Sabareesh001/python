"""
Dark Mode Theme Plugin

Provides a dark theme for the site.
"""

from plugin_base import PluginBase


class DarkModePlugin(PluginBase):
    """Provides a dark theme for the application."""
    
    name = "dark-mode-theme"
    version = "1.3.2"
    description = "Dark theme for site generator"
    author = "Third-party"
    required_plugins = []
    
    DARK_THEME_CONFIG = {
        "background": "#1a1a1a",
        "foreground": "#ffffff",
        "accent": "#00bfff",
        "name": "dark-mode",
    }
    
    def activate(self, app):
        """Register the dark theme."""
        app.register_theme("dark-mode", self.DARK_THEME_CONFIG)
        app.register_command("theme-info", self.theme_info)
    
    def deactivate(self, app):
        """Clean up theme resources."""
        pass
    
    def theme_info(self):
        """Get theme information."""
        return self.DARK_THEME_CONFIG
