#!/usr/bin/env python3
"""
Simple HTTP Server for hosting static files (HTML, CSS, JS)
Serves files from the 'client' directory on port 8000
"""

import http.server
import socketserver
import os
from pathlib import Path
from datetime import datetime


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with better logging."""
    
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format, *args):
        """Override to add timestamp to log messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {format % args}")
    
    def end_headers(self):
        """Add headers to prevent caching during development."""
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Expires', '0')
        super().end_headers()


def run_server(port=8000, directory="client"):
    """Start the HTTP server.
    
    Args:
        port: Port number to listen on (default: 8000)
        directory: Directory to serve files from (default: "client")
    """
    # Convert to absolute path
    abs_dir = Path(directory).resolve()
    
    if not abs_dir.exists():
        print(f"❌ Error: Directory '{directory}' not found at {abs_dir}")
        return
    
    if not abs_dir.is_dir():
        print(f"❌ Error: '{directory}' is not a directory")
        return
    
    # Change to the directory
    os.chdir(abs_dir)
    
    # Create server
    handler = lambda *args, **kwargs: MyHTTPRequestHandler(*args, directory=abs_dir, **kwargs)
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            hostname = "localhost"
            print(f"✅ HTTP Server started")
            print(f"   URL: http://{hostname}:{port}")
            print(f"   Serving: {abs_dir}")
            print(f"   Press Ctrl+C to stop\n")
            httpd.serve_forever()
    
    except OSError as e:
        if e.errno == 48 or e.errno == 98:  # Address already in use
            print(f"❌ Error: Port {port} is already in use")
            print(f"   Try a different port: python http_server.py --port 8001")
        else:
            print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n✋ Server stopped by user")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Simple HTTP server for serving static files"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to listen on (default: 8000)"
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="client",
        help="Directory to serve files from (default: client)"
    )
    
    args = parser.parse_args()
    run_server(port=args.port, directory=args.directory)
