# Lab5 Skeleton
#
#     Last Modified: november 7, 1:25pm
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

    facultyWS_ip = ipaddress.IPv4Address("10.0.1.2")
    printer_ip = ipaddress.IPv4Address("10.0.1.3")
    facultyPC_ip = ipaddress.IPv4Address("10.0.1.4")

    studentPC1_ip = ipaddress.IPv4Address("10.0.2.2")
    studentPC2_ip = ipaddress.IPv4Address("10.0.2.3")
    labWS_ip = ipaddress.IPv4Address("10.0.2.40")

    itWS_ip = ipaddress.IPv4Address("10.40.3.30")
    itPC_ip = ipaddress.IPv4Address("10.40.3.254")

    trustedPC_ip = ipaddress.IPv4Address("10.0.203.6") 
    exam_server_ip = ipaddress.IPv4Address("10.100.100.2")

    

    # port_on_switch - the port on which this packet was received
    # switch_id - the switch which received this packet

    # Rule #1: icmp between Student Housing, Faculty, and IT Dep. 
    #    NO: Univeristy or Internet subnet 

    if ip_header:
      src_ip = ip_header.srcip
      dst_ip = ip_header.dstip

    if switch_id == 1 and icmp_header:
      if dst_ip in faculty_subnet:
         accept(2)
         return
      if dst_ip in student_subnet:
         accept(3)
         return
      if dst_ip in it_subnet:
         accept(4)
         return

    if switch_id == 2 and icmp_header: # inside faculty switch (s2)
      if dst_ip == facultyWS_ip:
        accept(1)
        return
      elif dst_ip == printer_ip:
        accept(3)
        return
      elif dst_ip == facultyPC_ip:
        accept(4)
        return
      else:
         accept(2)
         return
      
    
    if switch_id == 3 and icmp_header: # inside student switch (s3)
      if dst_ip == studentPC1_ip:
        accept(1)
        return
      
      if dst_ip == labWS_ip:
        accept(2)
        return
      
      if dst_ip == studentPC2_ip:
        accept(4)
        return

    if switch_id == 4 and icmp_header: # inside IT switch (s4)
      if dst_ip == itWS_ip:
        accept(1)
        return
      
      if dst_ip == itPC_ip:
        accept(2)
        return
      
        
    # Rule #2: tcp between University, IT Dep, Faculty, Student Housing, and trustedPC
    #       - NO: Internet subnet
    #       - Only Faculty LAN may access exam server
    if tcp_header and ip_header:
        src_ip = ipaddress.IPv4Address(ip_header.srcip)
        dst_ip = ipaddress.IPv4Address(ip_header.dstip)

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
        src_ip = ipaddress.IPv4Address(ip_header.srcip)
        dst_ip = ipaddress.IPv4Address(ip_header.dstip)

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
