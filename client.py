import sys
import requests

# Print out usage message and exit program.
def usage():
    print("Error Processing command line arguments")
    print("Usage: python3 client.py <address> <port> <x> <y>")
    sys.exit()

# Make sure user enters correct command line arguments.
def handleArgs():
    if(not (len(sys.argv) < 5 or len(sys.argv) > 5)):
        if(not (isinstance(sys.argv[1], str ))):
            usage()
        if(not (isinstance(sys.argv[2], str ))):
            usage()
        try:
            int(sys.argv[3])
        except ValueError:
            usage()
        try:
            int(sys.argv[4])
        except ValueError:
            usage()
    else:
        usage()

# Send message to server containing fire coordinates
def fire():
    server_addr = sys.argv[1]
    port = int(sys.argv[2])
    x = int(sys.argv[3])
    y = int(sys.argv[4])
    server_url = "http://%s:%d" %(server_addr, port)
    response = requests.post(server_url, data={'x': x, 'y': y})
    print(response.status_code, response.reason)

#start of program
if __name__ == '__main__':
    handleArgs()
    fire()
