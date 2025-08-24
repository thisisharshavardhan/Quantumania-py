#!/usr/bin/env python
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

if __name__ == '__main__':
    # Change to the frontend_cdn directory
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend_cdn'))
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print('Starting server on http://localhost:8080...')
    httpd.serve_forever()
