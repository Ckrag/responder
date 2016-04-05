#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from graphgrapper import GraphGrapper
import time
from utils import Util

hostName = "localhost"
hostPort = 9001
sources_content = None

# Very inspired by http://stackoverflow.com/a/26652985
class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        json = str(GraphGrapper().get_data(Util.get_source_content()))

        response = "jsonpCallback({0})".format(json)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(response, "utf-8"))


myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    print("Server stopped, ..exiting")

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))