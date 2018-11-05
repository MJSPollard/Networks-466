'''
Created on Oct 12, 2016

@author: mwittie
'''
import network_3
import link_3
import threading
from time import sleep


##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 1 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads

    #create network nodes
    host_1 = network_3.Host(1)
    object_L.append(host_1)
    host_2 = network_3.Host(2)
    object_L.append(host_2)
    host_3 = network_3.Host(3)
    object_L.append(host_3)
    host_4 = network_3.Host(4)
    object_L.append(host_4)
    # key-interface value-destination
    router_a = network_3.Router(name='A', intf_count=2,
                                max_queue_size=router_queue_size, routing_table={3:0, 4:1})
    router_b = network_3.Router(name='B', intf_count=1,
                                max_queue_size=router_queue_size, routing_table={3:0})
    router_c = network_3.Router(name='C', intf_count=1,
                                max_queue_size=router_queue_size, routing_table={4:0})
    router_d = network_3.Router(name='D', intf_count=2,
                                max_queue_size=router_queue_size, routing_table={3:0, 4:1})
    object_L.append(router_a)
    object_L.append(router_b)
    object_L.append(router_c)
    object_L.append(router_d)

    #create a Link Layer to keep track of links between network nodes
    link_layer = link_3.LinkLayer()
    object_L.append(link_layer)

    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    link_layer.add_link(link_3.Link(host_1, 0, router_a, 0, 50))
    link_layer.add_link(link_3.Link(host_2, 0, router_a, 0, 50))
    link_layer.add_link(link_3.Link(router_a, 0, router_b, 0, 50))
    link_layer.add_link(link_3.Link(router_a, 1, router_c, 0, 50))
    link_layer.add_link(link_3.Link(router_b, 0, router_d, 0, 50))
    link_layer.add_link(link_3.Link(router_c, 0, router_d, 0, 50))
    link_layer.add_link(link_3.Link(router_d, 0, host_3, 0, 50))
    link_layer.add_link(link_3.Link(router_d, 1, host_4, 0, 50))



    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=host_1.__str__(), target=host_1.run))
    thread_L.append(threading.Thread(name=host_2.__str__(), target=host_2.run))
    thread_L.append(threading.Thread(name=host_3.__str__(), target=host_3.run))
    thread_L.append(threading.Thread(name=host_4.__str__(), target=host_4.run))

    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))

    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()


    #create some send events
    data = ('ZxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxO')

    hosts = [host_1, host_2]
    recipients = [3, 4]

    for i in range(len(hosts)-1):

    # if the data length is large than 40, split it up and send it in multiple parts
        if(len(data) > 40 ):
            firstChar = 0
            lastChar = 40
            while True:
                if(lastChar > len(data)):
                    hosts[i].udt_send(recipients[i], data[firstChar:])
                    break
                else:
                    hosts[i].udt_send(recipients[i], data[firstChar:lastChar])
                firstChar = firstChar + 40
                lastChar = lastChar + 40
        else:
            host_list[i].udt_send(recipients[i], data)

    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")



# writes to host periodically
