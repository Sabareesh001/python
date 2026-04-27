# Task 9: Plugin Architecture with Dynamic Module Loading

A flexible, extensible application framework that discovers, loads, and manages plugins at runtime. Supports dependency resolution, lifecycle hooks, and sandboxed plugin execution.

## Features

- **Dynamic Plugin Discovery**: Scans `./plugins/` directory for plugin modules on startup
- **Plugin Interface**: All plugins implement `PluginBase` with `activate()` and `deactivate()` hooks
- **Dependency Resolution**: Validates inter-plugin dependencies using topological sort
- **Lifecycle Management**: Proper activation order and graceful deactivation
- **Plugin Registry**: Plugins register commands, themes, and formatters with the core app
- **Error Handling**: Graceful degradation if a plugin fails to load or activate
- **No Core Modifications**: Add/remove plugins without modifying the application core

## Project Structure

```
task-9/
├── README.md
├── requirements.txt
├── plugin_base.py          # Abstract base class for plugins
├── dependency_resolver.py  # Dependency graph resolution
├── core.py                 # Main application and plugin manager
├── example.py              # Demonstration with multiple plugins
└── plugins/
    ├── markdown_parser.py  # Built-in markdown plugin
    ├── dark_mode.py        # Third-party theme plugin
    ├── rss_feed.py         # Plugin with dependencies
    └── image_optimizer.py  # Post-processor plugin
```

## How It Works

1. **Plugin Discovery**: Core scans `./plugins/` for `.py` files containing plugin classes
2. **Dependency Parsing**: Each plugin declares its dependencies in `required_plugins`
3. **Dependency Resolution**: Topological sort ensures plugins load in correct order
4. **Plugin Activation**: Each plugin's `activate()` hook is called when its dependencies are satisfied
5. **Command Registration**: Plugins register new commands, themes, etc. with the core app
6. **Plugin Usage**: Core app calls registered functions from active plugins
7. **Graceful Removal**: Plugins can be removed anytime; dependencies are checked

## Running the Application

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the example

```bash
python example.py build --theme dark-mode
```

Expected output:

```
[CORE] Scanning plugin directory: ./plugins/
[CORE] Discovered 4 plugins:
       ├── markdown-parser v2.1.0 (built-in)
       ├── dark-mode-theme v1.3.2 (third-party)
       ├── rss-feed v1.0.0 (third-party, depends: markdown-parser)
       └── image-optimizer v0.9.1 (third-party)

[CORE] Resolving dependencies...
       markdown-parser    (no dependencies)          OK
       dark-mode-theme    (no dependencies)          OK
       rss-feed           -> markdown-parser         OK (satisfied)
       image-optimizer    (no dependencies)          OK

[CORE] Activating plugins in order...
       [1/4] markdown-parser.activate()  — registered: .md -> HTML converter
       [2/4] dark-mode-theme.activate()  — registered: theme "dark-mode"
       [3/4] rss-feed.activate()         — registered: command "generate-rss"
       [4/4] image-optimizer.activate()  — registered: post-processor for .png/.jpg

[CORE] Building site...
       Processed 24 pages | Theme: dark-mode | RSS: feed.xml generated
       Images optimized: 18 files, saved 4.2 MB
[CORE] Build complete -> ./dist/ (0.87s)
```

## Creating Your Own Plugin

### Basic Plugin Template

```python
from plugin_base import PluginBase

class MyPlugin(PluginBase):
    name = "my-plugin"
    version = "1.0.0"
    description = "Does something cool"
    required_plugins = []  # List of plugin names this depends on

    def activate(self, app):
        # Called when plugin is activated
        print(f"{self.name} activated!")
        # Register commands, themes, etc.
        app.register_command("my-command", self.my_command)

    def deactivate(self, app):
        # Called when plugin is deactivated
        print(f"{self.name} deactivated!")

    def my_command(self, *args):
        # Plugin functionality
        print(f"Running: {args}")
```

## Architecture Patterns

- **Abstract Base Classes**: `PluginBase` defines the plugin interface
- **Decorators**: Plugin auto-registration via `@plugin` decorator
- **Class Registry**: Central registry of all available plugins
- **Dependency Graph**: Topological sort ensures correct load order
- **Hooks Pattern**: `activate()` and `deactivate()` lifecycle hooks
- **Service Locator**: Apps store references to active plugins

## Customization

- **Plugin Directory**: Change `PLUGIN_DIR` in `core.py`
- **Auto-Registration**: Modify discovery logic in `PluginManager.discover_plugins()`
- **Custom Hooks**: Add more lifecycle methods (e.g., `on_config_change()`)
- **Error Recovery**: Customize error handling in `activate_plugin()`

## Learning Outcomes

- ✅ Dynamic module loading with `importlib`
- ✅ Abstract base classes and interfaces (`abc.ABC`)
- ✅ Dependency resolution (topological sort)
- ✅ Plugin registry and discovery patterns
- ✅ Lifecycle management and hooks
- ✅ Graceful error handling and degradation
- ✅ Metaprogramming with `importlib.util` and `inspect`
