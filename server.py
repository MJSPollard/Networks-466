import sys
import socket
from http.server import HTTPServer

class handleRequests():
    def on_POST():
        print("made it")

def usage():
    print("Error Processing command line arguments")
    print("Usage: python3 server.py <port> <txtfilename>")
    sys.exit()

def handleArgs():
    if(not (len(sys.argv) < 3 or len(sys.argv) > 3)):
        try:
            int(sys.argv[1])
        except ValueError:
            usage()
        if(not (isinstance(sys.argv[2], str ))):
            usage()
    else:
        usage()

def startServer():
    PORT = int(sys.argv[1])
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, handleRequests)
    httpd.serve_forever()

#start of program
if __name__ == '__main__':
    handleArgs()
    startServer()
