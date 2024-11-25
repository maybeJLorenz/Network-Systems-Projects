import argparse
from socket import *
import sys

## =========== QUIT request function ================
def quit_request(server_ip, server_port, client_id):
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((server_ip, server_port))
        serverSocket.listen(2)

        message = f"QUIT\r\nMessage: {client_id} entered /quit\r\n\r\n"

        serverSocket.send(message.encode())
        serverResponse = serverSocket.recv(1024)
        
        serverSocket.close()
        return serverResponse.decode()

    except ConnectionRefusedError:
        return "Connection refused"
    except Exception as e:
        return f"Error: {str(e)}"

## ============ REGISTER request function ============
def register_request(server_ip, server_port, client_id, client_port):
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((server_ip, server_port)) ## server socket uses "bind" to connect to client
        serverSocket.listen(2)

        # message = f"REGACK\r\nclientID: {client_id}\r\nIP: {server_ip}\r\nPort: {client_port}\r\n\r\n"
        message = f"REGISTER: {client_id} from {server_ip}:{client_port}"
        print(message)

        serverSocket.send(message.encode()) ## send to client
        serverResponse = serverSocket.recv(1024) ## recieve response from client
        
        serverSocket.close()
        return serverResponse.decode()
    
    except ConnectionRefusedError:
        return "Connection refused"
    except Exception as e:
        return f"Error: {str(e)}"

## =========== BRIDGE request function ===================
def bridge_request(server_ip, server_port, client_id, client_port):

    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((server_ip, server_port))
        socket.listen(2)
        
        message = f"BRIDGE: {client_id}"
        print(message)

        serverSocket.send(message.encode())
        serverResponse = serverSocket.recv(1024)
        
        serverSocket.close()
        return serverResponse.decode()

    except ConnectionRefusedError:
        print("Connection refused. Unable to reach server.")
    except Exception as e:
        print(f"Error: {str(e)}")

## ============= CHAT request function =================
def chat_request(client_ip, client_port, client_id, message):
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((client_ip, client_port))

        chat_message = f"Request Type: CHAT\r\nclientID: {client_id}\r\nmessage: {message}\r\n\r\n"
        serverSocket.send(message.encode())
        response = serverSocket.recv(1024)
        print("Peer response: ", response.decode())
        serverSocket.close
        return response.decode()



    except ConnectionRefusedError:
        print("Connection refused. Unable to reach server.")
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
    parser.add_argument("--port", type=int, required=True, help="Client port")
   
    
    args = parser.parse_args()
    server_port = args.port
    server_port = int(server_port)
    hostname = gethostname()
    server_ip = gethostbyname(hostname)
    print(f"Server listening on {server_ip}:{server_port}")

    ## Preparing Server connection
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', server_port))
    serverSocket.listen(1)

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((server_ip, server_port))
    message = sock.recv(1024)
    message = message.decode()

    print(message)
    print("hello")
    client1_id = ""
    client2_id = ""
    
    try:
        while True:
            if message == "REGISTER":
                response = register_request(server_ip, server_port, clientAddress)
                print(response)
                if client1_id == "":
                    client1_id = clientAddress
                else:
                    client2_id = clientAddress

            elif message == "BRIDGE":
                response = bridge_request(server_ip, server_port, client_id, client_port)
                print(response)
            
            elif message == "CHAT":
                response = chat_request(server_ip, server_port, client_id, client_port, server)
                while True:
                    connectionSocket, clientAddress = serverSocket.accept()
                    message = connectionSocket.recv(1024).decode()
                
                    request_type = message.encode()
                    clientIP, clientPort = clientAddress

                    connectionSocket.send(message.encode())
                    connectionSocket.close()

            elif message == "QUIT":
                response = quit_request(server_ip, server_port, client_id, client_port)
                print(response)
                exit(0)

            else:
                print("\nInvalid message. You entered ", {request_type})
                print("This is clientIP: ", {clientIP})
                print("This is clientPort: ", {clientPort})
        
    except KeyboardInterrupt:
        print("\nTerminating Chat Program")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
