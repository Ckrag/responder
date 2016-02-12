from http.server import BaseHTTPRequestHandler, HTTPServer
from graphgrapper import GraphGrapper
import time
from urllib.parse import urlparse

hostName = "localhost"
hostPort = 9001

# Very inspired by http://stackoverflow.com/a/26652985
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):

        json = str(GraphGrapper().get_data())
        query_string = urlparse(self.path).query

        #handy for debugging
        if(query_string == "json"):
            response = json
        else:
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