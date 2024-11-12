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

    
    ## Primary variables for packets
    ip_header = packet.find('ipv4')
    tcp_header = packet.find('tcp')
    udp_header = packet.find('udp')
    icmp_header = packet.find('icmp')


    # Subnets
    faculty_subnet = ipaddress.ip_network("10.0.1.0/24")
    student_subnet = ipaddress.ip_network("10.0.2.0/24")
    it_subnet = ipaddress.ip_network("10.40.3.0/24")
    university_subnet = ipaddress.ip_network("10.100.100.0/24")
    internet_subnet = ipaddress.ip_network("10.0.198.0/32")


    # IP Addresses
      ## Faculty Addresses
    facultyWS_ip = ipaddress.ip_address("10.0.1.2")
    printer_ip = ipaddress.ip_address("10.0.1.3")
    facultyPC_ip = ipaddress.ip_address("10.0.1.4")

      ## Student Addresses
    studentPC1_ip = ipaddress.ip_address("10.0.2.2")
    studentPC2_ip = ipaddress.ip_address("10.0.2.3")
    labWS_ip = ipaddress.ip_address("10.0.2.40")

      ## IT Addresses
    itWS_ip = ipaddress.ip_address("10.40.3.30")
    itPC_ip = ipaddress.ip_address("10.40.3.254")

      ## University Addresses
    examServer_ip = ipaddress.ip_address("10.100.100.2")
    webServer_ip = ipaddress.ip_address("10.100.100.20")
    dnsServer_ip = ipaddress.ip_address("10.100.100.56")

      ## Internet Addresses
    trustedPC_ip = ipaddress.ip_address("10.0.203.6") 
    guest1_ip = ipaddress.ip_address("10.0.198.6")
    guest2_ip = ipaddress.ip_address("10.0.198.10")

    # port_on_switch - the port on which this packet was received
    # switch_id - the switch which received this packet

    # NOTE - Rule #1: icmp between Student Housing, Faculty, and IT Dep. 
    #    NO: Univeristy or Internet subnet 
    
    src_ip = ip_header.srcip
    dst_ip = ip_header.dstip


    ## packet is in Core Switch (s1)
    if switch_id == 1:
      if icmp_header: ## NOTE ======== start of RULE 1 ============
        if not (src_ip in university_subnet and dst_ip in university_subnet): ## DROP if icmp packet src and dst are not in University subnet
          drop()
          return
        if not (src_ip in internet_subnet and dst_ip in internet_subnet): ## DROP if icmp packet src and dst are not in Internet subnet
          drop()
          return
        if port_on_switch in [1, 2, 3, 4, 5, 6, 7]:
          if dst_ip in faculty_subnet:
            accept(2)
            return
          elif dst_ip in student_subnet:
            accept(3)
            return
          elif dst_ip in it_subnet:
            accept(4)
            return
          elif src_ip in university_subnet and dst_ip in university_subnet:
            accept(5)
            return
          elif src_ip in internet_subnet and dst_ip in internet_subnet:
            if dst_ip == guest1_ip:
              accept(7)
              return
            elif dst_ip == guest2_ip:
              accept(6)
              return
            elif dst_ip == trustedPC_ip:
              accept(1)
              return
        else:
          drop()
          return
        
      if tcp_header: #NOTE ========== start of RULE 2 =============
        if dst_ip == trustedPC_ip: ## ACCEPT all packets to trustedPC
          accept(1)
          return
        if (src_ip == guest1_ip or src_ip == guest2_ip):
          if dst_ip not in internet_subnet:
            drop() ## DROP if guests try to send packet to different subnet
            return  
        elif src_ip in internet_subnet and dst_ip in internet_subnet:
            if dst_ip == guest1_ip:
              accept(7)
              return
            elif dst_ip == guest2_ip:
              accept(6)
              return
            elif dst_ip == trustedPC_ip:
              accept(1)
              return
        if dst_ip in faculty_subnet:
          accept(2)
          return
        if dst_ip in student_subnet:
          accept(3)
          return
        if dst_ip in it_subnet:
          accept(4)
          return
        if dst_ip not in university_subnet:
          accept(5)
          return
        else:
          drop()
          return
      
      if udp_header: ## NOTE - start rule 3 ==============
        if src_ip in internet_subnet and dst_ip in internet_subnet:
          if dst_ip == guest1_ip:
            accept(7)
            return
          elif dst_ip == guest2_ip:
            accept(6)
            return
          elif dst_ip == trustedPC_ip:
            accept(1)
            return
        elif dst_ip in faculty_subnet:
          accept(2)
          return
        elif dst_ip in university_subnet:
          accept(5)
          return
        elif dst_ip in it_subnet:
          accept(4)
          return
        elif dst_ip in student_subnet:
          accept(3)
          return
    ## NOTE - END OF SWITCH 1 CODE ========================


    ## ICMP packet is in Faculty Switch (s2), distribute to Faculty hosts
    if switch_id == 2 and icmp_header:
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
        accept(2) ## Go back to core switch
        return
      
    ## ICMP packet is in Student Switch (s3), distribute to Student hosts
    if switch_id == 3 and icmp_header:
      if dst_ip == studentPC1_ip:
        accept(1)
        return
      elif dst_ip == labWS_ip:
        accept(2)
        return
      elif dst_ip == studentPC2_ip:
        accept(4)
        return
      else:
        accept(3)
        return

    ## ICMP packet is in IT Switch (s3), distribute to IT hosts
    if switch_id == 4 and icmp_header:
      if dst_ip == itWS_ip:
        accept(1)
        return
      elif dst_ip == itPC_ip:
        accept(2)
        return
      else:
        accept(4)
        return
      
      ## ICMP packet is in University Switch (s5), distribute to University hosts
    if switch_id == 5 and icmp_header:
      if dst_ip == examServer_ip:
        accept(1)
        return
      if dst_ip == webServer_ip:
        accept(2)
        return
      if dst_ip == dnsServer_ip:
        accept(3)
        return
      else:
        accept(5)
        return
        

    # NOTE Rule #2: tcp between University, IT Dep, Faculty, Student Housing, and trustedPC
    #       - NO: Internet subnet
    #       - Only Faculty LAN may access exam server
    if switch_id == 2 and tcp_header: ## TCP packet in Faculty Switch, send to Faculty hosts
      if dst_ip == guest1_ip or dst_ip == guest2_ip:
        drop()
        return
      if dst_ip == facultyWS_ip:
        accept(1)
        return
      elif dst_ip == printer_ip:
        accept(3)
        return
      elif dst_ip == facultyPC_ip:
        accept(4)
        return
      elif dst_ip not in faculty_subnet:
        accept(2)
        return
    
    if switch_id == 3 and tcp_header: ## TCP packet in Student Switch, send to Student hosts
      if dst_ip == guest1_ip or dst_ip == guest2_ip:
        drop()
        return
      if dst_ip == studentPC1_ip:
        accept(1)
        return
      elif dst_ip == labWS_ip:
        accept(2)
        return
      elif dst_ip == studentPC2_ip:
        accept(4)
        return
      elif dst_ip not in student_subnet:
        accept(3)
        return 

    if switch_id == 4 and tcp_header: ## TCP packet in IT Switch, send to IT hosts
      if dst_ip == guest1_ip or dst_ip == guest2_ip:
        drop()
        return
      if dst_ip == itWS_ip:
        accept(1)
        return
      elif dst_ip == itPC_ip:
        accept(2)
        return
      elif dst_ip not in it_subnet:
        accept(4)
        return

    if switch_id == 5 and tcp_header: ## TCP packet in University Switch, send to University hosts
      if dst_ip == guest1_ip or dst_ip == guest2_ip:
        drop()
        return
      if (src_ip not in faculty_subnet) and dst_ip == examServer_ip:
        drop()
        return
      elif (src_ip in faculty_subnet and dst_ip == examServer_ip) or (src_ip in university_subnet and dst_ip in university_subnet):
        accept(1)
        return
      if dst_ip == webServer_ip:
        accept(2)
        return
      elif dst_ip == dnsServer_ip:
        accept(3)
        return
      elif dst_ip not in university_subnet:
        accept(5)
        return
    

    
    # # NOTE - Rule #3: udp between University, IT Dep, Faculty, and Student Housing
    # #       - NO: Internet subnet
    if switch_id == 2 and udp_header:
      if src_ip in internet_subnet or dst_ip in internet_subnet:
        drop()
        return
      if dst_ip == facultyWS_ip:
        accept(1)
        return
      elif dst_ip == printer_ip:
        accept(3)
        return
      elif dst_ip == facultyPC_ip:
        accept(4)
        return
      elif dst_ip not in faculty_subnet:
        accept(2)
        return
    

    if switch_id == 3 and udp_header:
      if src_ip in internet_subnet or dst_ip in internet_subnet:
        drop()
        return
      if dst_ip == studentPC1_ip:
        accept(1)
        return
      elif dst_ip == labWS_ip:
        accept(2)
        return
      elif dst_ip == studentPC2_ip:
        accept(4)
        return
      elif dst_ip not in student_subnet:
        accept(3)
        return 
    
    if switch_id == 4 and udp_header:
      if src_ip in internet_subnet or dst_ip in internet_subnet:
        drop()
        return
      if dst_ip == itWS_ip:
        accept(1)
        return
      elif dst_ip == itPC_ip:
        accept(2)
        return
      elif dst_ip not in student_subnet:
        accept(4)
        return 

    # NOTE - Rule #4: all other traffic is dropped
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
