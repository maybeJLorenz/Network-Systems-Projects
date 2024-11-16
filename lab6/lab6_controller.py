# Lab6
#
#     Last Modified: november 15, 6:40pm
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
        if ip.startswith('10.0.198.'): return 'GUEST'  # Will be blocked in traffic rules
        if ip == '10.0.123.3': return 'DISCORD' # added discord server
        return None

    # Get destination port based on IP and switch
    def get_destination_port(switch_id, dst_ip):
        if switch_id == 1:  # Core switch (s1)
            if str(dst_ip).startswith('10.0.1.'): return 2  # To Faculty
            if str(dst_ip).startswith('10.0.2.'): return 3  # To Student
            if str(dst_ip).startswith('10.40.3.'): return 4  # To IT
            if str(dst_ip).startswith('10.100.100.'): return 5  # To Data Center
            if str(dst_ip) == '10.0.203.6': return 1  # To trustedPC
            if str(dst_ip) == '10.0.123.3': return 8 # To discord Server (dServer)
            # Removed guest forwarding ports since they're blocked
        
        elif switch_id == 2:  # Faculty switch (s2)
            if str(dst_ip) == '10.0.1.2': return 1  # To facultyWS
            if str(dst_ip) == '10.0.1.3': return 3  # To printer
            if str(dst_ip) == '10.0.1.4': return 4  # To facultyPC
            return 2  # Default return to core switch
        
        elif switch_id == 3:  # Student switch (s3)
            if str(dst_ip) == '10.0.2.2': return 1  # To studentPC1
            if str(dst_ip) == '10.0.2.40': return 2  # To studentPC2
            if str(dst_ip) == '10.0.2.3': return 4  # To labWS
            return 3  # Default return to core switch
        
        elif switch_id == 4:  # IT switch (s4)
            if str(dst_ip) == '10.40.3.30': return 1  # To itWS
            if str(dst_ip) == '10.40.3.254': return 2  # To itPC
            return 4  # Default return to core switch
        
        elif switch_id == 5:  # Data Center switch (s5)
            if str(dst_ip) == '10.100.100.2': return 1  # To examServer
            if str(dst_ip) == '10.100.100.20': return 2  # To webServer
            if str(dst_ip) == '10.100.100.56': return 3  # To dnsServer
            return 5  # Default return to core switch

    # Extract IP packet
    ip_packet = packet.find('ipv4')
    if ip_packet is None:
        # Handle non-IP packets (ARP etc.)
        accept(of.OFPP_FLOOD)
        return

    # Get source and destination networks
    src_net = get_network(ip_packet.srcip)
    dst_net = get_network(ip_packet.dstip)

    # Block all guest traffic immediately
    if src_net == 'GUEST' or dst_net == 'GUEST':
        drop()
        return
    
    dServer_ip = '10.0.123.3'
    if str(ip_packet.dstip) == dServer_ip:
        if src_net == 'STUDENT':
            output_port = get_destination_port(switch_id, ip_packet.dstip)
            accept(output_port)
        else:
            drop()
        return

    # Get the appropriate output port
    output_port = get_destination_port(switch_id, ip_packet.dstip)

    # Handle traffic based on protocol
    if packet.find('icmp'):
        # Rule 1: ICMP Traffic
        allowed_networks = ['STUDENT', 'FACULTY', 'IT', 'DISCORD']
        dnet = ['DISCORD']
        if src_net == dst_net or (src_net in allowed_networks and dst_net in allowed_networks):
            if dst_net in dnet and '10.0.123.3' in str(packet.dst):
                if src_net == 'STUDENT':
                    accept(output_port)
                else:
                    drop()
            else:
                accept(output_port)
        else:
            drop()

    elif packet.find('tcp'):
        # Rule 2: TCP Traffic
        allowed_networks = ['DATACENTER', 'IT', 'FACULTY', 'STUDENT', 'TRUSTED', 'DISCORD']
        dnet = ['DISCORD']
        if src_net == dst_net or (src_net in allowed_networks and dst_net in allowed_networks):
            # Special case: exam server access
            if dst_net == 'DATACENTER' and '10.100.100.2' in str(packet.dst):
                if src_net == 'FACULTY':
                    accept(output_port)
                else:
                    drop()
            if dst_net in dnet and '10.0.123.3' in str(packet.dst):
                if src_net == 'STUDENT':
                    accept(output_port)
                else:
                    drop()
            else:
                accept(output_port)
        else:
            drop()

    elif packet.find('udp'):
        # Rule 3: UDP Traffic
        allowed_networks = ['DATACENTER', 'IT', 'FACULTY', 'STUDENT', 'DISCORD']
        dnet = ['DISCORD']
        if src_net == dst_net or (src_net in allowed_networks and dst_net in allowed_networks):
            if dst_net in dnet and '10.0.123.3' in str(packet.dst):
                if src_net == 'STUDENT':
                    accept(output_port)
                else:
                    drop()
            else:
                accept(output_port)
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
