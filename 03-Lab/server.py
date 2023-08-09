import socket
import threading

# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 53536
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

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

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()