"""
Plugin Base Class

Defines the interface that all plugins must implement.
"""

from abc import ABC, abstractmethod


class PluginBase(ABC):
    """
    Abstract base class for all plugins.
    
    Plugins must inherit from this class and implement the required methods.
    """
    
    # Plugin metadata (override in subclasses)
    name: str = "unknown"
    version: str = "0.0.0"
    description: str = "No description"
    author: str = "Unknown"
    required_plugins: list = []  # List of plugin names this plugin depends on
    
    @abstractmethod
    def activate(self, app):
        """
        Called when the plugin is activated.
        
        Use this hook to:
        - Register commands with the app
        - Register themes
        - Register output formatters
        - Initialize resources
        
        Args:
            app: The application/plugin manager instance
        """
        pass
    
    @abstractmethod
    def deactivate(self, app):
        """
        Called when the plugin is deactivated or unloaded.
        
        Use this hook to:
        - Unregister commands
        - Clean up resources
        - Close connections
        
        Args:
            app: The application/plugin manager instance
        """
        pass
    
    def get_info(self) -> dict:
        """Get plugin metadata as a dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "required_plugins": self.required_plugins,
        }
