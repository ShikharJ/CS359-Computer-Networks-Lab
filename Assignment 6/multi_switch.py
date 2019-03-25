from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel


class MultiSwitch(Topo):
    """
    Base class for defining the topology.
    """
    def build(self):
        e = self.addSwitch('e1', ip = '192.168.0.100/24', mac = '00:00:00:00:00:09')
        f = self.addSwitch('f1', ip = '192.168.0.101/24', mac = '00:00:00:00:00:10')
        a = self.addHost('a', ip = '192.168.0.102/24', mac = '00:00:00:00:00:00')
        b = self.addHost('b', ip = '192.168.0.103/24', mac = '00:00:00:00:01:00')
        c = self.addHost('c', ip = '192.168.0.104/24', mac = '00:00:00:00:02:00')
        s = self.addHost('s', ip = '192.168.0.106/24', mac = '00:00:00:00:04:00')
        t = self.addHost('t', ip = '192.168.0.107/24', mac = '00:00:00:00:05:00')
        self.addLink(a, e, bw = 5, delay = '3ms', loss = 2, max_queue_size = 300)
        self.addLink(b, e, bw = 5, delay = '3ms', loss = 2, max_queue_size = 300)
        self.addLink(c, e, bw = 5, delay = '3ms', loss = 2, max_queue_size = 300)
        self.addLink(s, f, bw = 5, delay = '3ms', loss = 2, max_queue_size = 300)
        self.addLink(t, f, bw = 5, delay = '3ms', loss = 2, max_queue_size = 300)
        self.addLink(e, f, bw = 15, delay = '2ms')


def runner():
    topo = MultiSwitch()
    net = Mininet(topo = topo, link = TCLink)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    runner()