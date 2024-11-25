import argparse
from socket import *
import sys

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
        return "Connection refused"
    except Exception as e:
        return f"Error: {str(e)}"

## ============ REGISTER request function ============
def register_request(server_ip, server_port, client_id, client_port):
    try:
        client_port = int(client_port)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((server_ip, server_port)) ## client socket uses this to connect to server

        message = f"REGISTER\r\nclientID: {client_id}\r\nIP: {server_ip}\r\nPort: {client_port}\r\n\r\n"
        # print(message) 
        
        sock.send(message.encode()) ## send to server
        serverResponse = sock.recv(1024) ## recieve response from server
        
        sock.close()
        return serverResponse.decode()
    
    except ConnectionRefusedError:
        return "Connection refused"
    except Exception as e:
        return f"Error: {str(e)}"

## =========== BRIDGE request function ===================
def bridge_request(server_ip, server_port, client_id, client_port):

    try:
        client_port = int(client_port)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((server_ip, server_port))
        
        message = f"BRIDGE\r\nclientID: {client_id}\r\n\r\n"
        # print(message)

        sock.send(message.encode())
        serverResponse = sock.recv(1024)
        
        sock.close()
        return serverResponse.decode()

    except ConnectionRefusedError:
        print("Connection refused. Unable to reach server.")
    except Exception as e:
        print(f"Error: {str(e)}")

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
                # print(response)

            elif command == "/bridge":
                response = bridge_request(server_ip, server_port, client_id, client_port)
                # print(response)
            
            elif command == "/chat":
                message = sys.stdin.readline().strip()
                if message:
                    response = chat_request(server_ip, server_port, client_id, client_port, message)
                    print("Chat started~")
                    print(response)

            elif command == "/quit":
                response = quit_request(server_ip, server_port, client_id, client_port)
                # print(response)
                exit(0)

            else:
                print("\nInvalid command. Use /id, /register, /bridge, or /quit.")
        
    except KeyboardInterrupt:
        print("\nTerminating Chat Program")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
