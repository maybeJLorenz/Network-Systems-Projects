import argparse
from socket import *
import sys
import select
## ======= References ==============
#   Week 8 Slides: select() pseudocode and functionality
#   Project PDF: chat message format
#   docs.Python: select module function calls and reading more information
#
#
#
# ===================================
## =========== QUIT request function ================
def quit_request(server_ip, server_port, client_id, client_port):
    try:
        client_port = int(client_port)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((server_ip, server_port))
        message = f"QUIT\r\nMessage: {client_id} entered /quit\r\n\r\n"
        print(message)
        sock.send(message.encode())
        serverResponse = sock.recv(1024)
        
        sock.close()
        return serverResponse.decode()
    except ConnectionRefusedError:
        return "Connection refused for quit"
    except Exception as e:
        return f"Error: {str(e)}"
## ============ REGISTER request function ============
def register_request(server_ip, server_port, client_id, client_port):
    try:
        client_port = int(client_port)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((server_ip, server_port)) ## client socket uses this to connect to server
        message = f"REGISTER\r\nclientID: {client_id}\r\nIP: {server_ip}\r\nPort: {client_port}\r\n\r\n"
        print(message) 
        
        sock.send(message.encode()) ## send to server
        serverResponse = sock.recv(1024) ## recieve response from server
        
        sock.close()
        return serverResponse.decode()
    
    except ConnectionRefusedError:
        return "Connection refused for register"
    except Exception as e:
        return f"Error: {str(e)}"
## =========== BRIDGE request function ===================
def bridge_request(server_ip, server_port, client_id, client_port):
    try:
        client_port = int(client_port)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((server_ip, server_port))
        
        message = f"BRIDGE\r\nclientID: {client_id}\r\n\r\n"
        print(message)
        sock.send(message.encode())
        serverResponse = sock.recv(1024)
        
        sock.close()
        return serverResponse.decode()
    except ConnectionRefusedError:
        print("Connection refused for bridge.")
    except Exception as e:
        print(f"Error: {str(e)}")
def chat_request(server_ip, server_port, client_id, client_port):
    try:
        client_port = int(client_port)
        serverSock = socket(AF_INET, SOCK_STREAM)
        serverSock.connect((server_ip, server_port))
        
        message = f"CHAT\r\nclientID: {client_id}\r\nIP: {server_ip}\r\nPort: {client_port}\r\n\r\n"
        serverSock.send(message.encode())
        
        serverResponse = serverSock.recv(1024).decode()
        ## ===== closing ServerSocket, opening peerClientSocket =======
        # lines = serverResponse.split("\r\n")
        # serverSock.close()
        # peer_IP = lines[1]
        # peer_port = lines[2]
        
        # print(f" - - - Peer port: {peer_port}")
        # print(f"- - -  Peer IP: {peer_IP}")
        # peer_port = int(peer_port)
        
        # peer_sock = socket(AF_INET, SOCK_STREAM)
        # peer_sock.connect((peer_IP, peer_port))
        
        while True:
            
            readable, _, _ = select.select([serverSock, 0], [], [])
            for s in readable:
                if s == serverSock:
                    response = serverSock.recv(1024).decode() ## receive message from server
                    if not response:
                        print("Server got disconnected.")
                        return
                    print(f"\n{response}")
                else:  # getting client input to send to peer client
                    client_input = sys.stdin.readline().strip()
                    if client_input == "/quit":
                        print("Terminating chat program.")
                        serverSock.close()
                        exit(0)
                    serverSock.send(client_input.encode()) 
            
        
    except ConnectionRefusedError:
        print("Connection refused for chat.")
    except Exception as e:
        print(f"Error: {str(e)}")
#=============================================
#  
#             ---- MAIN FUNCTION ---- 
#
#==========================================
def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="Chat client program")
    parser.add_argument("--id", type=str, required=True, help="Client ID")
    parser.add_argument("--port", type=int, required=True, help="Client port")
    parser.add_argument("--server", type=str, required=True, help="Server IP and port")
    
    args = parser.parse_args()
    client_id = args.id
    client_port = args.port
    server = args.server
    server_ip, server_port = server.split(":")
    server_port = int(server_port)
    print(f"{client_id} running on {server}.")
    try:
        while True:
            command = sys.stdin.readline().strip()
            if command == "/id":
                print(f"clientID: {client_id}")
            
            elif command == "/register":
                response = register_request(server_ip, server_port, client_id, client_port)
                print(response)
            elif command == "/bridge":
                response = bridge_request(server_ip, server_port, client_id, client_port)
                print(response)
            
            elif command == "/chat":
                response = chat_request(server_ip, server_port, client_id, client_port)
                print(response)
            elif command == "/quit":
                response = quit_request(server_ip, server_port, client_id, client_port)
                print(response)
                exit(0)
            else:
                print("\nInvalid command. Use /id, /register, /bridge, or /quit.")
        
    except KeyboardInterrupt:
        print("\nTerminating Chat Program")
    except Exception as e:
        print(f"An error occurred: {e}")
if __name__ == "__main__":
    main()
