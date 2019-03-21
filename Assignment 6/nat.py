from mininet.topo import Topo
from mininet.net import Mininet
from mininet.nodelib import NAT
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
import thread
from time import sleep
import mininet.node


def server(net):
    publicServer = net.get('s')
    print("IP of server s is %s" % publicServer.IP())
    publicServer.cmd('tcpdump -i s-eth0 > connection.txt')


def server1(net):
    publicServer = net.get('t')
    print("ip of server t is %s" % publicServer.IP())
    publicServer.cmd('tcpdump -i t-eth0 > connection1.txt')


class NATServer(Topo):
    """
    """
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        # set up inet switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        for i in range(2):
            host = self.addHost(chr(ord('s') + i))
            self.addLink(s2, host)

        public_interface = "nat-eth2"
        private_interface = "nat-eth1"
        local_ip = '192.168.0.1'
        local_subnet = '192.168.0.0/24'
        nat_params = {'ip' : '192.168.0.1/24'}
        nat = self.addNode('nat', cls = NAT, subnet = local_subnet, inetIntf = public_interface, localIntf = private_interface)
        self.addLink(nat, s2, intfName1 = public_interface)
        self.addLink(nat, s1, intfName1 = private_interface, params1 = nat_params)

        for i in range(1, 4):
            host = self.addHost('h%d' % i, ip = '192.168.0.10%d/24' % i, defaultRoute = 'via 192.168.0.1')
            self.addLink(host, s1)


def runner():
    topo = NATServer()
    net = Mininet(topo = topo)
    net.start()
    nat = net.get('nat')
    print("Detailed Connections:")
    dumpNodeConnections(net.hosts)
    print("NAT IP of Public Interface (eth2) is: %s" % nat.IP())
    print("NAT IP of Private Interface (eth1) is: 192.168.0.1")

    CLI(net)
    private_host = net.get('h1')
    thread.start_new_thread(server, (net,))
    thread.start_new_thread(server1, (net,))
    for i in range(1, 4):
        host = net.get('h%d' % i)
        print("IP of Node h%d is %s" % (i, host.IP()))
        sIP = net.get('s').IP()
        tIP = net.get('t').IP()
        print("Node h%d Is Pinging Server s" % i)
        private_host.cmd('ping -c3 %s' % sIP)
        print("Node h%d Is Pinging Server t" % i)
        private_host.cmd('ping -c3 %s' % tIP)
    net.stop()
    
if __name__ == '__main__':
    setLogLevel('info')
    runner()
    print("Network Activity At Server s:")
    with open("connection.txt") as f:
        contents = f.readlines()
    contents = [x.strip() for x in contents]
    for i in range(len(contents)):
        print(contents[i])

    print("Network Activity At Server t:")
    with open("connection1.txt") as f:
        contents = f.readlines()
    contents = [x.strip() for x in contents]
    for i in range(len(contents)):
        print(contents[i])