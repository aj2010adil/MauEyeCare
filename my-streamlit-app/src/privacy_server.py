#!/usr/bin/env python
"""
Simple HTTP server to serve privacy policy and terms of service
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

class PrivacyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent.parent), **kwargs)

def start_privacy_server(port=8080):
    """Start privacy policy server"""
    try:
        with socketserver.TCPServer(("", port), PrivacyHandler) as httpd:
            print(f"Privacy Policy Server running at:")
            print(f"Privacy Policy: http://localhost:{port}/privacy.html")
            print(f"Terms of Service: http://localhost:{port}/terms.html")
            print(f"\nFor Meta submission, use these URLs:")
            print(f"Privacy Policy URL: http://localhost:{port}/privacy.html")
            print(f"Terms of Service URL: http://localhost:{port}/terms.html")
            print(f"\nPress Ctrl+C to stop the server")
            
            # Open privacy policy in browser
            webbrowser.open(f"http://localhost:{port}/privacy.html")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} is already in use. Trying port {port+1}")
            start_privacy_server(port+1)
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_privacy_server()