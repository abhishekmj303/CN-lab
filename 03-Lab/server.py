import socket
import threading
import sys
import os
from collections import namedtuple

# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 53535
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

clients = []
Client = namedtuple("Client", ["conn", "addr"])

current_input = None

def print_msg(msg):
    if current_input is None:
        print(msg)
    else:
        print(f"\r{msg}\n{current_input}", end="")
        sys.stdout.flush()


def input_msg(string):
    global current_input

    current_input = string
    result = input(string)
    current_input = None

    return result


def find_client(addr):
    for client in clients:
        if client.addr == addr:
            return client
    return None


def server_send():
    while True:
        addr_input = input_msg("(ip:port)> ")
        if addr_input == DISCONNECT_MESSAGE:
            while clients:
                client = clients.pop()
                client.conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
            os._exit(0)
        
        try:
            addr_input = (addr_input.split(":")[0], int(addr_input.split(":")[1]))
        except IndexError or ValueError:
            print_msg(f"[ERROR] Invalid address {addr_input}")
            continue
        
        client = find_client(addr_input)
        if client is None:
            print_msg(f"[ERROR] Client not found {addr_input}")
            continue

        msg_input = input_msg("(msg)> ")

        try:
            client.conn.send(msg_input.encode(FORMAT))
        except BrokenPipeError:
            print_msg(f"[ERROR] Cannot send message to {addr_input}")


def handle_client(conn, addr):
    print_msg(f"[NEW CONNECTION] {addr[0]}:{addr[1]} connected.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
        
        print_msg(f"[{addr[0]}:{addr[1]}] {msg}")
        try:
            conn.send("Msg received".encode(FORMAT))
        except BrokenPipeError:
            print_msg(f"[ERROR] Cannot send message to {addr}")
            connected = False
    
    print_msg(f"[DISCONNECT CONNECTION] {addr[0]}:{addr[1]} disconnected.")
    print_msg(f"[ACTIVE CONNECTIONS] {threading.active_count() - 3}")

    clients.remove(Client(conn, addr))
    conn.close()

def main():
    print_msg(f"[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.bind(ADDR)

    server.listen()
    print_msg(f"[LISTENING] Server is listening on {IP}:{PORT}")

    print_msg(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    server_send_thread = threading.Thread(target=server_send)
    server_send_thread.start()
    
    while True:
        conn, addr = server.accept()
        clients.append(Client(conn, addr))

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        
        print_msg(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

if __name__ == "__main__":
    main()