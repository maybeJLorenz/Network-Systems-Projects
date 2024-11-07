
# Lab5 Skeleton
#
#     Last Modified: november 6, 9:45pm
# 

from pox.core import core
import pox.openflow.libopenflow_01 as of
from netaddr import *

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
      msg.actions.append(of.ofp_action_output(port=1)) ## all ending ports (hosts) are 1
      msg.buffer_id = packet_in.buffer_id
      self.connection.send(msg)
      print("Packet Accepted - Flow Table Installed on Switches")
    
    def drop():
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      print("Packet Dropped - Flow Table Installed on Switches")
    
    ## Primary variables for packets
    ip_header = packet.find('ipv4')
    tcp_header = packet.find('tcp')
    udp_header = packet.find('udp')
    icmp_header = packet.find('icmp')
    
    faculty_subnet = "10.0.1.0/24"
    student_subnet = "10.0.2.0/24"
    it_subnet = "10.40.3.0/24"
    university_subnet = "10.100.100.0/24"

        
    trustedPC_ip = IPAddress("10.0.203.6/32") 
    exam_server_ip = IPAddress("10.100.100.2/24")


    # port_on_switch - the port on which this packet was received
    # switch_id - the switch which received this packet

    # Rule #1: icmp between Student Housing, Faculty, and IT Dep. 
    #    NO: Univeristy or Internet subnet 
    allowed_r1 = [faculty_subnet, student_subnet, it_subnet]

    if icmp_header and ip_header:
        src_ip = IPAddress(ip_header.srcip)
        dst_ip = IPAddress(ip_header.dstip)
        
        for subnet in allowed_r1:
            if src_ip in subnet and dst_ip in subnet:
                accept()
                return
      
        
    # Rule #2: tcp between University, IT Dep, Faculty, Student Housing, and trustedPC
    #       - NO: Internet subnet
    #       - Only Faculty LAN may access exam server
    if tcp_header and ip_header:
        src_ip = IPAddress(ip_header.srcip)
        dst_ip = IPAddress(ip_header.dstip)

        allowed_r2 = [university_subnet, it_subnet, faculty_subnet, student_subnet]
        for subnet in allowed_r2:
            if src_ip in subnet and dst_ip in subnet:
                accept()
                return
                
        # faculty LAN has access  exam server
        if src_ip in faculty_subnet and dst_ip == exam_server_ip:
            accept()
            return

        if src_ip == trustedPC_ip or dst_ip == trustedPC_ip:
            if any([src_ip in subnet or dst_ip in subnet for subnet in allowed_r2]):
                accept()
                return
                
    # # Rule #3: udp between University, IT Dep, Faculty, and Student Housing
    # #       - NO: Internet subnet
    if udp_header and ip_header:
        src_ip = IPAddress(ip_header.srcip)
        dst_ip = IPAddress(ip_header.dstip)

        allowed_r3 = [university_subnet, it_subnet, faculty_subnet, student_subnet]
        for subnet in allowed_r3:
            if src_ip in subnet and dst_ip in subnet:
                accept()
                return

    # Rule #4: all other traffic is dropped
    drop()
    return
    

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
