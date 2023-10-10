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

registered = {} # all registered clients to the server
logged_in = [] # all logged in clients to the server

clients = [] # list of all clients connected to the server
players = [] # list of players currently playing
queue = [] # list of clients waiting to play

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


def next_player_num():
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
    global gs
    print(f"[DISCONNECT CLIENT] {client.addr} disconnected.")

    client.connected = False

    clients.remove(client)
    print(f"[ACTIVE CLIENTS] {len(clients)}")

    if client in players:
        gs.paused = True
        gs.winner = -5
        players.remove(client)
    elif client in queue:
        queue.remove(client)
    try:
        logged_in.remove(client.mac)
        client.conn.close()
    except:
        pass


def setup_next_game():
    global gs
    
    screen.fill(BLACK)
    screen.blit(
        font.render("Starting next game...", True, WHITE), 
        (gs.W//2-100,gs.H//2)
    )
    pygame.display.flip()

    # gs.paused = True
    time.sleep(0.1)

    gs.reset()
    gs.paused = True 

    while len(queue) > 0 and not players_full():
        c = queue.pop(0)
        c.player = next_player_num()
        players.append(c)
        timer_thread = threading.Thread(target=player_timer, args=(c,))
        timer_thread.start()
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
            gs.paused = True
            gs.winner = -client.player
            client.time = 0.0
        else:
            time.sleep(1)
 

def login_player(client: Client):
    global gs

    logged_in.append(client.mac)

    if players_full():
        client.player = -1
        queue.append(client)
    else:
        client.player = next_player_num()
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
        if mac in registered:
            client.conn.send("MAC already registered".encode(FORMAT))
        else:
            registered[mac] = client
            client.mac = mac
            client.conn.send("OK".encode(FORMAT))
    elif "LOGIN" in msg:
        _, mac = msg.split("/")
        if mac in logged_in:
            client.conn.send("MAC already logged in".encode(FORMAT))
        elif mac in registered:
            client.mac = mac
            client.time = registered[mac].time
            if client.time <= 0:
                client.conn.send("No time left, Please pay to continue".encode(FORMAT))
                return
            registered[mac] = client
            client.conn.send("OK".encode(FORMAT))
            time.sleep(0.1)
            login_player(client)
        else:
            client.conn.send("MAC not registered".encode(FORMAT))
    elif "PAY" in msg:
        _, mac, amount = msg.split("/")
        if mac in registered:
            registered[mac].time += round(int(amount) * game_price, 2)
            client.conn.send("OK".encode(FORMAT))
        else:
            client.conn.send("MAC not registered".encode(FORMAT))
    elif "BALANCE" in msg:
        _, mac = msg.split("/")
        if mac in registered:
            client.conn.send(f"OK/{registered[mac].time}".encode(FORMAT))
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

    while client.connected: # recieve message from client
        from_msg = conn.recv(SIZE).decode(FORMAT)
        if from_msg == "QUIT":
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
    for client in registered:
        client.conn.send(msg.encode(FORMAT))


def server_loop():
    global gs
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

    print(f"[ACTIVE CLIENTS] {len(clients)}")

    gs.paused = True
    
    while True: # accept new connection
        conn, addr = server.accept()
        addr = f"{addr[0]}:{addr[1]}"

        current_client = Client(conn, addr, 0)
        clients.append(current_client) 

        # start new thread to handle client
        thread = threading.Thread(target=handle_client, args=(current_client,))
        thread.start()
        
        print(f"[ACTIVE CLIENTS] {len(clients)}")


def main():
    server_thread = threading.Thread(target=server_loop)
    server_thread.start()

    global gs, screen
    gs.paused = True

    while True:
        game_loop(True)
        setup_next_game()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt: # handle keyboard interrupt
        print("\n[EXITING] Server is shutting down...")
        for client in clients:
            client.conn.send("QUIT".encode(FORMAT)) 
            disconnect_client(client)
            # client.conn.close()
        os._exit(0)
    except OSError as e:
        print(f"[ERROR] {e}")
        os._exit(0)