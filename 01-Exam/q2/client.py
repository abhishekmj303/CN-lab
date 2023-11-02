import socket
import threading
import sys
import os

IP = socket.gethostbyname(socket.gethostname())
# IP = "172.16.19.141"
# IP = ''
PORT = 53535
ADDR = (IP, PORT)
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
    global client
    c_id = int(sys.argv[1])
    print(f"Client id: {c_id}")

    client.connect(ADDR)
    client.send(f"{c_id}".encode())

    is_ok = client.recv(SIZE).decode()
    if is_ok == 'OK':
        print(f"[CONNECTED] Client connecting to S {IP}:{PORT}")
    else:
        client.close()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_port = int(is_ok.split('!')[1])
        client.connect((IP, new_port))
        client.send(f"{c_id}".encode())
        print(f"[CONNECTED] Client connecting to Sr {IP}:{new_port}")

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
