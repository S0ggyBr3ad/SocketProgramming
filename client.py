<<<<<<< HEAD
import socket
import sys
import os
import hashlib
import time
from analytics import NetworkAnalytics

analytics = NetworkAnalytics()  # Initialize the analytics module


def create_socket():
    try:
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket created.")
    except socket.error as msg:
        print("Socket creation error: " + str(msg))


def connect_to_server(host, port):
    try:
        s.connect((host, port))
        print("Connected to the server.")
    except socket.error as msg:
        print("Connection error: " + str(msg))
        sys.exit()


def authenticate():
    print(s.recv(1024).decode(), end="")
    username = input()
    username = hashlib.sha256(username.encode()).hexdigest()
    s.send(username.encode())

    print(s.recv(1024).decode(), end="")
    password = input()
    password = hashlib.sha256(password.encode()).hexdigest()

    s.send(password.encode())

    response = s.recv(1024).decode()
    print(response)
    if "Authentication successful" not in response:
        sys.exit("Authentication failed.")


def send_file(filename):
    try:
        if not os.path.isfile(filename):
            print(f"File '{filename}' not found.")
            return

        start_time = time.time()
        # Send the upload command to the server
        s.send(f"upload {filename}".encode())
        response = s.recv(1024).decode()
        print(response)

        if "Server is ready to receive file" in response:
            with open(filename, "rb") as file:
                while (data := file.read(1024)):
                    s.send(data)

            #Send the end of file marker
            s.send(b'FILE_END')

            # Wait for the server's confirmation message
            response = s.recv(1024).decode()
            print(response)

            end_time = time.time()
            transfer_time = round(end_time - start_time,2)
            file_size = os.path.getsize(filename) / 1024  # Convert to KB
            data_rate = round(file_size / transfer_time, 2) if transfer_time > 0 else 0

            analytics.record_statistic("upload", filename, data_rate, transfer_time)
        else:
            print("Server rejected the upload.")
    except Exception as e:
        print(f"Error during file upload: {e}")


def receive_file(filename):
    try:
        s.send(f"download {filename}".encode())
        response = s.recv(1024).decode()

        if "Ready" in response:
            with open(filename, "wb") as f:
                while True:
                    data = s.recv(1024)
                    if data.endswith(b'FILE_END'):  # Check for end marker
                        f.write(data[:-8])  # Write all except 'FILE_END'
                        break
                    f.write(data)

            print(f"File {filename} downloaded successfully.")
        else:
            print(response)
    except Exception as e:
        print(f"Error during file download: {e}")


# Save analytics data before exiting
def save_analytics():
    analytics.save_to_file()

def delete_file(filename):
    try:
        s.send(f"delete {filename}".encode())
        response = s.recv(1024).decode()
        print(response)
    except Exception as e:
        print(f"Error during file deletion: {e}")


def view_directory():
    try:
        s.send("dir".encode())
        response = s.recv(4096).decode()  # Larger buffer for directory listing
        print("Server Directory Listing:\n" + response)
    except Exception as e:
        print(f"Error fetching directory listing: {e}")


def manage_subfolder(action, path):
    try:
        s.send(f"subfolder {action} {path}".encode())
        response = s.recv(1024).decode()
        print(response)
    except Exception as e:
        print(f"Error managing subfolder: {e}")

def main():
    create_socket()
    host = input("Enter server IP: ")
    port = 9999
    connect_to_server(host, port)
    authenticate()

    try:
        while True:
            command = input("Enter command: ")
            if command.startswith("upload"):
                filename = command.split()[1]
                send_file(filename)
            elif command.startswith("download"):
                filename = command.split()[1]
                receive_file(filename)
            elif command.startswith("delete"):
                filename = command.split()[1]
                delete_file(filename)
            elif command == "dir":
                view_directory()
            elif command.startswith("subfolder"):
                _, action, path = command.split(maxsplit=2)
                manage_subfolder(action, path)
            elif command == "quit":
                s.send(command.encode())
                s.close()
                break
            else:
                s.send(command.encode())
                print(s.recv(1024).decode())
    finally:
        save_analytics()


if __name__ == "__main__":
    main()
=======
import socket
import sys
import os
import hashlib

def create_socket():
    try:
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket created.")
    except socket.error as msg:
        print("Socket creation error: " + str(msg))


def connect_to_server(host, port):
    try:
        s.connect((host, port))
        print("Connected to the server.")
    except socket.error as msg:
        print("Connection error: " + str(msg))
        sys.exit()


def authenticate():
    print(s.recv(1024).decode(), end="")
    username = input()
    username = hashlib.sha256(username.encode()).hexdigest()
    s.send(username.encode())

    print(s.recv(1024).decode(), end="")
    password = input()
    password = hashlib.sha256(password.encode()).hexdigest()

    s.send(password.encode())

    response = s.recv(1024).decode()
    print(response)
    if "Authentication successful" not in response:
        sys.exit("Authentication failed.")


def send_file(filename):
    try:
        if not os.path.isfile(filename):
            print(f"File '{filename}' not found.")
            return

        # Send the upload command to the server
        s.send(f"upload {filename}".encode())
        response = s.recv(1024).decode()
        print(response)

        if "Server is ready to receive file" in response:
            # Open the file and send its contents
            with open(filename, "rb") as file:
                while (data := file.read(1024)):
                    s.send(data)

            # Send the end of file marker
            s.send(b'FILE_END')

            # Wait for the server's confirmation message
            response = s.recv(1024).decode()
            print(response)  # Print the server's success or error message
        else:
            print("Server rejected the upload.")
    except Exception as e:
        print(f"Error during file upload: {e}")



def receive_file(filename):
    s.send(f"download {filename}".encode())
    response = s.recv(1024).decode()
    if "Ready" in response:
        with open(filename, "wb") as f:
            while True:
                data = s.recv(1024)
                if data.endswith(b'FILE_END'):  # Check for end marker
                    f.write(data[:-8])  # Write all except 'FILE_END'
                    break
                f.write(data)
        print(f"File {filename} downloaded successfully.")
    else:
        print(response)



def delete_file(filename):
    try:
        s.send(f"delete {filename}".encode())
        response = s.recv(1024).decode()
        print(response)
    except Exception as e:
        print(f"Error during file deletion: {e}")


def view_directory():
    try:
        s.send("dir".encode())
        response = s.recv(4096).decode()  # Larger buffer for directory listing
        print("Server Directory Listing:\n" + response)
    except Exception as e:
        print(f"Error fetching directory listing: {e}")


def manage_subfolder(action, path):
    try:
        s.send(f"subfolder {action} {path}".encode())
        response = s.recv(1024).decode()
        print(response)
    except Exception as e:
        print(f"Error managing subfolder: {e}")


def main():
    create_socket()
    host = input("Enter server IP: ")
    port = 9999
    connect_to_server(host, port)
    authenticate()

    while True:
        command = input("Enter command: ")
        if command.startswith("upload"):
            filename = command.split()[1]
            send_file(filename)
        elif command.startswith("download"):
            filename = command.split()[1]
            receive_file(filename)
        elif command.startswith("delete"):
            filename = command.split()[1]
            delete_file(filename)
        elif command == "dir":
            view_directory()
        elif command.startswith("subfolder"):
            _, action, path = command.split(maxsplit=2)
            manage_subfolder(action, path)
        elif command == "quit":
            s.send(command.encode())
            s.close()
            break
        else:
            s.send(command.encode())
            print(s.recv(1024).decode())


if __name__ == "__main__":
    main()
>>>>>>> fea8715c7bc080d14f2a5d1f8c34b0715c3152d1
