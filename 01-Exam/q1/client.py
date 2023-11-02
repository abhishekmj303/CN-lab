import socket
import threading
import sys
import os

IP = socket.gethostbyname(socket.gethostname())
# IP = "172.16.19.141"
# IP = ''
PORT = 53530
SERVERS = [PORT+i for i in range(5)]
# PORT = 8006
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def handle_server(client: socket.socket):
    connected = True
    while connected:
        try:
            msg = client.recv(SIZE).decode()
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
    c_id = int(sys.argv[1])
    print(f"Client id: {c_id}")
    s_id = int(input("Enter the server id (int): "))
    ADDR = (IP, SERVERS[s_id])

    client.connect(ADDR)
    print(f"[CONNECTED] Client connecting to S{s_id} {IP}:{PORT}")

    client.send(f"{c_id}".encode())

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
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <client-id>")
        exit()
    try:
        main()
    except KeyboardInterrupt:
        client.send(DISCONNECT_MESSAGE.encode())
        client.close()
    except Exception as e:
        print(e)
    finally:
        os._exit(0)
