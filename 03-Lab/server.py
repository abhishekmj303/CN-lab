import socket
import threading
from collections import namedtuple

# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 5353
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

clients = []
Client = namedtuple("Client", ["conn", "addr"])

def find_client(addr):
    for client in clients:
        if client.addr == addr:
            return client
    return None

def send_msg(msg, addr):
    client = find_client(addr)
    if client is None:
        return False
    try:
        client.conn.send(msg.encode(FORMAT))
        return True
    except BrokenPipeError:
        return False

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
        
        print(f"[{addr}] {msg}")
        try:
            conn.send("Msg received".encode(FORMAT))
        except BrokenPipeError:
            connected = False

        addr_input = input("Send msg to (ip port): ")
        addr_input = (addr_input.split()[0], int(addr_input.split()[1]))
        msg_input = input("Message: ")
        if not send_msg(msg_input, addr_input):
            print(f"[ERROR] Cannot send message to {addr_input}")

    
    print(f"[DISCONNECT CONNECTION] {addr} disconnected.")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

    conn.close()

def main():
    print(f"[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.bind(ADDR)

    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    
    while True:
        conn, addr = server.accept()
        clients.append(Client(conn, addr))

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()