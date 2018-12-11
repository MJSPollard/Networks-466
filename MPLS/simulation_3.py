from network_3 import Router, Host
from link_3 import Link, LinkLayer
import threading
from time import sleep
import sys
from copy import deepcopy

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 15 #give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads at the end

    #create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)

    #create routers and routing tables for connected clients (subnets)

    #determine where encapsulation and decapsulation are needed
    encap_tbl_D = {"LP": {"RA"}, "HP": {"RA"}}
    decap_tbl_D = {"RD":{"H3"}}

    # inlabel outlabel, dest, outinterface
    frwd_tbl_D = {"LP": ("1", "H3", 2), "HP": ("2", "H3", 3)}

    router_a = Router(name='RA',
                              intf_capacity_L=[500,500,500,500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_a)

    # inlabel outlabel, dest, outinterface
    frwd_tbl_D = {"1": ("1", "H3", 1)}

    router_b = Router(name='RB',
                              intf_capacity_L=[500,500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_b)

    # inlabel outlabel, dest, outinterface
    frwd_tbl_D = {"2": ("2", "H3", 1)}

    router_c = Router(name='RC',
                              intf_capacity_L=[500,500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_c)

    # inlabel outlabel, dest, outinterface
    frwd_tbl_D = {"1": ("H3", "H3", 2), "2": ("H3", "H3", 2)}

    router_d = Router(name='RD',
                              intf_capacity_L=[500,500,100],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_d)


    #create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)

    #add all the links - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(Link(host_1, 0, router_a, 0))
    link_layer.add_link(Link(host_2, 0, router_a, 1))
    link_layer.add_link(Link(router_a, 2, router_b, 0))
    link_layer.add_link(Link(router_a, 3, router_c, 0))
    link_layer.add_link(Link(router_b, 1, router_d, 0))
    link_layer.add_link(Link(router_c, 1, router_d, 1))
    link_layer.add_link(Link(router_d, 2, host_3, 0))


    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run))

    for t in thread_L:
        t.start()

    #create some send events
    for i in range(1):
        # priority 1
        host_1.udt_send('H3', 'Sending on Priority Channel', 1)
        # priority 0
        host_2.udt_send('H3', 'Sending on Normal Channel', 0)

    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)


    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")
