import sys
from http.server import HTTPServer
from urllib.parse import parse_qsl
from http.server import BaseHTTPRequestHandler
from board import Board
board = Board()

# Handle messages sent from client accordingly.
class HandleRequests(BaseHTTPRequestHandler):
    def do_POST(self):
        print("FUCKING POST MESSAGE")
        coordinates = self.get_coordinates()
        self.send_result(board.check_hit(int(coordinates.get('x', "-1")), int(coordinates.get('y', "-1"))))
        self.end_headers()

    # handle html get request thing for baord
    def do_GET(self):
        print("GET MESSAGE")
        self.send_response(200)

        if(self.path == "/own_board.html"):
            print("own_board")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.print_own_board(self.wfile)

        if(self.path == "/opponent_board.html"):
            print("opponent board")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.print_opponent_board(self.wfile)

    # Return coordinates in string type dictionary.
    def get_coordinates(self):
        raw_data = self.rfile.read(int(self.headers['Content-Length']))
        byte_coordinates = dict(parse_qsl(raw_data))
        string_dict_coordinates = {key.decode(): val.decode() for key, val in byte_coordinates.items()}
        return string_dict_coordinates

    # Check what the coords hit and send client back appropriate message.
    def send_result(self, result):
        if(result == "HIT"):
            print("HIT")
            self.send_response(200, "hit=1")
        elif(result[:-1] == "SUNK"):
            print("SUNK")
            print("result[len(result) - 1:]")
            self.send_response(200, ("hit=1 sink=" + (result[len(result) - 1:])))
        elif(result == "MISS"):
            print("MISS")
            self.send_response(200, "hit=0")
        elif(result == "ALREADY_HIT"):
            print("ALREADY HIT")
            self.send_response(410)
        elif(result == "OUT_OF_BOUNDS"):
            print("OOB")
            self.send_response(404)
        else:
            print("Error")
            self.send_response(500)


# Print out the players own board
    def print_own_board(self, wfile):
        wfile.write(bytes('<html><head><title>Battleship</title></head><body>', "utf-8"))
        wfile.write(bytes('<h2>BATTLESHIP: Own board</h2>', "utf-8"))
        bb = board.get_board()
        for y in range(9):
            for x in range(9):
                wfile.write(bytes(bb[y][x] + ' ', "utf-8"))
            wfile.write(bytes('<br>', "utf-8"))
        wfile.write(bytes('<br><a href="own_board.html"><button>Refresh</button></a>', "utf-8"))
        wfile.write(bytes('<a href="opponent_board.html"><button>View Opponent Board</button></a>', "utf-8"))
        wfile.write(bytes('</body></html>', "utf-8"))

    def print_opponent_board(selfself, wfile):
        wfile.write(bytes('<html><head><title>Battleship</title></head><body>', "utf-8"))
        wfile.write(bytes('<h2>BATTLESHIP: Opponent board</h2>', "utf-8"))
        bb = board.get_opp_board()
        for y in range(9):
            for x in range(9):
                wfile.write(bytes(bb[y][x] + ' ', "utf-8"))
            wfile.write(bytes('<br>', "utf-8"))
        wfile.write(bytes('<br><a href="opponent_board.html"><button>Refresh</button></a>', "utf-8"))
        wfile.write(bytes('<a href="own_board.html"><button>View Own Board</button></a>', "utf-8"))
        wfile.write(bytes('</body></html>', "utf-8"))


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

# Start the server and listen for client interaction.
def startServer():
    port = int(sys.argv[1])
    server_address = ('127.0.0.1', port)
    print("Server started and listening...")
    httpd = HTTPServer(server_address, HandleRequests)
    httpd.serve_forever()

# Start of program.
if __name__ == '__main__':
    handleArgs()
    board.read_in_board(sys.argv[2])
    startServer()