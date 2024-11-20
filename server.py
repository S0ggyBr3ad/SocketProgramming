import socket
import threading
import os
import hashlib

# Configuration
HOST = ""  # Bind to all available interfaces
PORT = 7777
UPLOAD_DIR = "uploads"


# Ensure the upload directory exists
def ensure_upload_directory():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


# Handle client authentication
def authenticate(conn):
    try:
        conn.send("Username: ".encode())
        username = conn.recv(1024).decode().strip()
        conn.send("Password: ".encode())
        password = conn.recv(1024).decode().strip()

        # Simple authentication (Replace with more secure mechanisms for production)
        valid_user = "user"
        valid_password = hashlib.sha256("pass".encode()).hexdigest()

        if username == valid_user and hashlib.sha256(password.encode()).hexdigest() == valid_password:
            conn.send("Authentication successful.\n".encode())
            return True
        else:
            conn.send("Authentication failed.\n".encode())
            conn.close()
            return False
    except Exception as e:
        conn.send(f"Authentication error: {str(e)}\n".encode())
        return False


# Handle file upload
def handle_upload(conn, filename):
    try:
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            conn.send("File already exists. Overwrite? (yes/no): ".encode())
            response = conn.recv(1024).decode().strip()
            if response.lower() != "yes":
                conn.send("Upload canceled.\n".encode())
                return

        conn.send("Ready to receive file.\n".encode())

        # Receive file data and write to the server's file system
        with open(filepath, "wb") as file:
            while True:
                data = conn.recv(1024)
                if data == b'FILE_END':  # End of file marker
                    break
                file.write(data)

        conn.send(f"File {filename} uploaded successfully.\n".encode())
    except Exception as e:
        conn.send(f"Error during file upload: {str(e)}\n".encode())


# Handle file download
def handle_download(conn, filename):
    try:
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(filepath):
            conn.send("Ready to send file.\n".encode())
            with open(filepath, "rb") as file:
                while (data := file.read(1024)):
                    conn.send(data)
            conn.send(b'FILE_END')
        else:
            conn.send(f"File {filename} not found.\n".encode())
    except Exception as e:
        conn.send(f"Error during file download: {str(e)}\n".encode())


# Handle delete file
def handle_delete(conn, filename):
    try:
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
            conn.send(f"File {filename} deleted successfully.\n".encode())
        else:
            conn.send(f"File {filename} not found.\n".encode())
    except Exception as e:
        conn.send(f"Error deleting file: {str(e)}\n".encode())


# Handle directory listing
def handle_dir(conn):
    try:
        files = os.listdir(UPLOAD_DIR)
        response = "\n".join(files) if files else "No files or directories found."
        conn.send(response.encode())
    except Exception as e:
        conn.send(f"Error listing directory: {str(e)}\n".encode())


# Handle subfolder management
def handle_subfolder(conn, action, path):
    try:
        folder_path = os.path.join(UPLOAD_DIR, path)

        if action == "create":
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                conn.send(f"Subfolder '{path}' created successfully.\n".encode())
            else:
                conn.send(f"Subfolder '{path}' already exists.\n".encode())

        elif action == "delete":
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                os.rmdir(folder_path)
                conn.send(f"Subfolder '{path}' deleted successfully.\n".encode())
            else:
                conn.send(f"Subfolder '{path}' does not exist or is not empty.\n".encode())
        else:
            conn.send("Invalid subfolder action.\n".encode())
    except Exception as e:
        conn.send(f"Error managing subfolder: {str(e)}\n".encode())


# Handle client commands
def handle_client(conn, addr):
    print(f"Connection established with {addr}")
    if not authenticate(conn):
        return

    while True:
        try:
            # Receive command from the client
            command = conn.recv(1024).decode().strip()
            if command.startswith("upload"):
                _, filename = command.split(" ", 1)
                handle_upload(conn, filename)
            elif command.startswith("download"):
                _, filename = command.split(" ", 1)
                handle_download(conn, filename)
            elif command.startswith("delete"):
                _, filename = command.split(" ", 1)
                handle_delete(conn, filename)
            elif command == "dir":
                handle_dir(conn)
            elif command.startswith("subfolder"):
                _, action, path = command.split(maxsplit=2)
                handle_subfolder(conn, action, path)
            elif command.lower() == "quit":
                conn.send("Goodbye.\n".encode())
                conn.close()
                break
            else:
                conn.send("Invalid command.\n".encode())
        except Exception as e:
            conn.send(f"Error: {str(e)}\n".encode())
            conn.close()
            break


# Start the server
def start_server():
    ensure_upload_directory()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"Server listening on port {PORT}...")

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()


if __name__ == "__main__":
    start_server()
