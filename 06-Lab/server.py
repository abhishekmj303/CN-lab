# Abhishek M J - CS21B2018
# server.py

import socket
import threading
import time
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

clients = [] # list of clients connected to the server

@dataclass
class Client:
    '''Client class to store client information'''
    conn: socket.socket
    addr: str
    ok: bool


class FileNotSent(Exception):
    '''Exception raised when file is not sent'''
    pass


def find_client(addr: str) -> Client | None:
    '''Find client with given address'''
    for client in clients:
        if client.addr == addr:
            return client
    return None


def msg_encode(msg: str, from_client: Client | None = None) -> bytes:
    '''
    Encode message to be sent to client
    
    MSG FORMAT: <to_addr>/<msg>
    '''
    msg = urllib.parse.quote(msg)
    if from_client is None: # if message is from server
        to_msg = f"SERVER/{msg}"
    else:
        to_msg = f"{from_client.addr}/{msg}"
    return to_msg.encode(FORMAT)


def forward_file(from_client: Client, to_client: Client, file_name: str):
    '''
    Forward file from one client to another:
    1. Send file name to to_client: <to_addr>/<file_name>
    2. Send file data in raw bytes
    3. Send EOF to indicate end of file
    '''
    to_client.conn.send(msg_encode(file_name, from_client))
    time.sleep(0.1)

    file_data = from_client.conn.recv(SIZE)
    while file_data != b"EOF":
        to_client.conn.send(file_data)
        file_data = from_client.conn.recv(SIZE)
    time.sleep(0.1)
    to_client.conn.send(file_data)


def handle_msg(from_msg: str, from_client: Client):
    '''
    Handle message recieved from client:
    1. File transfer: <to_addr>/<file_name>
    2. Acknowledgement: SERVER/<to_addr>
    '''
    try:
        to_addr, msg = from_msg.strip().split("/")
        msg = urllib.parse.unquote(msg)
    except ValueError:
        raise FileNotSent(f"Invalid message format: {from_msg}")
    
    # If acknoledgement is recieved
    if to_addr == "SERVER":
        to_addr = msg # to_addr for acknowledgement
        file_name = "File sent"
        from_client = Client(None, "SERVER", True)
    else: # If message is to be sent
        file_name = msg # file_name for file transfer
        print(f"[SENDING] SERVER -> {from_client.addr}: File name recieved")
        from_client.conn.send(msg_encode("File name recieved"))

    to_client = find_client(to_addr)
    if to_client is None:
        raise FileNotSent(f"Client {to_addr} not found.")
    
    print(f"[SENDING] {from_client.addr} -> {to_client.addr}: {file_name}")
    try:
        if from_client.conn: # if file transfer
            forward_file(from_client, to_client, file_name)
        else: # if acknowledgement
            to_client.conn.send(msg_encode(file_name, from_client))
    except BrokenPipeError:
        disconnect_client(to_client)
        raise FileNotSent(f"Client {to_addr} disconnected.")


def server_broadcast(msg: str):
    '''Send message to all clients'''
    for client in clients:
        try:
            client.conn.send(msg_encode(msg))
        except BrokenPipeError:
            disconnect_client(client)


def disconnect_client(client: Client):
    '''Disconnect client'''
    client.ok = False

    print(f"[DISCONNECT CLIENT] {client.addr} disconnected.")
    print(f"[ACTIVE CLIENTS] {threading.active_count() - 2}")

    # broadcast client disconnect: <client_addr>-
    server_broadcast(f"{client.addr}-")

    clients.remove(client)
    client.conn.close()


def handle_client(client: Client):
    '''
    Handle client connection:
    1. Send all connected clients to new client
    2. Recieve message from client
    3. Handle recieved message
    '''
    addr = client.addr
    conn = client.conn
    print(f"[NEW CLIENT] {addr} connected.")

    for c in clients: # send all connected clients to new client
        if c.addr != addr:
            conn.send(msg_encode(f"{c.addr}+"))
            time.sleep(0.2)

    while client.ok: # recieve message from client
        from_msg = conn.recv(SIZE).decode(FORMAT)
        if from_msg == DISCONNECT_MESSAGE:
            client.ok = False
            break
        elif not from_msg:
            continue
        
        try: # handle recieved message
            handle_msg(from_msg, client)
        except FileNotSent as e:
            print(f"[ERROR] {e}")
            conn.send(msg_encode(str(e)))

    try:
        disconnect_client(client)
    except Exception as e:
        pass

def main():
    print(f"[STARTING] Server is starting...")

    # create socket, bind to address, and listen
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    print(f"[ACTIVE CLIENTS] {threading.active_count() - 1}")
    
    while True: # accept new connection
        conn, addr = server.accept()
        addr = f"{addr[0]}:{addr[1]}"
        current_client = Client(conn, addr, True)
        clients.append(current_client)

        server_broadcast(f"{current_client.addr}+") # broadcast new client: <client_addr>+

        # start new thread to handle client
        thread = threading.Thread(target=handle_client, args=(current_client,))
        thread.start()
        
        print(f"[ACTIVE CLIENTS] {threading.active_count() - 1}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt: # handle keyboard interrupt
        print("\n[EXITING] Server is shutting down...")
        for client in clients: # send disconnect message to all clients
            client.conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
        os._exit(0)