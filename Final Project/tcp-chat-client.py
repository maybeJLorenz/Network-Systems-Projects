import socket
import argparse
import sys

class ChatClient:
    def __init__(self, client_id, server_addr, server_port, client_port):
        """
        Initialize the chat client with given parameters
        
        :param client_id: Unique identifier for the client
        :param server_addr: IP address of the server
        :param server_port: Port number of the server
        :param client_port: Port number the client will listen on
        """
        self.client_id = client_id
        self.server_addr = server_addr
        self.server_port = server_port
        self.client_port = client_port
        
        # Client socket for communication with server
        self.server_socket = None
        
        # Client socket for listening
        self.listening_socket = None
        
    def create_server_connection(self):
        """
        Create a TCP socket connection to the server
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.server_addr, self.server_port))
            print(f"Connected to server {self.server_addr}:{self.server_port}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            sys.exit(1)
    
    def send_register_request(self):
        """
        Send REGISTER request to the server
        """
        try:
            # Get local IP address
            local_ip = socket.gethostbyname(socket.gethostname())
            
            # Construct REGISTER message
            register_msg = (
                f"REGISTER\r\n"
                f"clientID: {self.client_id}\r\n"
                f"IP: {local_ip}\r\n"
                f"Port: {self.client_port}\r\n\r\n"
            )
            
            # Send registration request
            self.server_socket.send(register_msg.encode())
            
            # Wait for REGACK
            response = self.server_socket.recv(1024).decode()
            print("Server Response:", response)
        except Exception as e:
            print(f"Registration error: {e}")
    
    def send_bridge_request(self):
        """
        Send BRIDGE request to the server
        """
        try:
            # Construct BRIDGE message
            bridge_msg = (
                f"BRIDGE\r\n"
                f"clientID: {self.client_id}\r\n\r\n"
            )
            
            # Send bridge request
            self.server_socket.send(bridge_msg.encode())
            
            # Wait for BRIDGEACK
            response = self.server_socket.recv(1024).decode()
            print("Bridge Response:", response)
        except Exception as e:
            print(f"Bridge request error: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="TCP Chat Client")
    parser.add_argument("--id", required=True, help="Client ID")
    parser.add_argument("--port", type=int, required=True, help="Client listening port")
    parser.add_argument("--server", required=True, help="Server IP:Port")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate server argument
    try:
        server_ip, server_port = args.server.split(':')
        server_port = int(server_port)
    except ValueError:
        print("Error: Invalid server argument. Use format: IP:Port")
        sys.exit(1)
    
    # Validate port
    if not (1024 <= args.port <= 65535):
        print("Error: Invalid port number. Use a port between 1024 and 65535.")
        sys.exit(1)
    
    # Create client instance
    client = ChatClient(
        client_id=args.id, 
        server_addr=server_ip, 
        server_port=server_port, 
        client_port=args.port
    )
    
    # Establish server connection
    client.create_server_connection()
    
    # Run indefinitely
    while True:
        try:
            # Get input
            user_input = input("Enter command (/id, /register, /bridge, /quit): ").strip()
            
            # Process input
            if user_input == "/id":
                print(f"User ID: {client.client_id}")
            elif user_input == "/register":
                client.send_register_request()
            elif user_input == "/bridge":
                client.send_bridge_request()
            elif user_input == "/quit":
                break
            else:
                print("Error: Invalid input. Please use /id, /register, /bridge, or /quit.")
        
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            break
    
    # Terminate program
    if client.server_socket:
        client.server_socket.close()
    print("Client terminated.")

if __name__ == "__main__":
    main()
