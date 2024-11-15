from pox.core import core
import pox.openflow.libopenflow_01 as of
import ipaddress

log = core.getLogger()

class Routing(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        
        # Pre-define IP networks
        self.faculty_subnet = ipaddress.ip_network("10.0.1.0/24")
        self.student_subnet = ipaddress.ip_network("10.0.2.0/24")
        self.it_subnet = ipaddress.ip_network("10.40.3.0/24")
        self.university_subnet = ipaddress.ip_network("10.100.100.0/24")
        
        # Define host IPs and ports for faculty subnet
        self.faculty_hosts = {
            "10.0.1.2": 1,  # facultyWS
            "10.0.1.3": 3,  # printer
            "10.0.1.4": 4   # facultyPC
        }
        
        # Other host IPs
        self.examServer_ip = ipaddress.ip_address("10.100.100.2")
        self.webServer_ip = ipaddress.ip_address("10.100.100.20")
        self.dnsServer_ip = ipaddress.ip_address("10.100.100.56")
        self.trustedPC_ip = ipaddress.ip_address("10.0.203.6")
        self.guest1_ip = ipaddress.ip_address("10.0.198.6")
        self.guest2_ip = ipaddress.ip_address("10.0.198.10")

    def accept(self, packet, packet_in, end_port):
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = 30
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port=end_port))
        msg.data = packet_in
        self.connection.send(msg)
        log.debug("Packet accepted - forwarding to port %s", end_port)

    def drop(self, packet):
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = 30
        msg.hard_timeout = 30
        self.connection.send(msg)
        log.debug("Packet dropped")

    def is_in_subnet(self, ip, subnet):
        return ipaddress.ip_address(ip) in subnet

    def handle_faculty_switch(self, packet, packet_in, ip_header):
        dst_ip = str(ip_header.dstip)
        
        # If destination is in faculty subnet, forward to correct port
        if dst_ip in self.faculty_hosts:
            self.accept(packet, packet_in, self.faculty_hosts[dst_ip])
            return True
        # If destination is outside faculty subnet, forward to core switch
        else:
            self.accept(packet, packet_in, 2)
            return True
        return False

    def handle_core_switch(self, packet, packet_in, port_on_switch, ip_header, icmp_header, tcp_header, udp_header):
        src_ip = ip_header.srcip
        dst_ip = ip_header.dstip

        # ICMP Rules (Rule 1)
        if icmp_header:
            # Allow ICMP within same subnet
            if self.is_in_subnet(src_ip, self.faculty_subnet) and self.is_in_subnet(dst_ip, self.faculty_subnet):
                self.accept(packet, packet_in, 2)  # Forward to faculty switch
                return
                
            # Allow ICMP between Faculty, Student, and IT subnets
            src_allowed = (self.is_in_subnet(src_ip, self.faculty_subnet) or 
                         self.is_in_subset(src_ip, self.student_subnet) or 
                         self.is_in_subnet(src_ip, self.it_subnet))
            dst_allowed = (self.is_in_subnet(dst_ip, self.faculty_subnet) or 
                         self.is_in_subnet(dst_ip, self.student_subnet) or 
                         self.is_in_subnet(dst_ip, self.it_subnet))
            
            if src_allowed and dst_allowed:
                if self.is_in_subnet(dst_ip, self.faculty_subnet):
                    self.accept(packet, packet_in, 2)
                elif self.is_in_subnet(dst_ip, self.student_subnet):
                    self.accept(packet, packet_in, 3)
                elif self.is_in_subnet(dst_ip, self.it_subnet):
                    self.accept(packet, packet_in, 4)
                return

            self.drop(packet)
            return

        # Rest of the code remains the same...
        # (TCP and UDP handling code)

    def do_routing(self, packet, packet_in, port_on_switch, switch_id):
        ip_header = packet.find('ipv4')
        if not ip_header:
            self.drop(packet)
            return

        icmp_header = packet.find('icmp')
        tcp_header = packet.find('tcp')
        udp_header = packet.find('udp')

        if switch_id == 1:  # Core switch
            self.handle_core_switch(packet, packet_in, port_on_switch, ip_header, icmp_header, tcp_header, udp_header)
        elif switch_id == 2:  # Faculty switch
            if not self.handle_faculty_switch(packet, packet_in, ip_header):
                self.drop(packet)
        else:  # Other edge switches (s3-s5)
            dst_ip = ip_header.dstip
            # Forward to appropriate host port or back to core switch
            if switch_id == 3:  # Student switch
                if self.is_in_subnet(dst_ip, self.student_subnet):
                    self.accept(packet, packet_in, port_on_switch)
                else:
                    self.accept(packet, packet_in, 3)  # Back to core
            elif switch_id == 4:  # IT switch
                if self.is_in_subnet(dst_ip, self.it_subnet):
                    self.accept(packet, packet_in, port_on_switch)
                else:
                    self.accept(packet, packet_in, 4)  # Back to core
            elif switch_id == 5:  # University switch
                if self.is_in_subnet(dst_ip, self.university_subnet):
                    self.accept(packet, packet_in, port_on_switch)
                else:
                    self.accept(packet, packet_in, 5)  # Back to core

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        self.do_routing(packet, event.ofp, event.port, event.dpid)

def launch():
    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Routing(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
