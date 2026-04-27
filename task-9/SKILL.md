# Skill: Task 9 - Plugin Architecture with Dynamic Module Loading

This skill provides comprehensive guidance for developing and extending the plugin architecture system.

## Overview

Task 9 implements a flexible plugin system that discovers, loads, and manages plugins at runtime. It features dependency resolution via topological sort, lifecycle hooks (activate/deactivate), and a registry for plugins to extend core functionality.

## Project Architecture

### Components

1. **plugin_base.py**: Abstract base class defining plugin interface
2. **dependency_resolver.py**: Topological sort for dependency graph resolution
3. **core.py**: Plugin manager and application core
4. **example.py**: Demonstration with multiple interdependent plugins
5. **plugins/**: Directory containing plugin implementations

### Plugin System Flow

1. **Discovery**: Core scans `./plugins/` for Python files containing plugin classes
2. **Registration**: Each plugin declares name, version, and dependencies
3. **Validation**: Dependency graph is built and validated (no cycles)
4. **Resolution**: Topological sort determines activation order
5. **Activation**: Plugins activate in dependency order, each calling `activate()` hook
6. **Usage**: Core app calls registered functions from active plugins

## Creating New Plugins

### Plugin Template

```python
from plugin_base import PluginBase

class MyPlugin(PluginBase):
    def __init__(self):
        super().__init__(
            name="my-plugin",
            version="1.0.0",
            description="My custom plugin",
            required_plugins=[]  # list of plugin names this depends on
        )

    def activate(self):
        print(f"Activating {self.name}")
        # Register commands, themes, etc.
        # Store references to other plugins if needed
        return True

    def deactivate(self):
        print(f"Deactivating {self.name}")
        # Cleanup code
        return True
```

### Declaring Dependencies

```python
class RSSFeedPlugin(PluginBase):
    def __init__(self):
        super().__init__(
            name="rss-feed",
            version="1.0.0",
            required_plugins=["markdown-parser"]  # Depends on markdown-parser
        )
```

## Common Tasks & Solutions

### Running the Example

```bash
cd task-9
python example.py
```

Output shows:

- Plugin discovery results
- Dependency resolution status
- Activation order
- Plugin commands and features used

### Debugging Plugin Loading

**Problem**: Plugin not discovered

- Check file is in `./plugins/` directory
- Verify it contains a class inheriting from `PluginBase`
- Check class is not prefixed with underscore

**Problem**: Circular dependency error

- Check `required_plugins` list for cycles (A→B→A)
- Use `dependency_resolver.py` logic to trace the cycle
- Refactor plugins to break the cycle (e.g., use events instead)

**Problem**: Plugin activation fails

- Add try/except in `activate()` to capture errors
- Check dependencies are actually active before using them
- Verify version compatibility between plugins

## Key Files to Understand

- `plugin_base.py`: Base interface and plugin contract
- `dependency_resolver.py`: Lines 10-40: Topological sort implementation
- `core.py`: Lines 50-150: Plugin manager and activation logic
- `example.py`: Real-world usage with 4 different plugins

## Plugin Registry Pattern

Plugins typically register features with the core app:

```python
def activate(self):
    # Register theme
    self.core.register_theme("dark", dark_theme_css)
    # Register command
    self.core.register_command("optimize", self.optimize_images)
    # Register formatter
    self.core.register_formatter("markdown", markdown_to_html)
```

The core app then uses these registered functions:

```python
core.call_command("optimize")  # Calls registered command
html = core.format("markdown", content)  # Uses registered formatter
```

## Testing Plugin Changes

After modifying a plugin, re-run example.py to verify:

1. Plugin is discovered (check output log)
2. Dependencies resolve correctly
3. Plugin activates without errors
4. Registered features are available to core app
