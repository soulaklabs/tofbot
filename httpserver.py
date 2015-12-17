import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body>I am not dead!</body></html>")

    def do_HEAD(self):
        self._set_headers()


def run(server_class=HTTPServer, handler_class=S):
    port = int(os.getenv("OPENSHIFT_PYTHON_PORT", "8080"))
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
