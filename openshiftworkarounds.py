import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import requests
import threading
from datetime import datetime


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        uptime = str(datetime.now() - self.server.start_time).split('.')[0]
        self.wfile.write("Tofbot uptime: %s" % uptime)

    def do_HEAD(self):
        self._set_headers()


def serve(server_class=HTTPServer, handler_class=S):
    port = int(os.getenv("OPENSHIFT_PYTHON_PORT", "8080"))
    ip = os.getenv('OPENSHIFT_PYTHON_IP', '')
    server_address = (ip, port)
    httpd = server_class(server_address, handler_class)
    httpd.start_time = datetime.now()
    httpd.serve_forever()


def enable():
    server = threading.Thread(target=serve)
    server.daemon = True
    server.start()
