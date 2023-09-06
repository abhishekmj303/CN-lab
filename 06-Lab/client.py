import socket
import threading
import os
import readline
import time
# to url_encode and decode
import urllib.parse

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

folder_path = "client/" # folder to store files for client

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


def send_file(client, to_addr, file_name):
    file_path = file_name
    if not os.path.exists(file_path):
        print_msg(f"[ERROR] File '{file_name}' not found.")
        return
    
    client.send(msg_encode(os.path.basename(file_path), to_addr))
    time.sleep(0.1)

    with open(file_path, "rb") as f:
        bin_data = f.read(SIZE)
        while bin_data:
            client.send(bin_data)
            bin_data = f.read(SIZE)
        time.sleep(0.1)
        client.send(b"EOF")


def recieve_file(client, file_name):
    file_path = folder_path + file_name
    with open(file_path, "wb") as f:
        bin_data = client.recv(SIZE)
        while bin_data != b"EOF":
            f.write(bin_data)
            bin_data = client.recv(SIZE)


def handle_msg(from_msg, client):
    try:
        from_addr, msg = from_msg.strip().split("/")
        msg = urllib.parse.unquote(msg)
    except ValueError:
        raise MsgNotRecieved(f"Invalid message format: {from_msg}")
    
    # Check if broadcast
    if from_addr == "SERVER":
        if msg[-1] == "+":
            if len(clients) == 0:
                print_msg(f"[CURRENT CLIENT] {msg[:-1]}")
                global folder_path
                folder_path = msg[:-1] + "/"
                if not os.path.exists(folder_path): # create folder if not exists
                    os.makedirs(folder_path)
            else:
                print_msg(f"[CLIENT ONLINE] {msg[:-1]} connected.")
            clients.append(msg[:-1])
        elif msg[-1] == "-":
            clients.remove(msg[:-1])
            print_msg(f"[CLIENT OFFLINE] {msg[:-1]} disconnected.")
        else:
            print_msg(f"[SERVER] {msg}")
    else:
        print_msg(f"[{from_addr}] {msg}")
        recieve_file(client, msg)
        # send acknowledgement
        client.send(msg_encode(from_addr))


def disconnect_server(client, by):
    client.send(DISCONNECT_MESSAGE.encode(FORMAT))
    if by == "client":
        print_msg(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")
    elif by == "server":
        print_msg(f"[DISCONNECTED] Server disconnected from Client.")
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
        disconnect_server(client, "server")
    except Exception:
        pass


def main():
    global client
    client.connect(ADDR)
    print_msg(f"[CONNECTED] Client connected to {IP}:{PORT}")

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
            print_msg(f"[CURRENT CLIENT] {clients[0]}")
            for c in clients[1:]:
                print_msg(f"[CLIENT] {c}")
            continue

        if to_addr not in clients:
            print_msg(f"[ERROR] Client '{to_addr}' not found.")
            continue

        file_name = input_msg("(file)> ").strip()
        send_file(client, to_addr, file_name)

    disconnect_server(client, "client")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        disconnect_server(client, "client")