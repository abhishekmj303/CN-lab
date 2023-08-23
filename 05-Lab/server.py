import socket
import threading
import os
from dataclasses import dataclass

# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 53535
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

folder_path = "server/"

clients = []

@dataclass
class Client:
    conn: socket.socket
    addr: str

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    for i in range(2):
        msg = conn.recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            break

        opts = {0: "Create", 1: "File Content"}
        print(f"[{addr}] {opts[i]}: {msg}")

        try:
            if i == 0:
                file_name = msg
                file_path = folder_path + file_name
                with open(file_path, "w"):
                    conn.send(f"File name recieved: {msg}".encode(FORMAT))
            else:
                with open(file_path, "a") as f:
                    f.write(msg)
                    f.write("\n")
                    conn.send(f"File contents of {file_name} recieved: {msg}".encode(FORMAT))
        except Exception as e:
            print(e)
            conn.send(f"Error: {e}".encode(FORMAT))
            break

    conn.close()
    clients.remove(Client(conn, addr))
    print(f"[DISCONNECTED] {addr} disconnected.")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count()-2}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[STARTING] Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        addr = f"{addr[0]}:{addr[1]}"

        clients.append(Client(conn, addr))

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")

if __name__ == "__main__":
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    print(f"[SERVER] Keep the files to send/recieve inside folder: '{folder_path}'")
    try:
        main()
    except KeyboardInterrupt:
        print("\n[EXITING] Server is shutting down...")
        for client in clients:
            client.conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
            # client.conn.close()
        os._exit(0)