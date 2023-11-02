import socket
import threading
import sys
import os

from collections import defaultdict
from dataclasses import dataclass

IP = ''
PORT = 53535
SIZE = 1024
FORMAT = "utf-8"
ACK = "Msg Recieved"
DISCONNECT_MESSAGE = "QUIT!"

S = {0: 'S', 1: 'Sr'}
clients = {0: defaultdict(None), 1: defaultdict(None)}
servers_connected = defaultdict(set)
clients_for_S = set()

MAX_LIMIT = 3
max_reached = False

@dataclass
class Client:
    id: int
    conn: socket.socket
    addr: str
    connected: bool


def disconnect_conn(conn: socket.socket):
    conn.send(DISCONNECT_MESSAGE.encode())
    conn.close()

def transfer_conn(conn: socket.socket):
    print('[S] TRANSFERRING TO Sr')
    conn.send(f"QUIT!{PORT+1}".encode())
    conn.close()


def disconnect(c_id: int, s_ids: set):
    global clients, servers_connected
    for s_id in s_ids:
        client = clients[s_id].get(c_id, None)
        if client is not None:
            disconnect_conn(client.conn)
            servers_connected[c_id].remove(s_id)
            clients[s_id].pop(c_id)
            print(f"[{S[s_id]}] [CLIENT OFFLINE] C{c_id}")


def server_loop(s_id: int):
    global clients, clients_connected, servers_connected, max_reached
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT+s_id))
    server.listen()

    print(f"[{S[s_id]}] Starting Server at {IP}:{PORT+s_id}")

    while True:
        conn, addr = server.accept()
        addr = f"{addr[0]}:{addr[1]}"
        # print(f"[{S[s_id]}] [CONNECTION REQUEST] {addr}")
        try:
            c_id = int(conn.recv(SIZE).decode())
        except TypeError:
            print("[ERROR] Invalid client id")
            disconnect_conn(conn)
            continue

        if s_id in servers_connected[c_id]:
            disconnect_conn(conn)
            continue

        if s_id == 0:
            if max_reached and c_id not in clients_for_S:
                transfer_conn(conn)
                continue
            else:
                conn.send('OK'.encode())
        
        
        client = Client(c_id, conn, addr, connected=True)
        clients[s_id][c_id] = client
        servers_connected[c_id].add(s_id)
        if s_id == 0:
            clients_for_S.add(c_id)
            if len(clients_for_S) == MAX_LIMIT:
                max_reached = True

        client_thread = threading.Thread(target=handle_client, args=(s_id, c_id))
        client_thread.start()


def handle_client(s_id: int, c_id: int):
    print(f"[{S[s_id]}] [CLIENT ONLINE] C{c_id}")

    client: Client = clients[s_id][c_id]
    while client.connected:
        msg = client.conn.recv(SIZE).decode()
        if not msg or msg == DISCONNECT_MESSAGE:
            client.connected = False
            break

        print(f"[{S[s_id]}] [C{c_id}] {msg}")
        try:
            client.conn.send(ACK.encode())
        except BrokenPipeError:
            print(f"[{S[s_id]}] [ERROR] Cannot send message to C{c_id}")
            client.connected = False
            break
    
    # try:
    disconnect(c_id, {s_id})
    # except:
    #     pass


def main():
    server_threads = []
    for i in range(2):
        server_threads.append(threading.Thread(target=server_loop, args=(i,)))
        server_threads[-1].start()
    
    for t in server_threads:
        t.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Servers Shutting down...")
        for c_id, s_ids in servers_connected.items():
            disconnect(c_id, s_ids)
    finally:
        os._exit(0)
