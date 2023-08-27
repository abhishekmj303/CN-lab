import socket
import threading
import os
import time
import readline
from urllib.parse import quote, unquote # for encoding/decoding data in url format

IP = socket.gethostbyname(socket.gethostname())
# IP = "172.16.19.141"
# IP = ''
PORT = 53535
# PORT = 8006
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create client socket
connected = True # flag to check if client is connected to server

# MSG Format:
#   MSG/<msg>
#   CREATE/<file_name>
#   POST/<file_name>/<file_content>
#   GET/<file_name>

folder_path = "client/" # folder to store files for client

current_prompt = "" # store current prompt of input

def print_msg(msg):
    if not current_prompt:
        print(msg)
    else:
        input_buffer = readline.get_line_buffer() # store current input buffer
        print(f"\r{msg}\n{current_prompt}{input_buffer}", end="", flush=True) # print message and restore input buffer


def input_msg(string):
    global current_prompt

    # set current prompt and take input
    current_prompt = string
    result = input(f"\r{string}")
    current_prompt = ""

    return result


# send message to server
def send_msg(conn, msg):
    conn.send(f"MSG/{quote(msg)}".encode(FORMAT))


# handle file requests from server
def handle_file_request(request, body):
    # CREATE/<file_name>
    if request == "CREATE":
        file_name = unquote(body) # decode file name
        file_path = folder_path + file_name
        print_msg(f"[SERVER] Create file '{file_name}'")
        with open(file_path, "w"): # create file
            msg = f"File name recieved"
            send_msg(client, msg) # send acknowledgement to server
            time.sleep(0.1)
            client.send(f"GET/{quote(file_name)}".encode(FORMAT)) # send GET request to server to get file contents

    # POST/<file_name>/<file_content>
    elif request == "POST":
        file_name, file_content = map(unquote, body.split("/", 1)) # decode file name and file content
        file_path = folder_path + file_name
        print_msg(f"[SERVER] Contents of '{file_name}': {file_content}")
        with open(file_path, "a") as f:
            f.write(file_content) # write file content to file
            msg = f"File contents of '{file_name}' recieved"
            send_msg(client, msg) # send acknowledgement to server

    # GET/<file_name>
    elif request == "GET":
        file_name = unquote(body) # decode file name
        file_path = folder_path + file_name
        try:
            with open(file_path, "r") as f: # read file contents
                file_content = f.read()
                client.send(f"POST/{quote(file_name)}/{quote(file_content)}".encode(FORMAT)) # send file contents to server
        except Exception as e: # if file not found
            err = f"Error: {e}"
            print_msg(err)
            send_msg(client, err)

    else:
        send_msg(client, f"Error: Invalid request '{request}'.")


def handle_server():
    global connected
    while connected:
        msg = client.recv(SIZE).decode(FORMAT) # recieve message from server
        if not msg or msg == DISCONNECT_MESSAGE:
            connected = False
            end_client()
        
        try:
            request, body = msg.split("/", 1) # split request and body
        except Exception as e: # if invalid request format
            err = "Error: Invalid request format."
            print_msg(err)
            send_msg(client, err)
            continue

        if request == "MSG": # if message request
            print_msg(f"[SERVER] {unquote(body)}")
            continue

        try: # handle file request
            handle_file_request(request, body)
        except Exception as e: # if error occured while handling file request
            err = f"Error: {e}"
            print_msg(err)
            send_msg(client, err)
            continue

    client.close() # close connection
    print_msg(f"[DISCONNECTED] Server disconnected from Client.")
    os._exit(0)

def main():
    client.connect(ADDR) # connect to server

    print_msg(f"[CONNECTED] Client connected to {IP}:{PORT}")

    server_thread = threading.Thread(target=handle_server)
    server_thread.start() # start thread to handle server

    global connected
    while connected:
        msg = input_msg("(file_name)> ").strip() # take input from user
        if msg == DISCONNECT_MESSAGE:
            end_client()

        client.send(f"CREATE/{quote(msg)}".encode(FORMAT)) # send CREATE request to server

    client.close() # close connection
    print_msg(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")


def end_client():
    client.close() # close connection
    print_msg("\n[CLIENT] Client is shutting down...")
    os._exit(0)

if __name__ == "__main__":
    if not os.path.exists(folder_path): # create folder if not exists
        os.makedirs(folder_path)
    print_msg(f"[CLIENT] Keep the files to send/recieve inside folder: '{folder_path}'")
    try:
        main()
    except KeyboardInterrupt: # if client is stopped
        end_client()