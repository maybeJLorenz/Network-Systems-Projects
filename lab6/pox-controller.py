from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()

class NetworkController(object):
    def __init__(self):
        core.openflow.addListeners(self)
        
    def _handle_ConnectionUp(self, event):
        log.info("Switch %s has connected.", dpid_to_str(event.dpid))
        
    def drop(self, event):
        msg = of.ofp_flow_mod()
        msg.match = event.match
        msg.idle_timeout = 30
        msg.hard_timeout = 30
        msg.buffer_id = event.ofp.buffer_id
        event.connection.send(msg)
        
    def accept(self, event, end_port):
        msg = of.ofp_flow_mod()
        msg.match = event.match
        msg.idle_timeout = 30
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port=end_port))
        msg.buffer_id = event.ofp.buffer_id
        event.connection.send(msg)
    
    def is_same_subnet(self, ip1, ip2):
        # Define subnet masks
        subnets = {
            '10.100.100.': 'university',
            '10.40.3.': 'it',
            '10.0.1.': 'faculty',
            '10.0.2.': 'student'
        }
        
        for subnet_prefix in subnets:
            if ip1.startswith(subnet_prefix) and ip2.startswith(subnet_prefix):
                return True
        return False
    
    def get_subnet_type(self, ip):
        if ip.startswith('10.100.100.'): return 'university'
        if ip.startswith('10.40.3.'): return 'it'
        if ip.startswith('10.0.1.'): return 'faculty'
        if ip.startswith('10.0.2.'): return 'student'
        if ip == '10.0.203.6': return 'trusted'
        if ip.startswith('10.0.198.'): return 'guest'
        return None

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp
        ip_packet = packet.find('ipv4')
        
        if not ip_packet:
            self.drop(event)
            return

        src_ip = str(ip_packet.srcip)
        dst_ip = str(ip_packet.dstip)
        
        # Get source and destination subnet types
        src_subnet = self.get_subnet_type(src_ip)
        dst_subnet = self.get_subnet_type(dst_ip)
        
        if src_subnet is None or dst_subnet is None:
            self.drop(event)
            return
            
        # Rule 1: ICMP Traffic
        if ip_packet.protocol == 1:  # ICMP
            allowed = False
            if self.is_same_subnet(src_ip, dst_ip):
                allowed = True
            elif src_subnet in ['student', 'faculty', 'it'] and dst_subnet in ['student', 'faculty', 'it']:
                allowed = True
            
            if allowed:
                self.accept(event, event.port)
            else:
                self.drop(event)
            return
            
        # Rule 2: TCP Traffic
        elif ip_packet.protocol == 6:  # TCP
            allowed = False
            
            # Special case: exam server access
            if dst_ip == '10.100.100.2':  # exam server
                if src_subnet == 'faculty':
                    allowed = True
            else:
                if self.is_same_subnet(src_ip, dst_ip):
                    allowed = True
                elif (src_subnet in ['university', 'it', 'faculty', 'student', 'trusted'] and 
                      dst_subnet in ['university', 'it', 'faculty', 'student', 'trusted']):
                    allowed = True
            
            if allowed:
                self.accept(event, event.port)
            else:
                self.drop(event)
            return
            
        # Rule 3: UDP Traffic
        elif ip_packet.protocol == 17:  # UDP
            allowed = False
            if self.is_same_subnet(src_ip, dst_ip):
                allowed = True
            elif (src_subnet in ['university', 'it', 'faculty', 'student'] and 
                  dst_subnet in ['university', 'it', 'faculty', 'student']):
                allowed = True
            
            if allowed:
                self.accept(event, event.port)
            else:
                self.drop(event)
            return
            
        # Rule 4: Drop all other traffic
        else:
            self.drop(event)
            return

def launch():
    core.registerNew(NetworkController)
