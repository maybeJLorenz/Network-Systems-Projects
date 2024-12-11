import argparse
from socket import *
import select


## ======= References ==============
#   Week 8 Slides: select() pseudocode and functionality
#   docs.Python: select module function calls and reading more information
#
# ===================================


def handle_client(client_request, REG_clients, BRIDGE_clients, serverSocket, serverIP, serverPort, clientAddress, clientSocket):
    try:
        if client_request:
            lines = client_request.split("\r\n")
            request_type = lines[0]

            client_id = ''
            server_ip = ''
            client_port = ''

            for line in lines[1:]:
                if line.startswith("clientID:"):
                    client_id = line.split(":")[1].strip()
                elif line.startswith("IP:"):
                    server_ip = line.split(":")[1].strip()
                elif line.startswith("Port:"):
                    client_port = line.split(":")[1].strip()


            if request_type == "REGISTER":
                if client_id not in REG_clients:
                    
                    REG_clients[client_id] = lines[3]

                    print(f"REGISTER: {client_id} from {clientAddress[0]}:{client_port} received")
                    serverMessage = f"REGACK\r\n{lines[1]}\r\n{lines[2]}\r\n{lines[3]}\r\nStatus: registered\r\n\r\n"
                    clientSocket.send(serverMessage.encode())
                    clientSocket.close()
                    return serverMessage
            
            elif request_type == "BRIDGE":

                if (client_id in REG_clients) and (client_id not in BRIDGE_clients):
                    
                    peer_client_port = None
                    peer_client_name = None
                    curr_client_port = REG_clients[client_id]
                    curr_client_port = curr_client_port.replace("Port: ", "")
                    BRIDGE_clients[client_id] = curr_client_port

                    for key, value in REG_clients.items():
                        if key != client_id:
                            peer_client_port = REG_clients[client_id]
                            peer_client_name = key
                            break
                    
                    if len(BRIDGE_clients) == 1:
                        serverMessage = f"BRIDGEACK\r\nclientID:\r\nIP:\r\nPort: \r\n\r\n"
                    else:
                        serverMessage = f"BRIDGEACK\r\nclientID: {peer_client_name}\r\nIP: {clientAddress[0]}\r\n{peer_client_port}\r\n\r\n"

                    if len(BRIDGE_clients) == 1:
                        print(f"BRIDGE: {client_id} {serverIP}:{curr_client_port}")

                    else:
                        peer_client_port = BRIDGE_clients[peer_client_name]
                        print(f"BRIDGE: {client_id} {serverIP}:{curr_client_port} {peer_client_name} {serverIP}:{peer_client_port}")

                    
                    clientSocket.send(serverMessage.encode())
                    clientSocket.close()
                    return serverMessage

            
            
            ## ============== START OF CHAT FUNCTION =====================
            elif request_type == "CHAT":
                if len(REG_clients) == 2 and len(BRIDGE_clients) == 2:

                    for key, value in REG_clients.items():
                        if key != client_id:
                            peer_client_port = REG_clients[client_id]
                            peer_client_name = key
                            break
                    
                    peer_client_ip, peer_client_port = clientAddress

                    serverMessage = f"CHAT_ACK\r\n{peer_client_ip}\r\n{peer_client_port}\r\n\r\n"
                    clientSocket.send(serverMessage.encode())
                    
                    socket_list = [serverSocket]
                    clients = {}

                    while True:
                        readable, _, _ = select.select(socket_list, [], [])

                        for s in readable:
                            if s is serverSocket:
                                
                                connectionSocket, addr = serverSocket.accept()
                                if len(socket_list) - 1 < 2:  
                                    socket_list.append(connectionSocket)
                                    clients[connectionSocket] = addr
                                    print(f"Client {addr} connected.")
                                else:
                                    print(f"Rejected connection from {addr}.")
                                    connectionSocket.close()
                            else:
                                
                                try:
                                    message = s.recv(1024).decode()
                                    if not message: 
                                        print(f"Client {clients[s]} disconnected.")
                                        socket_list.remove(s)
                                        del clients[s]
                                        s.close()
                                        exit(0)
                                    else:
                                        print(f"Received from {clients[s]}: {message}")
                                        # Forwarding message to peer client
                                        for client_socket in socket_list:
                                            if client_socket != serverSocket and client_socket != s:
                                                client_socket.send(f"Message from {clients[s]}: {message}".encode())
                                except:
                                    print(f"Error with client {clients[s]}")
                                    socket_list.remove(s)
                                    del clients[s]
                                    s.close()
            ##============ END OF CHAT FUNCTION ====================
            
            elif request_type == "QUIT":
                serverMessage = f"Terminating Chat Program from quit"
                clientSocket.send(serverMessage.encode())
                clientSocket.close()
                serverSocket.close()
            
            else:
                serverMessage = f"nothing to say.."
                clientSocket.send(serverMessage.encode())

    except KeyboardInterrupt:
        print("\nTerminating Chat Program")
    except Exception as e:
        print(f"An error occurred: {e}")


#=============================================
#  
#             ---- MAIN FUNCTION ---- 
#
#==========================================
def main():

    
    REG_clients = {}   ## storing ID's and Ports of registered clients
    BRIDGE_clients = {} ## storing ID's and Port of bridged clients

    # parsing server arguments
    parser = argparse.ArgumentParser(description="Chat server program")
    parser.add_argument("--port", type=int, required=True, help="Server port")
    
    args = parser.parse_args()
    server_port = args.port # -------- getting server port number
    server_port = int(server_port)
    
    hostname = gethostname()
    server_ip = gethostbyname(hostname) # ------ getting server IP
    print(f"Server is listening on {server_ip}:{server_port}")
    
    # Preparing Server connection
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((server_ip, server_port)) # -------- establishing server connection
    serverSocket.listen(2)
    
    try:
        while True:
            clientSocket, clientAddress = serverSocket.accept() # ---- getting client socket + port
            client_request = clientSocket.recv(1024).decode()
            handle_client(client_request, REG_clients, BRIDGE_clients, serverSocket, server_ip, server_port, clientAddress, clientSocket)
            

    except KeyboardInterrupt:
        print("\nTerminating Chat Program")
    except Exception as e:
        print(f"An error occurred: {e}")
    

if __name__ == "__main__":
    main()
