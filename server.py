import socket
import sys


#Create a Socket (connect two computers)
def create_socket():
    try:
        global host
        global port
        global s

        host = ""
        port = 9999
        s = socket.socket()
    
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

#Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s

        print("Binding port #" + str(port))
    
        s.bind(host, port)
        s.listen(5)

    except socket.error as msg:
            print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
            bind_socket()