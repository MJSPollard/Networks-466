import network_2_1
import argparse
from time import sleep
import hashlib
import datetime
import sys

class Packet:
    ## the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    ## length of md5 checksum in hex
    checksum_length = 32 
        
    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S
        
    @classmethod
    def from_byte_S(self, byte_S):
        if Packet.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')
        #extract the fields
        seq_num = int(byte_S[Packet.length_S_length : Packet.length_S_length+Packet.seq_num_S_length])
        msg_S = byte_S[Packet.length_S_length+Packet.seq_num_S_length+Packet.checksum_length :]
        return self(seq_num, msg_S)
        
        
    def get_byte_S(self):
        #convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        #convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(self.length_S_length)
        #compute the checksum
        checksum = hashlib.md5((length_S+seq_num_S+self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        #compile into a string
        return length_S + seq_num_S + checksum_S + self.msg_S
   
    
    @staticmethod
    def corrupt(byte_S):
        #extract the fields
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length : Packet.seq_num_S_length+Packet.seq_num_S_length]
        checksum_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length : Packet.seq_num_S_length+Packet.length_S_length+Packet.checksum_length]
        msg_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length+Packet.checksum_length :]
        
        #compute the checksum locally
        checksum = hashlib.md5(str(length_S+seq_num_S+msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()
        #and check if the same
        return checksum_S != computed_checksum_S
        

class RDT:
    ## latest sequence number used in a packet
    seq_num = 1
    ## buffer of bytes read from network
    byte_buffer = '' 

    def __init__(self, role_S, server_S, port):
        self.network = network_2_1.NetworkLayer(role_S, server_S, port)
    
    def disconnect(self):
        self.network.disconnect()

    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())

    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet
            #create packet from buffer content and add to return string
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration

    def rdt_2_1_send(self, msg_S):
        packet = Packet(self.seq_num, msg_S)
        print("Packet Sequence Number = ", self.seq_num)
 
        # wait for packet to be sent
        while True:

             # init the response to an empty string
            response = ""

            # Attempt to send the packet.
            self.network.udt_send(packet.get_byte_S())

            # wait for some sort of response, exit on 5 second time out
            # start_time = datetime.datetime.now()
            while(response == ""):
                response = self.network.udt_receive()
                # if((datetime.datetime.now() - start_time) > datetime.timedelta(seconds = 1)):
                #     print("rdt_2_1 waiting for response timed out")
                #     sys.exit()

            # extract info from response
            length = int(response[:Packet.length_S_length])
            packet_info = Packet.from_byte_S(response[:length])
            resp = packet_info.msg_S
            print("resp = ", resp)

            # check type of response
            if(self.isNAK(resp)):
                print("NAK received, send packet again")
            elif(self.isACK(resp)):
                print("ACK received, move on to next packet")
                self.seq_num += 1
                break
            else:
                print("aww fuck nak or ack might be corrupted")

    def rdt_2_1_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        print("In receive")
        print("length = ", len(self.byte_buffer))
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length

            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet

            # check if the packet is corrupted
            if(self.isCorrupted(self.byte_buffer)):
                print("The Packet has been corrupted, sending NAK")
                nak = Packet(self.seq_num, "0") #send which packet is corrupted
                self.network.udt_send(nak.get_byte_S())

            else:
                #extract the data from the packet and put into ret_S
                p = Packet.from_byte_S(self.byte_buffer[0:length])

                print("The Packet is all good dawg, sending ACK")
                nak = Packet(self.seq_num, "1") #send which packet is corrupted
                self.network.udt_send(nak.get_byte_S())

                ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
                #remove the packet bytes from the buffer
                self.byte_buffer = self.byte_buffer[length:]
                #if this was the last packet, will return on the next iteration


    # check if the packet contains a NAK response
    def isNAK(self, response):
        return (response == 0)
    
    # check if the packet contains an ACK response
    def isACK(self, response):
        return (response == 1)
    
    # check if the packet is corrupted
    def isCorrupted(self, packet):
        if(Packet.corrupt(packet)):
            return True
        else:
            return False


if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()
    
    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_1_0_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_2_1_receive())
        rdt.disconnect()
        
        
    else:
        sleep(1)
        print(rdt.rdt_2_1_receive())
        rdt.rdt_1_0_send('MSG_FROM_SERVER')
        rdt.disconnect()
        


        
        