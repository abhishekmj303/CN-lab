import socket
import threading
import os

import pygame
from pong4 import *

IP = socket.gethostbyname(socket.gethostname())
# IP = '192.168.2.24'
PORT = 53535
ADDR = (IP, PORT)
SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
player = 0
pl = {1: "Left", 2: "Right", 3: "Top", 4: "Bottom"}


def disconnect_server(client: socket.socket, recv_from: str):
    client.send(DISCONNECT_MESSAGE.encode(FORMAT))
    if recv_from == "client":
        print(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")
    elif recv_from == "server":
        print(f"[DISCONNECTED] Server disconnected from Client.")
    client.close()
    os._exit(0)


def update_loop():
    global gs
    while True:
        try:
            client.send("GET;".encode(FORMAT))

            msg = client.recv(SIZE).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                disconnect_server(client, "server")

            gs = GameState.from_json(msg)
        except (BrokenPipeError, ConnectionResetError):
            print(f"[EXCEPTION] Connection error: Server not connected")
            os._exit(0)
        except json.decoder.JSONDecodeError:
            print("[EXCEPTION] JSON Decode Error")
            continue

        screen.fill(BLACK)

        tag_pos = 50 if gs.FourPlayers else 5
        screen.blit(font.render(f"{pl[player]} Player", True, WHITE), (gs.W//2-65,tag_pos))
        drawscore(screen, font, gs.H, gs.FourPlayers, gs)
        drawball(screen, gs.bx, gs.by, gs.bw)

        drawpaddle(screen,gs.p1x, gs.p1y, gs.paddle_width_v, gs.paddle_height_v, py1_Color) 
        drawpaddle(screen,gs.p2x, gs.p2y, gs.paddle_width_v, gs.paddle_height_v, py2_Color)

        if gs.FourPlayers:
            drawpaddle(screen,gs.p3x, gs.p3y, gs.paddle_width_h, gs.paddle_height_h, py3_Color)
            drawpaddle(screen,gs.p4x, gs.p4y, gs.paddle_width_h, gs.paddle_height_h, py4_Color)
        
        pygame.display.flip()
        # pygame.time.wait(wt)


def game_loop():
    global gs, client

    keys = {
        pygame.K_w: "left",
        pygame.K_s: "right",
        pygame.K_UP: "left",
        pygame.K_DOWN: "right",
        pygame.K_a: "left",
        pygame.K_d: "right",
        pygame.K_LEFT: "left",
        pygame.K_RIGHT: "right",
    }

    while True:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    disconnect_server(client, "client")
                if event.type == pygame.KEYDOWN:
                    if event.key in keys:
                        key = keys[event.key]
                        client.send(f"{key}:down;".encode(FORMAT))
                elif event.type == pygame.KEYUP:
                    if event.key in keys:
                        key = keys[event.key]
                        client.send(f"{key}:up;".encode(FORMAT))
        except BrokenPipeError:
            print(f"[EXCEPTION] Broken pipe error: Server not connected")
            os._exit(0)
        # pygame.time.wait(wt)


def main():
    # connect to server
    global client, player, gs

    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to {IP}:{PORT}")

    msg = client.recv(SIZE).decode(FORMAT)
    if msg == DISCONNECT_MESSAGE:
        print(f"Game is full.")
        disconnect_server(client, "server")
    
    player = int(msg)
    print(f"[PLAYER] Player {player}")

    update_thread = threading.Thread(target=update_loop)
    update_thread.start()

    game_loop()

    disconnect_server(client, "client")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[EXCEPTION] Keyboard Interrupt.")
        disconnect_server(client, "client")
    except ConnectionRefusedError:
        print(f"[EXCEPTION] Connection Refused: Server not connected.")
        os._exit(0)