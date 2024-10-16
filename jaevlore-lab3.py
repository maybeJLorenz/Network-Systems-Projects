#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink

class MyTopology(Topo):
    """
    A basic topology
    """
    def __init__(self):
        Topo.__init__(self)

        ## Adding and linking switches 1 and 2
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        self.addLink(switch1, switch2, delay="40ms")

        ## Adding the 4 hosts
        desktopHost = self.addHost('Desktop')
        laptopHost = self.addHost('Laptop')
        lightsHost = self.addHost('Lights')
        fridgeHost = self.addHost('Fridge')

        ## Linking the hosts to their switches
        self.addLink(desktopHost, switch1, delay="40ms")
        self.addLink(laptopHost, switch1, delay="40ms")
        self.addLink(lightsHost, switch2, delay="40ms")
        self.addLink(fridgeHost, switch2, delay="40ms")
if __name__ == '__main__':
    """
    If this script is run as an executable (by chmod +x), this is
    what it will do
    """
    topo = MyTopology() ## Creates the topology
    net = Mininet(topo=topo, link=TCLink) ## Loads the topology
    net.start() ## Starts Mininet
    # Commands here will run on the simulated topology
    CLI(net)
