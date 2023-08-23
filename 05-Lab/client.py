import socket
import threading
import os
import readline

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

def handle_server():
    global connected
    while connected:
        msg = client.recv(SIZE).decode(FORMAT)
        if not msg or msg == DISCONNECT_MESSAGE:
            connected = False
            break
        print_msg(f"[SERVER] {msg}")

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
        for i in range(2):
            if i == 0:
                msg = input_msg("Enter file name (with ext): ")
            else:
                with open(folder_path+msg, "r") as f:
                    msg = f.read()
            client.send(msg.encode(FORMAT))
            if msg == DISCONNECT_MESSAGE:
                break

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