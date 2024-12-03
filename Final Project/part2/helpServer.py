import argparse
import socket
import threading
import logging

class ChatServer:
    def __init__(self, host, port):
        """Initialize the chat server with logging and client tracking."""
        self.host = host
        self.port = port
        self.clients = {}  # Store registered clients
        self.server_socket = None
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start the server and begin accepting client connections."""
        try:
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.logger.info(f"Server listening on {self.host}:{self.port}")
            
            while True:
                # Accept incoming client connections
                client_socket, client_address = self.server_socket.accept()
                client_handler = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, client_address)
                )
                client_handler.start()
        
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        """Handle individual client connections and requests."""
        try:
            # Receive client message
            message = client_socket.recv(1024).decode().strip()
            lines = message.split("\r\n")
            
            if not lines:
                return
            
            request_type = lines[0]
            client_info = {}
            
            # Parse client information from message
            for line in lines[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    client_info[key.strip()] = value.strip()
            
            # Handle different request types
            if request_type == "REGISTER":
                self.handle_registration(client_socket, client_info)
            elif request_type == "BRIDGE":
                self.handle_bridge_request(client_socket, client_info)
            elif request_type == "CHAT":
                self.handle_chat_request(client_socket, client_info)
            else:
                self.send_error_response(client_socket, "Invalid request type")
        
        except Exception as e:
            self.logger.error(f"Client handling error: {e}")
        finally:
            client_socket.close()

    def handle_registration(self, client_socket, client_info):
        """Process client registration."""
        client_id = client_info.get('clientID')
        if client_id:
            self.clients[client_id] = client_info
            response = f"REGACK\r\nclientID:{client_id}\r\nStatus:registered\r\n\r\n"
            client_socket.send(response.encode())
            self.logger.info(f"Registered client: {client_id}")
        else:
            self.send_error_response(client_socket, "Invalid registration")

    def handle_bridge_request(self, client_socket, client_info):
        """Handle bridge request between clients."""
        client_id = client_info.get('clientID')
        if client_id and client_id in self.clients:
            response = f"BRIDGEACK\r\nclientID:{client_id}\r\n"
            client_socket.send(response.encode())
            self.logger.info(f"Bridge request processed for: {client_id}")
        else:
            self.send_error_response(client_socket, "Client not registered")

    def handle_chat_request(self, client_socket, client_info):
        """Process chat requests between clients."""
        client_id = client_info.get('clientID')
        if client_id and client_id in self.clients:
            response = f"CHAT_READY\r\nclientID:{client_id}\r\n\r\n"
            client_socket.send(response.encode())
            self.logger.info(f"Chat request received from: {client_id}")
        else:
            self.send_error_response(client_socket, "Cannot process chat request")

    def send_error_response(self, client_socket, error_message):
        """Send standardized error response."""
        response = f"ERROR\r\nMessage:{error_message}\r\n\r\n"
        client_socket.send(response.encode())
        self.logger.warning(f"Sent error response: {error_message}")

def main():
    parser = argparse.ArgumentParser(description="Chat Server")
    parser.add_argument("--port", type=int, required=True, help="Server port number")
    args = parser.parse_args()

    # Get local IP address
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)

    # Create and start server
    server = ChatServer(server_ip, args.port)
    server.start()

if __name__ == "__main__":
    main()
