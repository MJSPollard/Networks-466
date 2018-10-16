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

    def rdt_2_1_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        current_seq = self.seq_num
        self.network.udt_send(p.get_byte_S(), True)
 
        #wait for response 
        while current_seq == self.seq_num:
            
            # add bytes to the byte buffer
            self.byte_buffer += self.network.udt_receive()
            
            # get the required bytes
            if(len(self.byte_buffer) >= Packet.length_S_length):
                pass
            else:
                continue

            # extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) >= length:
                pass
            else:
                continue

            # check for corrupted ack or nak
            if(Packet.corrupt((self.byte_buffer[0:length]))):
                print("sender: corrupt ack or nak")
                self.byte_buffer = self.byte_buffer[length:]
                self.network.udt_send(p.get_byte_S(), True)
            else:
                response = Packet.from_byte_S(self.byte_buffer[0:length])
                self.byte_buffer = self.byte_buffer[length:]

                # print("response seq num = ",response.seq_num)
                # print("self seq num = ",self.seq_num)
                # check type of response
                if response.seq_num != self.seq_num:
                    print("reciever behind sender")
                    ack = Packet(response.seq_num, "1")
                    self.network.udt_send(ack.get_byte_S(), True)

                # print("response seq num2 = ",response.seq_num)
                # print("self seq num2 = ",self.seq_num)

                if(response.seq_num == self.seq_num):
                    if response.msg_S == "0":
                        print("RECEIVED NAK")
                        self.network.udt_send(p.get_byte_S(), True)
                    elif response.msg_S == "1":
                        print("RECEIVED ACK")
                        self.seq_num += 1
                        break

    def rdt_2_1_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S

        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                break

            # extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                break

            # check if the packet is corrupted
            if(Packet.corrupt((self.byte_buffer[0:length]))):
                print("SENDING NAK")
                nak = Packet(self.seq_num, "0")
                self.network.udt_send(nak.get_byte_S(), False)
            else:
                #extract the data from the packet and put into ret_S
                print("SENDING ACK")
                p = Packet.from_byte_S(self.byte_buffer[0:length])

                if p.seq_num == self.seq_num:
                    ack = Packet(self.seq_num, "1")
                    self.seq_num += 1
                    self.network.udt_send(ack.get_byte_S(), False)
                else:
                    ack = Packet(p.seq_num, "1")
                    self.network.udt_send(ack.get_byte_S(), False)

                ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            self.byte_buffer = self.byte_buffer[length:]
        return ret_S
                

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
        rdt.rdt_2_1_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_2_1_receive())
        rdt.disconnect()
        
        
    else:
        sleep(1)
        print(rdt.rdt_2_1_receive())
        rdt.rdt_2_1_send('MSG_FROM_SERVER')
        rdt.disconnect()