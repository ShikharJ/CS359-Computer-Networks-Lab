from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
import thread
from time import sleep


def server(net):
    h1 = net.get('h1')
    h1.cmd('iperf -s -p 5111 -i 2 > throughput.txt')


class SingleSwitch(Topo):
    """
    Base class for defining the topology.
    """
    def build(self):
        switch = self.addSwitch('s1')
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        self.addLink(host1, switch)
        self.addLink(host2, switch)


def runner():
    topo = SingleSwitch()
    net = Mininet(topo = topo)
    net.start()
    dumpNodeConnections(net.hosts)
    h1 = net.get('h1')
    h2 = net.get('h2')
    thread.start_new_thread(server, (net,))
    h2.cmd('iperf -c 10.0.0.1 -p 5111 -t 20')


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    runner()
    count = 0
    print("Required Throughput")
    print("Time Interval       Throughput")
    with open("throughput.txt") as f:
        contents = f.readlines()
    contents = [x.strip() for x in contents]
    for i in range(6, len(contents)):
        line = contents[i].split()
        if i <= 9:
            print("[%s %s %s] ---> %s %s" % (line[2], line[3], line[4], float(line[5]) / 2, line[6] + "/sec"))
        elif i == len(contents) - 1:
            print("[%s %s] ---> %s %s " % (line[2], line[3], float(line[4]) / 20, line[5] + "/sec"))
        else:
            print("[%s %s] ---> %s %s " % (line[2], line[3], float(line[4]) / 2, line[5] + "/sec"))