from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel


class MultiSwitch(Topo):
    """
    Base class for defining the topology.
    """
    def build(self):
        s = self.addSwitch('s1')
        t = self.addSwitch('t1')
        a = self.addHost('a', cpu = 0.5 / 6)
        b = self.addHost('b', cpu = 0.5 / 6)
        c = self.addHost('c', cpu = 0.5 / 6)
        d = self.addHost('d', cpu = 0.5 / 6)
        source = self.addHost('source', cpu = 0.5 / 6)
        sink = self.addHost('sink', cpu = 0.5 / 6)
        self.addLink(a, s, bw = 5, delay = '3ms', loss = 2)
        self.addLink(b, s, bw = 5, delay = '3ms', loss = 2)
        self.addLink(c, t, bw = 5, delay = '3ms', loss = 2)
        self.addLink(d, t, bw = 5, delay = '3ms', loss = 2)
        self.addLink(s, t, bw = 15, delay = '2ms')
        self.addLink(c, sink, bw = 15, delay = '2ms')
        self.addLink(source, a, bw = 15, delay = '2ms')
        self.addLink(source, b, bw = 15, delay = '2ms')


def runner():
    topo = MultiSwitch()
    net = Mininet(topo = topo, host = CPULimitedHost, link = TCLink)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    source = net.get('source')
    sink = net.get('sink')
    net.pingAll()
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    runner()