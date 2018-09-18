import sys
from http.server import HTTPServer
from urllib.parse import parse_qsl
from http.server import BaseHTTPRequestHandler
from board import Board

# Handle messages sent from client accordingly.
class HandleRequests(BaseHTTPRequestHandler):
    def do_POST(self):
        print("FUCKING POST MESSAGE")
        coordinates = self.get_coordinates()
        self.send_response(200)
        self.end_headers()
        # need to check here if the spot on the board gets hit

    def do_GET(self):
        self.send_response(404)
        self.end_headers()

    def get_coordinates(self):
        raw_data = self.rfile.read(int(self.headers['Content-Length']))
        byte_coordinates = dict(parse_qsl(raw_data))
        string_coordinates = {key.decode(): val.decode() for key, val in byte_coordinates.items()} #convert from bytes to str
        return string_coordinates

# Print out usage message and exit program.
def usage():
    print("Error Processing command line arguments")
    print("Usage: python3 server.py <port> <txtfilename>")
    sys.exit()

# Make sure user enters correct command line arguments.
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

# Initialize the board.
def initBoard():
    board = Board()
    myBoard = board.read_in_board(sys.argv[2])

# Start the server and listen for client interaction.
def startServer():
    PORT = int(sys.argv[1])
    server_address = ('127.0.0.1', PORT)
    print("Server started and Listening...")
    httpd = HTTPServer(server_address, HandleRequests)
    httpd.serve_forever()

# Start of program.
if __name__ == '__main__':
    handleArgs()
    initBoard()
    startServer()
