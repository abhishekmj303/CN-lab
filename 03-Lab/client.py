import socket
import threading
import sys
import os

IP = socket.gethostbyname(socket.gethostname())
# IP = "172.16.19.141"
# IP = ''
PORT = 53535
# PORT = 8006
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

def handle_server(client: socket.socket):
    connected = True
    while connected:
        try:
            msg = client.recv(SIZE).decode(FORMAT)
        except OSError:
            return
        if msg == DISCONNECT_MESSAGE:
            connected = False
        
        if msg:
            print(f"\r[SERVER] {msg}")
            print("> ", end="")
            sys.stdout.flush()
    print()

    print(f"[DISCONNECT CONNECTION] Server disconnected.")
    client.close()
    os._exit(0)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to {IP}:{PORT}")

    server_thread = threading.Thread(target=handle_server, args=(client,))
    server_thread.start()

    connected = True
    while connected:
        msg = input("> ")
        client.send(msg.encode(FORMAT))
        if msg == DISCONNECT_MESSAGE:
            connected = False

    print(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")
    client.close()

if __name__ == "__main__":
    main()