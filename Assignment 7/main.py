from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink


def topology():
    net = Mininet(controller = RemoteController, link = TCLink, switch = OVSKernelSwitch)

    # Add hosts, switches and a controller.
    h1 = net.addHost('h1', ip = "10.0.1.10/24", mac = "00:00:00:00:00:01")
    h2 = net.addHost('h2', ip = "10.0.2.10/24", mac = "00:00:00:00:00:02")
    r1 = net.addHost('r1')
    r2 = net.addHost('r2')

    net.addLink(r1, h1)
    net.addLink(r2, h2)
    net.addLink(r1, r2)

    net.build()
    r1.cmd("sysctl net.ipv4.ip_forward=1")
    r2.cmd("sysctl net.ipv4.ip_forward=1")

    r1.cmd("ifconfig r1-eth0 0")
    r2.cmd("ifconfig r2-eth0 0")
    r1.cmd("ifconfig r1-eth1 0")
    r2.cmd("ifconfig r2-eth1 0")

    r1.cmd("ifconfig r1-eth0 hw ether 00:00:00:00:01:01")
    r2.cmd("ifconfig r2-eth0 hw ether 00:00:00:00:01:02")

    r1.cmd("ip addr add 10.0.1.1/24 brd + dev r1-eth0")
    r1.cmd("ip addr add 10.0.3.2/24 brd + dev r1-eth1")
    r1.cmd("ip route add to 10.0.2.0/24 via 10.0.3.1 dev r1-eth1")

    r2.cmd("ip addr add 10.0.2.1/24 brd + dev r2-eth0")
    r2.cmd("ip addr add 10.0.3.1/24 brd + dev r2-eth1")
    r2.cmd("ip route add to 10.0.1.0/24 via 10.0.3.2 dev r2-eth1")

    r1.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
    h1.cmd("ip route add default via 10.0.1.1")
    h2.cmd("ip route add default via 10.0.2.1")

    print "*** Running CLI"
    CLI(net)
    print "*** Stopping network"
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()