import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import requests
import threading
import time


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


def serve(server_class=HTTPServer, handler_class=S):
    port = int(os.getenv("OPENSHIFT_PYTHON_PORT", "8080"))
    ip = os.getenv('OPENSHIFT_PYTHON_IP', '')
    server_address = (ip, port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


def self_query():
    host = os.getenv("OPENSHIFT_APP_DNS", "127.0.0.1")
    while True:
        time.sleep(3600)
        requests.get("http://" + host)


def do():
    server = threading.Thread(target=serve)
    server.daemon = True
    server.start()

    keepalive = threading.Thread(target=self_query)
    keepalive.daemon = True
    keepalive.start()

