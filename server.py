import socket
import select
import os
import sys

clients = {}  # dir to save username
SHARED_FILES_DIR = "SharedFiles"  # create sharefile
def broadcast_message(message, exclude_socket=None):
    """broadcast functionality"""
    client_sockets = list(clients.keys())  # create dir key 
    for client_socket in client_sockets:
        if client_socket != exclude_socket:
            try:
                client_socket.send(message.encode())
            except (ConnectionResetError, BrokenPipeError):
                handle_disconnect(client_socket, silent=True)

def send_private_message(sender_socket, target_username, message):
    """private message functionality"""
    target_socket = None
    for client_socket, username in clients.items():
        if username == target_username:
            target_socket = client_socket
            break

    if target_socket:
        try:
            sender_username = clients[sender_socket]
            private_message = f"[Private] {sender_username}: {message}"
            target_socket.send(private_message.encode())
        except (ConnectionResetError, BrokenPipeError):
            handle_disconnect(target_socket, silent=True)
    else:
        # check if user exists
        try:
            error_message = f"User '{target_username}' not found."
            sender_socket.send(error_message.encode())
        except (ConnectionResetError, BrokenPipeError):
            handle_disconnect(sender_socket, silent=True)

def handle_disconnect(client_socket, silent=False):
    """handle disconnected"""
    if client_socket in clients:
        username = clients.pop(client_socket)  # pop from dir
        if not silent:
            print(f"{username} disconnected.")
        broadcast_message(f"[{username}] has left")  # inform cilent
        try:
            client_socket.close() 
        except:
            pass

def list_shared_files():
    """list all files"""
    if not os.path.exists(SHARED_FILES_DIR):
        os.makedirs(SHARED_FILES_DIR)  # create folder if there r not exist
    files = os.listdir(SHARED_FILES_DIR)
    return files if files else ["No files available."]

def find_file(filename):
    """search files in folder """
    files = os.listdir(SHARED_FILES_DIR)
    for file in files:
        if file.lower() == filename.lower():  # ignore upper or lower font
            return file
    return None

def send_file(client_socket, filename):
    """send file to cilent """
    real_filename = find_file(filename)
    if not real_filename:
        client_socket.send(f"File '{filename}' not found.".encode())
        return

    filepath = os.path.join(SHARED_FILES_DIR, real_filename)
    try:
        with open(filepath, "rb") as file:
            content = file.read()
        client_socket.send(f"FILE_START {real_filename} {len(content)}".encode()) 
        client_socket.sendall(content)  # send file
        client_socket.send("FILE_END".encode()) 
    except Exception as e:
        client_socket.send(f"Error sending file: {e}".encode())

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(5)
    print(f"Server started on port {port}...")
    sockets_list = [server_socket]

    while True:
        try:
            read_sockets, _, _ = select.select(sockets_list, [], [])
            for notified_socket in read_sockets:
                if notified_socket == server_socket:
                    # new connection
                    client_socket, client_address = server_socket.accept()
                    try:
                        username = client_socket.recv(1024).decode().strip()
                        if not username:
                            raise ValueError("Invalid username")
                        sockets_list.append(client_socket)
                        clients[client_socket] = username
                        print(f"Username {username} connected from {client_address}.")
                        broadcast_message(f"[{username}] has joined", exclude_socket=client_socket)
                    except Exception as e:
                        print(f"Failed to accept connection: {e}")
                        client_socket.close()
                else:
                    # receive message
                    try:
                        message = notified_socket.recv(1024).decode().strip()
                        if not message:  # disconnection 
                            if notified_socket in sockets_list:
                                sockets_list.remove(notified_socket)
                            handle_disconnect(notified_socket)
                        elif message.lower() == "exit":  # exit functionality
                            if notified_socket in sockets_list:
                                sockets_list.remove(notified_socket)
                            handle_disconnect(notified_socket)
                        elif message.startswith("/private"):  # private message
                            parts = message.split(" ", 2)
                            if len(parts) < 3:
                                error_message = "Invalid private message format. Use /private [username] [message]."
                                notified_socket.send(error_message.encode())
                            else:
                                target_username = parts[1]
                                private_message = parts[2]
                                send_private_message(notified_socket, target_username, private_message)
                        elif message == "/files":  # list files
                            files = list_shared_files()
                            notified_socket.send("\n".join(files).encode())
                        elif message.startswith("/download "):  # download functionality
                            parts = message.split(" ", 1)
                            if len(parts) < 2:
                                notified_socket.send("Invalid download command. Use /download [filename].".encode())
                            else:
                                filename = parts[1]
                                send_file(notified_socket, filename)
                        else:
                            username = clients.get(notified_socket, "Unknown")
                            broadcast_message(f"{username}: {message}", exclude_socket=notified_socket)
                    except (ConnectionResetError, ValueError, BrokenPipeError):
                        # handle disconnection
                        if notified_socket in sockets_list:
                            sockets_list.remove(notified_socket)
                        handle_disconnect(notified_socket, silent=True)
        except KeyboardInterrupt:
            print("Server shutting down...")
            for client_socket in list(clients.keys()):
                handle_disconnect(client_socket, silent=True)
            server_socket.close()
            break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py [port]")
        sys.exit(1)
    start_server(int(sys.argv[1]))
