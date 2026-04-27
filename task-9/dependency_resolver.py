"""
Dependency Resolver

Resolves inter-plugin dependencies using topological sort.
Ensures plugins are activated in the correct order.
"""

from typing import List, Dict, Set
from collections import defaultdict, deque


class DependencyResolver:
    """Resolves plugin dependency graphs and produces activation order."""
    
    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)  # plugin -> dependencies
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)  # dependency -> dependents
    
    def add_plugin(self, plugin_name: str, dependencies: List[str]):
        """
        Add a plugin and its dependencies to the graph.
        
        Args:
            plugin_name: Name of the plugin
            dependencies: List of plugins this plugin depends on
        """
        self.graph[plugin_name] = set(dependencies)
        for dep in dependencies:
            self.reverse_graph[dep].add(plugin_name)
    
    def resolve(self) -> tuple[List[str], List[str]]:
        """
        Resolve dependency graph using topological sort (Kahn's algorithm).
        
        Returns:
            (sorted_plugins, unmet_dependencies) where:
            - sorted_plugins: List of plugin names in activation order
            - unmet_dependencies: List of plugins with unmet dependencies
        """
        # Count in-degrees (number of dependencies for each plugin)
        in_degree = {plugin: len(deps) for plugin, deps in self.graph.items()}
        
        # Queue of plugins with no dependencies
        queue = deque([plugin for plugin, degree in in_degree.items() if degree == 0])
        
        sorted_order = []
        
        while queue:
            # Pick a plugin with no unmet dependencies
            plugin = queue.popleft()
            sorted_order.append(plugin)
            
            # Process dependents of this plugin
            for dependent in self.reverse_graph[plugin]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Find unmet dependencies (plugins not in sorted order = have circular dependencies)
        all_plugins = set(self.graph.keys())
        unmet = list(all_plugins - set(sorted_order))
        
        return sorted_order, unmet
    
    def check_dependency(self, plugin_name: str, available_plugins: List[str]) -> tuple[bool, List[str]]:
        """
        Check if a plugin's dependencies are satisfied.
        
        Args:
            plugin_name: Name of the plugin to check
            available_plugins: List of available/active plugins
            
        Returns:
            (is_satisfied, missing_dependencies)
        """
        dependencies = self.graph.get(plugin_name, set())
        available_set = set(available_plugins)
        missing = [dep for dep in dependencies if dep not in available_set]
        
        return len(missing) == 0, missing


# Simple test
if __name__ == "__main__":
    resolver = DependencyResolver()
    
    # Add plugins
    resolver.add_plugin("markdown-parser", [])
    resolver.add_plugin("dark-mode", [])
    resolver.add_plugin("rss-feed", ["markdown-parser"])
    resolver.add_plugin("image-optimizer", [])
    
    # Resolve
    order, unmet = resolver.resolve()
    
    print("Dependency Resolution")
    print("=" * 40)
    print(f"Plugins: {list(resolver.graph.keys())}")
    print(f"Activation Order: {order}")
    print(f"Unmet Dependencies: {unmet if unmet else 'None'}")
    
    # Test dependency checking
    print("\nDependency Checks:")
    is_sat, missing = resolver.check_dependency("rss-feed", ["markdown-parser"])
    print(f"  rss-feed with [markdown-parser]: {is_sat} (missing: {missing})")
    
    is_sat, missing = resolver.check_dependency("rss-feed", [])
    print(f"  rss-feed with []: {is_sat} (missing: {missing})")
