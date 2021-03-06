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

    # check the results of the fire message
    if(response.status_code == 200):
        if(response.reason[len(response.reason) - 1:] == '1'):
            print("You hit a ship!")
        elif(response.reason[len(response.reason) - 1:] == '0'):
            print("You missed")
        else:
            print("You sunk a ship!")
    elif(response.status_code == 410):
        print("You already hit that spot!")
    elif(response.status_code == 404):
        print("You're shot was out of bounds!")
    else:
        print("There was an error!")

    # update record of players shots on opponent board
    requests.get(server_url + "/opponent_board.html")

# start of program
if __name__ == '__main__':
    handleArgs()
    fire()
