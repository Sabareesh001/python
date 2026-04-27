"""
Markdown Parser Plugin

Built-in plugin that provides markdown parsing capabilities.
"""

from plugin_base import PluginBase


class MarkdownParserPlugin(PluginBase):
    """Parses markdown files and converts them to HTML."""
    
    name = "markdown-parser"
    version = "2.1.0"
    description = "Converts markdown files to HTML"
    author = "Built-in"
    required_plugins = []
    
    def activate(self, app):
        """Register markdown parsing capability."""
        app.register_formatter("md-to-html", self.convert_md_to_html)
        app.register_post_processor("markdown", self.process_markdown)
    
    def deactivate(self, app):
        """Clean up markdown parser."""
        pass
    
    def convert_md_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML (simplified)."""
        # In a real app, this would use a library like markdown2 or mistune
        html = markdown_content.replace("\n", "<br>")
        html = f"<div class='markdown'>{html}</div>"
        return html
    
    def process_markdown(self, file_path: str):
        """Post-process markdown files."""
        print(f"Processing markdown: {file_path}")
