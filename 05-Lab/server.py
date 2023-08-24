import socket
import threading
import os
import time
import readline
from urllib.parse import quote, unquote
from dataclasses import dataclass

# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 53535
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

# MSG Format:
#   MSG/<msg>
#   CREATE/<file_name>
#   POST/<file_name>/<file_content>
#   GET/<file_name>

folder_path = "server/"

clients = []

@dataclass
class Client:
    conn: socket.socket
    addr: str


def find_client(addr):
    for client in clients:
        if client.addr == addr:
            return client
    return None


current_input = ""

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


def send_msg(conn, msg):
    conn.send(f"MSG/{quote(msg)}".encode(FORMAT))


def server_input():
    while True:
        to_addr = input_msg("(ip:port)> ").strip()
        if to_addr == DISCONNECT_MESSAGE:
            raise KeyboardInterrupt
        elif to_addr in ["", "list", "ls"]:
            print_msg("Active clients:")
            for client in clients:
                print_msg(f"  {client.addr}")
            continue

        to_client = find_client(to_addr)
        if to_client is None:
            print_msg(f"Error: Client '{to_addr}' not found.")
            continue

        msg = input_msg("(file_name)> ")
        if msg == DISCONNECT_MESSAGE:
            raise KeyboardInterrupt
        elif msg == "":
            continue

        to_client.conn.send(f"CREATE/{quote(msg)}".encode(FORMAT))


def handle_file_request(client, request, body):
    if request == "CREATE":
        file_name = unquote(body)
        file_path = folder_path + file_name
        print_msg(f"[{client.addr}] Create file '{file_name}'")
        with open(file_path, "w"):
            msg = f"File name recieved"
            send_msg(client.conn, msg)
            time.sleep(0.1)
            client.conn.send(f"GET/{quote(file_name)}".encode(FORMAT))

    elif request == "POST":
        file_name, file_content = map(unquote, body.split("/", 1))
        file_path = folder_path + file_name
        print_msg(f"[{client.addr}] Contents of '{file_name}': {file_content}")
        with open(file_path, "a") as f:
            f.write(file_content)
            f.write("\n")
            msg = f"File contents of '{file_name}' recieved"
            send_msg(client.conn, msg)

    elif request == "GET":
        file_name = unquote(body)
        file_path = folder_path + file_name
        try:
            with open(file_path, "r") as f:
                file_content = f.read()
                client.conn.send(f"POST/{quote(file_name)}/{quote(file_content)}".encode(FORMAT))
        except Exception as e:
            err = f"Error: {e}"
            print_msg(err)
            send_msg(client.conn, err)

    else:
        send_msg(client.conn, f"Error: Invalid request '{request}'.")


def handle_client(conn, addr):
    print_msg(f"[NEW CONNECTION] {addr} connected.")

    while True:
        msg = conn.recv(SIZE).decode(FORMAT)
        if not msg or msg == DISCONNECT_MESSAGE:
            break

        try:
            request, body = msg.split("/", 1)
        except Exception as e:
            err = "Error: Invalid request format."
            print_msg(f"[{addr}] {err}")
            send_msg(conn, err)
            continue

        if request == "MSG":
            print_msg(f"[{addr}] {unquote(body)}")
            continue

        try:
            handle_file_request(find_client(addr), request, body)
        except Exception as e:
            err = f"Error: {e}"
            print_msg(f"[{addr}] {err}")
            send_msg(conn, err)
            continue

    conn.close()
    clients.remove(Client(conn, addr))
    print_msg(f"[DISCONNECTED] {addr} disconnected.")
    print_msg(f"[ACTIVE CONNECTIONS] {threading.active_count()-3}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print_msg(f"[STARTING] Server is listening on {IP}:{PORT}")

    server_input_thread = threading.Thread(target=server_input)
    server_input_thread.start()

    while True:
        conn, addr = server.accept()
        addr = f"{addr[0]}:{addr[1]}"

        clients.append(Client(conn, addr))

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        print_msg(f"[ACTIVE CONNECTIONS] {threading.active_count()-2}")

if __name__ == "__main__":
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    print_msg(f"[SERVER] Keep the files to send/recieve inside folder: '{folder_path}'")
    try:
        main()
    except KeyboardInterrupt:
        print_msg("\n[EXITING] Server is shutting down...")
        for client in clients:
            client.conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
            # client.conn.close()
        os._exit(0)