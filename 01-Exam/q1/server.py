import socket
import threading
import sys
import os

from collections import defaultdict
from dataclasses import dataclass

IP = ''
PORT = 53530
SIZE = 1024
FORMAT = "utf-8"
ACK = "Msg Recieved"
DISCONNECT_MESSAGE = "QUIT!"

clients = defaultdict(lambda: defaultdict(None))
servers_connected = defaultdict(set)

@dataclass
class Client:
    id: int
    conn: socket.socket
    addr: str
    connected: bool


def disconnect_conn(conn: socket.socket):
    conn.send(DISCONNECT_MESSAGE.encode())
    conn.close()


def disconnect(c_id: int, s_ids: set):
    global clients, servers_connected
    for s_id in s_ids:
        client = clients[s_id].get(c_id, None)
        if client is not None:
            disconnect_conn(client.conn)
            servers_connected[c_id].remove(s_id)
            clients[s_id].pop(c_id)
            print(f"[S{s_id}] [CLIENT OFFLINE] C{c_id}")


def server_loop(s_id: int):
    global clients, servers_connected
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT+s_id))
    server.listen()

    print(f"[S{s_id}] Starting Server at {IP}:{PORT+s_id}")

    while True:
        conn, addr = server.accept()
        addr = f"{addr[0]}:{addr[1]}"
        print(f"[S{s_id}] [CONNECTION REQUEST] {addr}")
        try:
            c_id = int(conn.recv(SIZE).decode())
        except TypeError:
            print(f"[S{s_id}] [CONNECTION REJECTED] Invalid client id")
            disconnect_conn(conn)
            continue

        if s_id in servers_connected[c_id]:
            print(f"[S{s_id}] [CONNECTION REJECTED] Client id already connected")
            disconnect_conn(conn)
            continue

        if 0 in servers_connected[c_id]:
            print(f"[S{s_id}] [CONNECTION REJECTED] S0 also connected")
            disconnect_conn(conn)
            continue
        elif 1 in servers_connected[c_id]:
            if s_id not in {2, 3}:
                if s_id == 0:
                    print(f"[S{s_id}] [CONNECTION ALTERING] Disconnecting S2, S3")
                    disconnect(c_id, {2, 3})
                else:
                    print(f"[S{s_id}] [CONNECTION REJECTED] S1 also connected")
                    disconnect_conn(conn)
                    continue
        elif 4 in servers_connected[c_id]:
            if s_id == 0:
                print(f"[S{s_id}] [CONNECTION ALTERING] Disconnecting S1, S2, S3, S4")
                disconnect(c_id, {1, 2, 3, 4})
        
        print(f"[S{s_id}] [CONNECTION ACCEPTED] {addr}")
        
        client = Client(id=c_id, conn=conn, addr=addr, connected=True)
        clients[s_id][c_id] = client
        servers_connected[c_id].add(s_id)

        client_thread = threading.Thread(target=handle_client, args=(s_id, c_id))
        client_thread.start()


def handle_client(s_id: int, c_id: int):
    print(f"[S{s_id}] [CLIENT ONLINE] C{c_id}")

    client: Client = clients[s_id][c_id]
    while client.connected:
        msg = client.conn.recv(SIZE).decode()
        if not msg or msg == DISCONNECT_MESSAGE:
            client.connected = False
            break

        print(f"[S{s_id}] [C{c_id}] {msg}")
        try:
            client.conn.send(ACK.encode())
        except BrokenPipeError:
            print(f"[S{s_id}] [ERROR] Cannot send message to C{c_id}")
            client.connected = False
            break
    
    try:
        disconnect(c_id, {s_id})
    except:
        pass


def main():
    server_threads = []
    for i in range(5):
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
