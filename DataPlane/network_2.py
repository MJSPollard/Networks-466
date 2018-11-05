'''
Created on Oct 12, 2016

@author: mwittie
'''
import queue
import threading


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
        self.mtu = None
    
    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)


## Implements a network layer packet (different from the RDT packet
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths
    dst_addr_S_length = 5
    flag_S_length = 1
    offset_S_length = 2
    header_S_length = dst_addr_S_length + flag_S_length + offset_S_length

    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S, flag = 0, offset = 0):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.flag = flag
        self.offset = offset

    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()

    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return byte_S

    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length : ]
        return self(dst_addr, data_S)

    ## convert packet to a byte string for transmission over links with fragment fields
    def to_fragment_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += str(self.flag).zfill(self.flag_S_length)
        byte_S += str(self.offset).zfill(self.offset_S_length)
        byte_S += self.data_S
        return byte_S

    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_fragment_byte_S(self, byte_S, curMTU):
        dst_addr = int(byte_S[0: NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length:]
        fragmented_packets = []
        offset = 0
        flag = 2

        # fragment the packets
        while 1:
            if self.header_S_length + len(data_S[offset:]) > curMTU:
                flag = 1 # more packets coming
            else:
                flag = 0 # last fragment
            
            #set offset increment
            increment = curMTU + offset - self.header_S_length

            #append correct length info to the packets
            fragmented_packets.append(self(dst_addr, data_S[offset:increment], flag, offset))
            offset = increment

            # break out of the loop when the flag indicates the last fragment (0)
            if flag == 0:
                break
            if flag == 2: # sanity check
                print("flag is still 2")
                break

        return fragmented_packets


## Implements a network host for receiving and transmitting data
class Host:
    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False  # for thread termination
        self.fragments = []

    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)

    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S, MTU_limit):
        # if packet is too large for maximum transmission unit
        if(len(data_S) > MTU_limit):
            firstChar = 0
            lastChar = MTU_limit
            # Keep breaking up packets into specific chunks until the length left is less than the mtu
            while True:
                if(lastChar > len(data_S)):
                    p = NetworkPacket(dst_addr, data_S[firstChar:])
                    self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
                    print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))
                    break
                else:
                    p = NetworkPacket(dst_addr, data_S[firstChar:lastChar])
                    self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
                #increase position in packets and print
                firstChar = firstChar + MTU_limit
                lastChar = lastChar + MTU_limit
                print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))
        else:
            p = NetworkPacket(dst_addr, data_S)
            self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
            print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

    ## receive packet from the network layer and reconstruct if fragmented
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()

        if pkt_S is not None:
            # append the packet fragments back together excluding the header info
            self.fragments.append(pkt_S[NetworkPacket.header_S_length:])
            # if the network packet is the last to be added (indicated by 0 flag), print out and reset
            if(pkt_S[NetworkPacket.dst_addr_S_length] == '0'):
                print('%s: received packet "%s" on the in interface' % (self, str(self.fragments)))
                self.fragments = []

    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return

## Implements a multi-interface router described in class
class Router:
    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces 
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.from_fragment_byte_S(pkt_S, self.out_intf_L[i].mtu)  # parse a packet out
                    #forward all fragments of a packet
                    for packet_num in p:
                        self.out_intf_L[i].put(packet_num.to_fragment_byte_S(), True)
                        print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' % (self, packet_num.to_fragment_byte_S(), i, i, self.out_intf_L[i].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass

    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 