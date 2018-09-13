import sys
import socket
import requests

def usage():
    print("Error Processing command line arguments")
    print("Usage: python3 client.py <address> <port> <x> <y>")
    sys.exit()

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

def fire():
    serv_addr = sys.argv[1]
    port = int(sys.argv[2])
    x = int(sys.argv[3])
    y = int(sys.argv[4])
    serv_url = "http://%s:%d" %(serv_addr, port)
    data = dict(x = x, y = y)
    resp = requests.post(serv_url, data)
    
    #example 
    #http://111.222.333.444:5555?x=5&y=7

#start of program
if __name__ == '__main__':
    handleArgs()
    fire()
