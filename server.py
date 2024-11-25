import socket
import threading
import os
import hashlib

# Configuration
HOST = ""  # Bind to all available interfaces
PORT = 9999
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
        valid_user = hashlib.sha256("user".encode()).hexdigest()
        valid_password = hashlib.sha256("pass".encode()).hexdigest()

        if username == valid_user and password == valid_password:
            conn.send("Authentication successful.\n".encode())
            print("Authentication successful.\n")
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

        # Check if file exists and prompt user to overwrite
        if os.path.exists(filepath):
            conn.send("File already exists. Overwrite? (yes/no): ".encode())
            response = conn.recv(1024).decode().strip()
            if response.lower() != "yes":
                conn.send("Upload canceled.\n".encode())
                return

        conn.send("Server is ready to receive file.\n".encode())

        # Receive file data
        with open(filepath, "wb") as file:
            while True:
                data = conn.recv(1024)
                if data.endswith(b'FILE_END'):  # Check if the marker is in this chunk
                    file.write(data[:-8])  # Write all except 'FILE_END'
                    break
                file.write(data)

        # Print and send success message
        success_message = f"File '{filename}' uploaded successfully."
        print(success_message)  # Print to server terminal
        conn.send(f"{success_message}\n".encode())

    except Exception as e:
        error_message = f"Error during file upload: {str(e)}"
        print(error_message)  # Print error to server terminal
        conn.send(error_message.encode())


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

            # Notify server that the file is being sent
            print(f"File '{filename}' downloaded successfully.")
        else:
            conn.send(f"File {filename} not found.\n".encode())
    except Exception as e:
        error_message = f"Error during file download: {str(e)}"
        print(error_message)  # Print error to server terminal
        conn.send(error_message.encode())



# Handle delete file
def handle_delete(conn, filename):
    try:
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)

            # Notify server and client that the file was deleted
            print(f"File '{filename}' deleted successfully.")
            conn.send(f"File {filename} deleted successfully.\n".encode())
        else:
            conn.send(f"File {filename} not found.\n".encode())
    except Exception as e:
        error_message = f"Error deleting file: {str(e)}"
        print(error_message)  # Print error to server terminal
        conn.send(error_message.encode())



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

        # Handling subfolder creation
        if action == "create":
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # Create the subfolder
                success_message = f"Subfolder '{path}' created successfully on the server."
                print(success_message)  # Print to server terminal
                conn.send(success_message.encode())
            else:
                error_message = f"Subfolder '{path}' already exists on the server."
                print(error_message)  # Print to server terminal
                conn.send(error_message.encode())

        # Handling subfolder deletion
        elif action == "delete":
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                try:
                    os.rmdir(folder_path)  # Delete the subfolder (only if it's empty)
                    success_message = f"Subfolder '{path}' deleted successfully from the server."
                    print(success_message)  # Print to server terminal
                    conn.send(success_message.encode())
                except OSError:
                    error_message = f"Subfolder '{path}' is not empty, unable to delete."
                    print(error_message)  # Print to server terminal
                    conn.send(error_message.encode())
            else:
                error_message = f"Subfolder '{path}' does not exist or is not a directory on the server."
                print(error_message)  # Print to server terminal
                conn.send(error_message.encode())

        # If the action is neither 'create' nor 'delete'
        else:
            invalid_action_message = "Invalid subfolder action. Please use 'create' or 'delete'."
            print(invalid_action_message)  # Print to server terminal
            conn.send(invalid_action_message.encode())

    except Exception as e:
        error_message = f"Error managing subfolder: {str(e)}"
        print(error_message)  # Print to server terminal
        conn.send(error_message.encode())



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
                print("Client disconnected.\n")
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
