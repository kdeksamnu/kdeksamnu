#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"=== CATHEDRAL WORLD SIMULATOR ACTIVE ===")
    print(f"Target URL: http://localhost:{PORT}/cathedral_world_simulator.html")
    if "--open" in sys.argv:
        webbrowser.open(f"http://localhost:{PORT}/cathedral_world_simulator.html")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSimulator server stopped.")
