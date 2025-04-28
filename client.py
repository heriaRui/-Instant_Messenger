import socket
import threading
import os

def receive_messages(client_socket):
    """receive the message"""
    try:
        while True:
            header = client_socket.recv(1024).decode()
            if header.startswith("FILE_START"):
                _, filename, filesize = header.split(" ")
                filesize = int(filesize)
                content = b""
                while len(content) < filesize:
                    chunk = client_socket.recv(1024)
                    content += chunk
                    
                # save file
                local_dir = os.path.join(os.getcwd(), username)
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)
                filepath = os.path.join(local_dir, filename)
                with open(filepath, "wb") as file:
                    file.write(content)
                print(f"File '{filename}' downloaded successfully to {filepath}")
            elif header == "FILE_END":
                continue
            else:
                print(header)  # message functionality 
    except Exception as e:
        print(f"Error receiving message: {e}")
        client_socket.close()

def start_client(username, hostname, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((hostname, port))
        client_socket.send(username.encode())  # get username

        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

        # get message 
        while True:
            message = input()
            if message.lower() == "exit":
                client_socket.send(message.encode())
                break
            client_socket.send(message.encode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python client.py [username] [hostname] [port]")
        sys.exit(1)
    username = sys.argv[1]
    start_client(username, sys.argv[2], int(sys.argv[3]))
