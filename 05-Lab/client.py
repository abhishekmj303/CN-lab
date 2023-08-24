import socket
import threading
import os
import time
import readline
from urllib.parse import quote, unquote

IP = socket.gethostbyname(socket.gethostname())
# IP = "172.16.19.141"
# IP = ''
PORT = 53535
# PORT = 8006
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = True

# MSG Format:
#   MSG/<msg>
#   CREATE/<file_name>
#   POST/<file_name>/<file_content>
#   GET/<file_name>

folder_path = "client/"

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


def handle_file_request(request, body):
    if request == "CREATE":
        file_name = unquote(body)
        file_path = folder_path + file_name
        print_msg(f"[SERVER] Create file '{file_name}'")
        with open(file_path, "w"):
            msg = f"File name recieved"
            send_msg(client, msg)
            time.sleep(0.1)
            client.send(f"GET/{quote(file_name)}".encode(FORMAT))

    elif request == "POST":
        file_name, file_content = map(unquote, body.split("/", 1))
        file_path = folder_path + file_name
        print_msg(f"[SERVER] Contents of '{file_name}': {file_content}")
        with open(file_path, "a") as f:
            f.write(file_content)
            f.write("\n")
            msg = f"File contents of '{file_name}' recieved"
            send_msg(client, msg)

    elif request == "GET":
        file_name = unquote(body)
        file_path = folder_path + file_name
        try:
            with open(file_path, "r") as f:
                file_content = f.read()
                client.send(f"POST/{quote(file_name)}/{quote(file_content)}".encode(FORMAT))
        except Exception as e:
            err = f"Error: {e}"
            print_msg(err)
            send_msg(client, err)

    else:
        send_msg(client, f"Error: Invalid request '{request}'.")


def handle_server():
    global connected
    while connected:
        msg = client.recv(SIZE).decode(FORMAT)
        if not msg or msg == DISCONNECT_MESSAGE:
            connected = False
            break
        
        try:
            request, body = msg.split("/", 1)
        except Exception as e:
            err = "Error: Invalid request format."
            print_msg(err)
            send_msg(client, err)
            continue

        if request == "MSG":
            print_msg(f"[SERVER] {unquote(body)}")
            continue

        try:
            handle_file_request(request, body)
        except Exception as e:
            err = f"Error: {e}"
            print_msg(err)
            send_msg(client, err)
            continue

    client.close()
    print_msg(f"[DISCONNECTED] Server disconnected from Client.")
    os._exit(0)

def main():
    client.connect(ADDR)

    print_msg(f"[CONNECTED] Client connected to {IP}:{PORT}")

    server_thread = threading.Thread(target=handle_server)
    server_thread.start()

    global connected
    while connected:
        msg = input_msg("(file_name)> ").strip()
        if msg == DISCONNECT_MESSAGE:
            break

        client.send(f"CREATE/{quote(msg)}".encode(FORMAT))

    client.close()
    print_msg(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")

if __name__ == "__main__":
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    print_msg(f"[CLIENT] Keep the files to send/recieve inside folder: '{folder_path}'")
    try:
        main()
    except KeyboardInterrupt:
        client.close()
        print_msg("\n[CLIENT] Client is shutting down...")
        os._exit(0)