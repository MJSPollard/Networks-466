import network_3_0
import argparse
import time
from time import sleep
import hashlib


class Packet:
    ## the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    ## length of md5 checksum in hex
    checksum_length = 32
        
    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S

    def get_seq_num(self):
        return self.seq_num
        
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
    seq_num_list = []
    ## buffer of bytes read from network
    byte_buffer = '' 

    def __init__(self, role_S, server_S, port):
        self.network = network_3_0.NetworkLayer(role_S, server_S, port)
    
    def disconnect(self):
        self.network.disconnect()

    # Implementation of RDT 3.0 send method
    def rdt_3_0_send(self, msg_S):

        # Create packet and set sequence number
        p = Packet(self.seq_num, msg_S)
        current_seq = self.seq_num

        # Send packet over udt network layer
        self.network.udt_send(p.get_byte_S(), True)

        # Attributes for processing a timeout by the client
        sent_time = time.time()
        timer = 3;

        # wait for response
        while current_seq == self.seq_num:

            # Concatenate bytes to byte buffer
            self.byte_buffer += self.network.udt_receive()

            # If no response after given time occurs, refresh buffer and resend packet
            if sent_time + timer - time.time() < 0 and len(self.byte_buffer) == 0:
                print("TIMEOUT")
                self.byte_buffer = ''
                sent_time = time.time()
                self.network.udt_send(p.get_byte_S(), True)
                continue

            # get the required bytes
            if len(self.byte_buffer) >= Packet.length_S_length:
                pass
            else:
                continue

            # extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) >= length:
                pass
            else:
                continue

            # If packet is corrupted, set sequence number back and resend packet
            if Packet.corrupt((self.byte_buffer[0:length])):
                self.byte_buffer = self.byte_buffer[length:]
                self.network.udt_send(p.get_byte_S(), True)
                self.seq_num -= 1

            else:
                # If valid Packet, determine response
                ack = Packet.from_byte_S(self.byte_buffer[0:length])
                self.byte_buffer = ''

                # Determine either ACK or NAK from response packet
                if ack.seq_num == self.seq_num:
                    if ack.msg_S == "0":
                        print("RECEIVED NAK")
                        self.network.udt_send(p.get_byte_S(), True)
                    elif ack.msg_S == "1":
                        print("RECEIVED ACK")
                        self.seq_num += 1
                        break

    # Implementation of RDT 3.0 send method
    def rdt_3_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S

        #keep extracting packets - if reordered, could get more than one
        while True:

            #check if we have received enough bytes
            if len(self.byte_buffer) < Packet.length_S_length:
                break #not enough bytes to read packet length

            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                break #not enough bytes to read the whole packet

            # If packet is corrupt, send NAK packet
            if Packet.corrupt(self.byte_buffer):
                # print ("Corrupted")
                nack = Packet(self.seq_num, "0")
                self.network.udt_send(nack.get_byte_S(), False)
            else:
                # Create packet from byte buffer message and send appropriate acknowledgement
                p = Packet.from_byte_S(self.byte_buffer[0:length])

                # Check duplicate packet
                if self.seq_num in self.seq_num_list:
                    # Will be printed from the server side
                    print("Duplicate packet")
                    ack = Packet(self.seq_num, "1")
                    self.network.udt_send(ack.get_byte_S(), False)
                    break
                self.seq_num_list.append(self.seq_num)

                # check sequence numbers and send ACK packet
                if p.seq_num == self.seq_num:
                    ack = Packet(self.seq_num, "1")
                    self.seq_num += 1
                    self.network.udt_send(ack.get_byte_S(), False)
                else:
                    ack = Packet(p.seq_num, "1")
                    self.network.udt_send(ack.get_byte_S(), False)

                # Retrieve message from the packet
                ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S

            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
        return ret_S

if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()
    
    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_3_0_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_3_0_receive())
        rdt.disconnect()
        
        
    else:
        sleep(1)
        print(rdt.rdt_3_0_receive())
        rdt.rdt_3_0_send('MSG_FROM_SERVER')
        rdt.disconnect()
        


        
        