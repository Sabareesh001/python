"""
Example Usage of Plugin Architecture

Demonstrates discovering, loading, and managing plugins.
"""

from core import SiteGenerator


def main():
    """Run the site generator with plugins."""
    print("=== Site Generator with Plugin Architecture ===\n")
    
    # Initialize application
    app = SiteGenerator()
    app.initialize()
    
    print()
    print("=" * 60)
    print()
    
    # Build site with dark theme
    app.build(theme="dark-mode")
    
    print()
    print("=" * 60)
    print()
    
    # List active plugins
    active = app.plugin_manager.list_active_plugins()
    print(f"[INFO] Active plugins: {', '.join(active)}\n")
    
    # Get plugin info
    for plugin_name in active:
        info = app.plugin_manager.get_plugin_info(plugin_name)
        print(f"  {plugin_name:20} v{info['version']:10} - {info['description']}")


if __name__ == "__main__":
    main()
