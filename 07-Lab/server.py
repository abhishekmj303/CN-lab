import socket
import threading
import os
from dataclasses import dataclass

import pygame
from pong4 import *

# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 53535
ADDR = (IP, PORT)
SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

clients = [] # list of clients connected to the server

@dataclass
class Client:
    '''Client class to store client information'''
    conn: socket.socket
    addr: str
    player: int


def get_next_player():
    all_players = sorted([c.player for c in clients])
    player = 1
    for p in all_players:
        if p == player:
            player += 1
        else:
            break
    return player

def disconnect_client(client: Client):
    '''Disconnect client'''
    print(f"[DISCONNECT CLIENT] {client.addr} disconnected.")
    print(f"[ACTIVE CLIENTS] {threading.active_count() - 3}")

    clients.remove(client)
    client.conn.close()


def handle_msg(client: Client, msg: str):
    print(f"[{client.addr}] {msg}")
    if "GET" in msg:
        client.conn.send(gs.toJSON().encode(FORMAT))
    else:
        key, press = msg.split(":")
        keys_map = {
            1: {
                "left": pygame.K_w,
                "right": pygame.K_s,
            },
            2: {
                "left": pygame.K_UP,
                "right": pygame.K_DOWN,
            },
            3: {
                "left": pygame.K_a,
                "right": pygame.K_d,
            },
            4: {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
            },
        }
        presses_map = {
            "down": pygame.KEYDOWN,
            "up": pygame.KEYUP,
        }
        pygame.event.post(pygame.event.Event(
            presses_map[press],
            key=keys_map[client.player][key],
        ))


def handle_client(client: Client):
    addr = client.addr
    conn = client.conn
    print(f"[NEW CLIENT] {addr} connected.")

    conn.send(f"{client.player}".encode(FORMAT))

    while True: # recieve message from client
        from_msg = conn.recv(SIZE).decode(FORMAT)
        if from_msg == DISCONNECT_MESSAGE:
            break
        elif not from_msg:
            continue

        try: # handle recieved message
            while ";" in from_msg:
                msg, from_msg = from_msg.split(";", 1)
                handle_msg(client, msg)
        except Exception as e:
            print(f"[ERROR] {e}")

    try:
        disconnect_client(client)
    except Exception as e:
        pass

def server_loop():
    print(f"[STARTING] Server is starting...")

    # create socket, bind to address, and listen
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    print(f"[ACTIVE CLIENTS] {threading.active_count() - 2}")
    
    while True: # accept new connection
        conn, addr = server.accept()
        addr = f"{addr[0]}:{addr[1]}"

        if ((len(clients) >= 4 and gs.FourPlayers) or 
            (len(clients) >= 2 and not gs.FourPlayers)):
            conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
            continue

        current_client = Client(conn, addr, get_next_player())
        clients.append(current_client)

        # start new thread to handle client
        thread = threading.Thread(target=handle_client, args=(current_client,))
        thread.start()
        
        print(f"[ACTIVE CLIENTS] {threading.active_count() - 2}")



def main():
    game_thread = threading.Thread(target=game_loop)
    game_thread.start()

    server_loop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt: # handle keyboard interrupt
        print("\n[EXITING] Server is shutting down...")
        for client in clients: # send disconnect message to all clients
            client.conn.close()
        os._exit(0)
    except OSError as e:
        print(f"[ERROR] {e}")
        os._exit(0)