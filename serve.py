#!/usr/bin/env python3
"""
Simple HTTP server to view the Seattle Customer Service visualization.
Run this script and open http://localhost:8000/visualization.html in your browser.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow loading local JSON
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        # Custom logging format
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    # Change to the script directory
    os.chdir(Path(__file__).parent)

    print("\n" + "="*60)
    print("Seattle Customer Service Requests - 3D Visualization Server")
    print("="*60)
    print(f"\nStarting server on port {PORT}...")
    print(f"URL: http://localhost:{PORT}/visualization.html")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        # Try to open browser automatically
        try:
            webbrowser.open(f'http://localhost:{PORT}/visualization.html')
            print("Opening browser automatically...\n")
        except:
            print("Could not open browser automatically.")
            print(f"Please open http://localhost:{PORT}/visualization.html manually\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            httpd.shutdown()
            print("Server stopped.")

if __name__ == '__main__':
    main()
