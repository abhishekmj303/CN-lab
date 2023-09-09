# Abhishek M J - CS21B2018
# client.py

import socket
import threading
import os
import readline
import time
# to url_encode and decode
import urllib.parse

IP = socket.gethostbyname(socket.gethostname())
# IP = ''
PORT = 53533
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

# create client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

folder_path = "client/" # folder to store files for client

clients = [] # list of clients connected to the server


class FileNotSent(Exception):
    '''Exception raised when file is not sent'''
    pass


current_prompt = "" # current input prompt


def print_msg(msg: str):
    '''Print message without overwriting current input prompt'''
    if not current_prompt:
        print(msg)
    else:
        input_buffer = readline.get_line_buffer()
        print(f"\r{msg}\n{current_prompt}{input_buffer}", end="", flush=True)


def input_msg(string: str):
    '''Same as input() but stores current input prompt while taking input'''
    global current_prompt

    current_prompt = string
    result = input(f"\r{string}")
    current_prompt = ""

    return result


def msg_encode(msg: str, to_addr: str = None) -> bytes:
    '''
    Encode message to be sent to client:

    MSG FORMAT: <to_addr>/<msg>
    '''
    msg = urllib.parse.quote(msg)
    if to_addr is None:
        to_msg = f"SERVER/{msg}"
    else:
        to_msg = f"{to_addr}/{msg}"
    return to_msg.encode(FORMAT)


def send_file(client: socket.socket, to_addr: str, file_path: str):
    '''
    Send file to another client through server:
    1. Send file name to to_client: <to_addr>/<file_name>
    2. Send file data in raw bytes
    3. Send EOF to indicate end of file
    '''
    if not os.path.exists(file_path):
        print_msg(f"[ERROR] File '{file_path}' not found.")
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


def recieve_file(client: socket.socket, file_name: str):
    '''
    Recieve file from another client through server:
    1. Recieve file data in raw bytes
    2. Write file data to file
    3. Recieve EOF to indicate end of file
    '''
    file_path = folder_path + file_name
    with open(file_path, "wb") as f:
        bin_data = client.recv(SIZE)
        while bin_data != b"EOF":
            f.write(bin_data)
            bin_data = client.recv(SIZE)


def handle_msg(from_msg: str, client: socket.socket):
    '''
    Handle message recieved from server:
    1. File transfer: <from_addr>/<file_name>
    2. Acknowledgement: SERVER/<from_addr>
    3. Client online: SERVER/<client_addr>+
    4. Client offline: SERVER/<client_addr>-
    '''
    try:
        from_addr, msg = from_msg.strip().split("/")
        msg = urllib.parse.unquote(msg)
    except ValueError:
        raise FileNotSent(f"Invalid message format: {from_msg}")
    
    # Check if broadcast
    if from_addr == "SERVER":
        if msg[-1] == "+": # if client online
            if len(clients) == 0: # first client is current client
                print_msg(f"[CURRENT CLIENT] {msg[:-1]}")
                global folder_path
                folder_path = msg[:-1] + "/"
                if not os.path.exists(folder_path): # create folder if not exists
                    os.makedirs(folder_path)
            else:
                print_msg(f"[CLIENT ONLINE] {msg[:-1]} connected.")
            clients.append(msg[:-1])
        elif msg[-1] == "-": # if client offline
            clients.remove(msg[:-1])
            print_msg(f"[CLIENT OFFLINE] {msg[:-1]} disconnected.")
        else: # if acknowledgement
            print_msg(f"[SERVER] {msg}")
    else: # if file transfer
        print_msg(f"[{from_addr}] {msg}")
        recieve_file(client, msg)
        # send acknowledgement
        client.send(msg_encode(from_addr))


def disconnect_server(client: socket.socket, recv_from: str):
    '''
    Disconnect from server, received from "client" or "server":
    '''
    client.send(DISCONNECT_MESSAGE.encode(FORMAT))
    if recv_from == "client":
        print_msg(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")
    elif recv_from == "server":
        print_msg(f"[DISCONNECTED] Server disconnected from Client.")
    client.close()
    os._exit(0)


def handle_server(client: socket.socket):
    '''
    Handle server:
    1. Recieve message from server
    2. Handle message
    '''
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
        except FileNotSent as e:
            print_msg(f"[ERROR] {e}")

    try:
        disconnect_server(client, "server")
    except Exception:
        pass


def main():
    # connect to server
    global client
    client.connect(ADDR)
    print_msg(f"[CONNECTED] Client connected to {IP}:{PORT}")

    # start server thread to handle messages from server
    server_thread = threading.Thread(target=handle_server, args=(client,))
    server_thread.start()

    connected = True
    while connected: # send file to other clients
        to_addr = input_msg("(ip:port)> ").strip() # get client address

        if to_addr == DISCONNECT_MESSAGE:
            connected = False
            disconnect_server(client, "client")

        elif to_addr.lower() in ["", "l", "list"]: # list all clients
            print_msg(f"[ONLINE CLIENT LIST] {len(clients)} clients connected.")
            print_msg(f"[CURRENT CLIENT] {clients[0]}")
            for c in clients[1:]:
                print_msg(f"[CLIENT] {c}")
            continue

        if to_addr not in clients:
            print_msg(f"[ERROR] Client '{to_addr}' not found.")
            continue

        file_path = input_msg("(file)> ").strip() # get file path
        send_file(client, to_addr, file_path)

    disconnect_server(client, "client")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt: # handle keyboard interrupt
        disconnect_server(client, "client")