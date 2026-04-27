"""
Image Optimizer Plugin

Optimizes images for web distribution.
"""

from plugin_base import PluginBase


class ImageOptimizerPlugin(PluginBase):
    """Optimizes images during site generation."""
    
    name = "image-optimizer"
    version = "0.9.1"
    description = "Optimizes images for web"
    author = "Third-party"
    required_plugins = []
    
    def activate(self, app):
        """Register image optimization."""
        app.register_post_processor("image-optimizer", self.optimize_images)
        app.register_command("compress-images", self.compress_images)
    
    def deactivate(self, app):
        """Clean up image optimizer."""
        pass
    
    def optimize_images(self, format_type: str = "webp"):
        """Optimize images to specified format."""
        print(f"Optimizing images to {format_type} format")
    
    def compress_images(self, directory: str):
        """Compress images in a directory."""
        print(f"Compressing images in: {directory}")
        return {
            "files_processed": 18,
            "bytes_saved": 4200000,
        }
