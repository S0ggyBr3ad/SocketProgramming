import socket
import sys

def create_socket():
    try:
        global host
        global port
        global s
        host = "127.0.0.1"  # Server IP or hostname
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

def connect_to_server():
    try:
        s.connect((host, port))
        print(f"Connected to server at {host}:{port}")
    except socket.error as msg:
        print("Connection error: " + str(msg))
        sys.exit()

def receive_commands():
    while True:
        try:
            data = s.recv(1024).decode("utf-8")
            if len(data) > 0:
                print(f"Server: {data}")
                cmd = input("Enter response: ")
                if cmd.lower() == "quit":
                    s.close()
                    sys.exit("Disconnected from server.")
                s.send(cmd.encode())
        except socket.error as msg:
            print("Error receiving data: " + str(msg))
            break

def main():
    create_socket()
    connect_to_server()
    receive_commands()

if __name__ == "__main__":
    main()
