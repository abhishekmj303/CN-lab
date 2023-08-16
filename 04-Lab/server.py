import socket
import threading
import sys
import os
# to url_encode and decode
import urllib.parse
from dataclasses import dataclass

# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 53533
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

clients = []

@dataclass
class Client:
    conn: socket.socket
    addr: str
    ok: bool


class MsgNotDelivered(Exception):
    pass


def find_client(addr):
    for client in clients:
        if client.addr == addr:
            return client
    return None


def msg_encode(msg, from_client=None):
    msg = urllib.parse.quote(msg)
    if from_client is None:
        to_msg = f"SERVER/{msg}"
    else:
        to_msg = f"{from_client.addr}/{msg}"
    return to_msg.encode(FORMAT)


def server_send(from_msg, from_client):
    try:
        to_addr, msg = from_msg.strip().split("/")
        msg = urllib.parse.unquote(msg)
    except ValueError:
        raise MsgNotDelivered(f"Invalid message format: {from_msg}")
    
    # If acknoledgement is recieved
    if to_addr == "SERVER":
        to_addr = msg # msg sent is the address of another client
        msg = "Delivered"
        from_client = Client(None, "SERVER", True)
    else: # If message is to be sent
        print(f"[SENDING] SERVER -> {from_client.addr}: Recieved")
        from_client.conn.send(msg_encode("Recieved"))

    to_client = find_client(to_addr)
    if to_client is None:
        raise MsgNotDelivered(f"Client {to_addr} not found.")
    
    print(f"[SENDING] {from_client.addr} -> {to_client.addr}: {msg}")
    try:
        to_client.conn.send(msg_encode(msg, from_client))
    except BrokenPipeError:
        disconnect_client(to_client)
        raise MsgNotDelivered(f"Client {to_addr} disconnected.")


def server_broadcast(msg):
    for client in clients:
        try:
            client.conn.send(msg_encode(msg))
        except BrokenPipeError:
            disconnect_client(client)


def disconnect_client(client):
    client.ok = False

    print(f"[DISCONNECT CLIENT] {client.addr} disconnected.")
    print(f"[ACTIVE CLIENTS] {threading.active_count() - 2}")

    server_broadcast(f"{client.addr}-")

    clients.remove(client)
    client.conn.close()


def handle_client(client):
    addr = client.addr
    conn = client.conn
    print(f"[NEW CLIENT] {addr} connected.")

    for c in clients:
        if c.addr != addr:
            conn.send(msg_encode(f"{c.addr}+"))

    while client.ok:
        from_msg = conn.recv(SIZE).decode(FORMAT)
        if from_msg == DISCONNECT_MESSAGE:
            client.ok = False
            break
        elif not from_msg:
            continue
        
        try:
            server_send(from_msg, client)
        except MsgNotDelivered as e:
            print(f"[ERROR] {e}")
            conn.send(msg_encode(str(e)))

    try:
        disconnect_client(client)
    except Exception as e:
        pass

def main():
    print(f"[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.bind(ADDR)

    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    print(f"[ACTIVE CLIENTS] {threading.active_count() - 1}")
    
    while True:
        conn, addr = server.accept()
        addr = f"{addr[0]}:{addr[1]}"
        current_client = Client(conn, addr, True)
        clients.append(current_client)

        server_broadcast(f"{current_client.addr}+")

        thread = threading.Thread(target=handle_client, args=(current_client,))
        thread.start()
        
        print(f"[ACTIVE CLIENTS] {threading.active_count() - 1}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[EXITING] Server is exiting...")
        os._exit(0)