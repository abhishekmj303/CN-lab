import socket
import threading
import os
import readline
# to url_encode and decode
import urllib.parse
from collections import namedtuple

IP = socket.gethostbyname(socket.gethostname())
# IP = "172.16.19.141"
# IP = ''
PORT = 53533
# PORT = 8006
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = []

current_input = ""


class MsgNotRecieved(Exception):
    pass


def print_msg(msg):
    if not current_input:
        print(msg)
    else:
        input_buffer = readline.get_line_buffer()
        print(f"\r{msg}\n{current_input}{input_buffer}", end="", flush=True)


def input_msg(string):
    global current_input

    current_input = string
    result = input(f"\r{string}")
    current_input = ""

    return result


def msg_encode(msg, to_addr=None):
    msg = urllib.parse.quote(msg)
    if to_addr is None:
        to_msg = f"SERVER/{msg}"
    else:
        to_msg = f"{to_addr}/{msg}"
    return to_msg.encode(FORMAT)


def handle_msg(from_msg, client):
    try:
        from_addr, msg = from_msg.strip().split("/")
        msg = urllib.parse.unquote(msg)
    except ValueError:
        raise MsgNotRecieved(f"Invalid message format: {from_msg}")
    
    # Check if broadcast
    if from_addr == "SERVER":
        if msg[-1] == "+":
            clients.append(msg[:-1])
            print_msg(f"[CLIENT ONLINE] {msg[:-1]} connected.")
        elif msg[-1] == "-":
            clients.remove(msg[:-1])
            print_msg(f"[CLIENT OFFLINE] {msg[:-1]} disconnected.")
        else:
            print_msg(f"[SERVER] {msg}")
    else:
        print_msg(f"[{from_addr}] {msg}")
        # send acknowledgement
        client.send(msg_encode(from_addr))


def disconnect_server(client):
    client.send(DISCONNECT_MESSAGE.encode(FORMAT))
    print_msg(f"[SERVER DISCONNECTED] Client disconnected from {IP}:{PORT}")
    client.close()
    os._exit(0)


def handle_server(client: socket.socket):
    connected = True
    while connected:
        try:
            msg = client.recv(SIZE).decode(FORMAT)
        except OSError:
            return
        if not msg or msg == DISCONNECT_MESSAGE:
            connected = False
            break

        try:
            handle_msg(msg, client)
        except MsgNotRecieved as e:
            print_msg(f"[ERROR] {e}")

    try:
        disconnect_server(client)
    except Exception:
        pass


def main():
    global client
    client.connect(ADDR)
    print_msg(f"[SERVER CONNECTED] Client connected to {IP}:{PORT}")

    server_thread = threading.Thread(target=handle_server, args=(client,))
    server_thread.start()

    connected = True
    while connected:
        to_addr = input_msg("(ip:port)> ").strip()

        if to_addr == DISCONNECT_MESSAGE:
            connected = False
            disconnect_server(client)

        elif to_addr.lower() in ["", "l", "list"]:
            print_msg(f"[ONLINE CLIENT LIST] {len(clients)} clients connected.")
            for c in clients:
                print_msg(f"[CLIENT] {c}")
            continue

        if to_addr not in clients:
            print_msg(f"[ERROR] Client '{to_addr}' not found.")
            continue

        to_msg = input_msg("(msg)> ")

        client.send(msg_encode(to_msg, to_addr))

    disconnect_server(client)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        disconnect_server(client)
        print_msg("[EXITING] Client is exiting...")