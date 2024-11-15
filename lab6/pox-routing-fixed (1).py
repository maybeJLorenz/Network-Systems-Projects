# Lab5 Skeleton
#
#     Last Modified: november 11, 8:40pm
# 

from pox.core import core
import pox.openflow.libopenflow_01 as of
import ipaddress

log = core.getLogger()

class Routing (object):
    
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

  def do_routing (self, packet, packet_in, port_on_switch, switch_id):
    # port_on_switch - the port on which this packet was received
    # switch_id - the switch which received this packet

    # Your code here
    def do_routing(self, packet, packet_in, port_on_switch, switch_id):
    def accept(end_port):
        msg = of.ofp_flow_mod()
        msg.data = packet_in
        msg.match = of.ofp_match.from_packet(packet)
        msg.actions.append(of.ofp_action_output(port=end_port))
        msg.buffer_id = packet_in.buffer_id
        self.connection.send(msg)
        print("Packet Accepted - Flow Table Installed on Switches")
    
    def drop():
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        self.connection.send(msg)
        print("Packet Dropped - Flow Table Installed on Switches")

    # Get network type based on IP
    def get_network(ip):
        if not ip: return None
        ip = str(ip)
        if ip.startswith('10.0.1.'): return 'FACULTY'
        if ip.startswith('10.0.2.'): return 'STUDENT'
        if ip.startswith('10.40.3.'): return 'IT'
        if ip.startswith('10.100.100.'): return 'DATACENTER'
        if ip == '10.0.203.6': return 'TRUSTED'
        if ip.startswith('10.0.198.'): return 'GUEST'
        return None

    # Extract IP packet
    ip_packet = packet.find('ipv4')
    if ip_packet is None:
        # Handle non-IP packets (ARP etc.)
        accept(of.OFPP_FLOOD)
        return

    # Get source and destination networks
    src_net = get_network(ip_packet.srcip)
    dst_net = get_network(ip_packet.dstip)

    # Determine protocol
    if packet.find('icmp'):
        # Rule 1: ICMP Traffic
        allowed_networks = ['STUDENT', 'FACULTY', 'IT']
        if src_net == dst_net:
            accept(packet_in.in_port)
        elif src_net in allowed_networks and dst_net in allowed_networks:
            accept(packet_in.in_port)
        else:
            drop()

    elif packet.find('tcp'):
        # Rule 2: TCP Traffic
        allowed_networks = ['DATACENTER', 'IT', 'FACULTY', 'STUDENT', 'TRUSTED']
        if src_net == dst_net:
            accept(packet_in.in_port)
        elif src_net in allowed_networks and dst_net in allowed_networks:
            # Special case: exam server access
            if dst_net == 'DATACENTER' and '10.100.100.2' in str(packet.dst):
                if src_net == 'FACULTY':
                    accept(packet_in.in_port)
                else:
                    drop()
            else:
                accept(packet_in.in_port)
        else:
            drop()

    elif packet.find('udp'):
        # Rule 3: UDP Traffic
        allowed_networks = ['DATACENTER', 'IT', 'FACULTY', 'STUDENT']
        if src_net == dst_net:
            accept(packet_in.in_port)
        elif src_net in allowed_networks and dst_net in allowed_networks:
            accept(packet_in.in_port)
        else:
            drop()

    else:
        # Rule 4: Drop all other traffic
        drop()
    
  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_routing(packet, packet_in, event.port, event.dpid)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Routing(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
