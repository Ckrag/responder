from http.server import BaseHTTPRequestHandler, HTTPServer
from graphgrapper import GraphGrapper
import socket
import time

hostName = "localhost"
hostPort = 9000

# Very inspired by http://stackoverflow.com/a/26652985
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(str(GraphGrapper().get_data()), "utf-8"))


myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    print("Server stopped, ..exiting")

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))