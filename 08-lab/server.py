# ServerProgram: server.py

import socket
import threading
import os
import time
from dataclasses import dataclass

import pygame
from pong4 import *

# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 53533
ADDR = (IP, PORT)
SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

clients = {} # all registered clients to the server
players = [] # list of players currently playing
queue = [] # list of clients waiting to play

logged_in_macs = []
active_clients = 0

max_players = 4 if gs.FourPlayers else 2
game_price = 60/100 # 60 seconds per 100 rupees

@dataclass
class Client:
    '''Client class to store client information'''
    conn: socket.socket
    addr: str
    player: int
    mac: str = None
    time: float = 0.0
    connected: bool = True


def get_next_player():
    if players_full():
        return -1
    all_players = sorted([c.player for c in players])
    player = 1
    for p in all_players:
        if p == player:
            player += 1
        else:
            break
    return player


def players_full():
    return len(players) >= max_players


def disconnect_client(client: Client):
    '''Disconnect client'''
    global gs, active_clients
    print(f"[DISCONNECT CLIENT] {client.addr} disconnected.")

    active_clients -= 1
    print(f"[ACTIVE CLIENTS] {active_clients}")

    if client in players:
        gs.paused = True
        players.remove(client)
    else:
        queue.remove(client)
    client.connected = False
    try:
        logged_in_macs.remove(client.mac)
        client.conn.close()
    except:
        pass


def start_next_game():
    global gs
    gs.reset()
    gs.paused = True

    players.clear()
    while len(queue) > 0 and not players_full():
        c = queue.pop(0)
        c.player = get_next_player()
        players.append(c)
        c.conn.send(f"{c.player}".encode(FORMAT))
    
    if players_full():
        gs.paused = False


def player_timer(client: Client):
    global gs
    while client.connected:
        if gs.paused and client.time > 0:
            time.sleep(0.1)
            continue
        client.time -= 1
        if client.time < 0:
            client.conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
            disconnect_client(client)
            break
        time.sleep(1)


def add_player(client: Client):
    global gs

    logged_in_macs.append(client.mac)

    if players_full():
        client.player = -1
        queue.append(client)
    else:
        client.player = get_next_player()
        players.append(client)
        timer_thread = threading.Thread(target=player_timer, args=(client,))
        timer_thread.start()
    
    client.conn.send(f"{client.player}".encode(FORMAT))

    time.sleep(0.1)
    if players_full():
        gs.paused = False


def handle_msg(client: Client, msg: str):
    print(f"[{client.addr}] {msg}")
    if "GET" in msg:
        global gs
        gs.set_ptime(client.player, client.time)
        client.conn.send(gs.to_json().encode(FORMAT))
    elif "REGISTER" in msg:
        _, mac = msg.split("/")
        if mac in clients:
            client.conn.send("MAC already registered".encode(FORMAT))
        else:
            clients[mac] = client
            client.mac = mac
            client.conn.send("OK".encode(FORMAT))
    elif "LOGIN" in msg:
        _, mac = msg.split("/")
        if mac in logged_in_macs:
            client.conn.send("MAC already logged in".encode(FORMAT))
        elif mac in clients:
            client.mac = mac
            client.time = clients[mac].time
            clients[mac] = client
            client.conn.send("OK".encode(FORMAT))
            time.sleep(0.1)
            add_player(client)
        else:
            client.conn.send("MAC not registered".encode(FORMAT))
    elif "PAY" in msg:
        _, mac, amount = msg.split("/")
        if mac in clients:
            clients[mac].time += int(amount) * game_price
            client.conn.send("OK".encode(FORMAT))
        else:
            client.conn.send("MAC not registered".encode(FORMAT))
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
        handle_events(presses_map[press], keys_map[client.player][key])


def handle_client(client: Client):
    addr = client.addr
    conn = client.conn
    print(f"[NEW CLIENT] {addr} connected.")

    # conn.send(f"{client.player}".encode(FORMAT))

    while client.connected: # recieve message from client
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


def server_broadcast(msg: str):
    for client in clients:
        client.conn.send(msg.encode(FORMAT))


def server_loop():
    global gs, active_clients
    print(f"[STARTING] Server is starting...")

    # create socket, bind to address, and listen
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(ADDR)
    except OSError as e:
        print(f"[ERROR] {e}")
        os._exit(0)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    print(f"[ACTIVE CLIENTS] {active_clients}")

    gs.paused = True
    
    while True: # accept new connection
        conn, addr = server.accept()
        addr = f"{addr[0]}:{addr[1]}"

        # if players_full():
        #     conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
        #     continue

        current_client = Client(conn, addr, 0)
        active_clients += 1

        # start new thread to handle client
        thread = threading.Thread(target=handle_client, args=(current_client,))
        thread.start()
        
        print(f"[ACTIVE CLIENTS] {active_clients}")


def main():
    # game_thread = threading.Thread(target=game_loop, args=(True,))
    # game_thread.start()

    # server_loop()

    server_thread = threading.Thread(target=server_loop)
    server_thread.start()

    global gs, screen
    gs.paused = True

    while True:
        game_loop(True)
        screen.fill(BLACK)
        screen.blit(
            font.render("Starting next game...", True, WHITE), 
            (gs.W//2-100,gs.H//2)
        )
        pygame.display.flip()
        time.sleep(2)
        start_next_game()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt: # handle keyboard interrupt
        print("\n[EXITING] Server is shutting down...")
        for client in players: # send disconnect message to all clients
            client.conn.close()
        for client in queue:
            client.conn.close()
        os._exit(0)
    except OSError as e:
        print(f"[ERROR] {e}")
        os._exit(0)