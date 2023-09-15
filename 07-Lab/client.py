import socket
import threading
import os

import pygame
from pong4 import *

IP = socket.gethostbyname(socket.gethostname())
# IP = ''
PORT = 53533
ADDR = (IP, PORT)
SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
player = 0


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
            client.send("GET".encode(FORMAT))

            msg = client.recv(SIZE).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                disconnect_server(client, "server")

            gs = GameState.from_json(msg)
        except BrokenPipeError:
            print(f"[EXCEPTION] Broken pipe error: Server not connected")
            os._exit(0)

        screen.fill(BLACK)

        drawscore(screen, font, gs.H, gs.FourPlayers)
        drawball(screen, gs.bx, gs.by, gs.bw)

        drawpaddle(screen,gs.p1x, gs.p1y, gs.paddle_width_v, gs.paddle_height_v, py1_Color) 
        drawpaddle(screen,gs.p2x, gs.p2y, gs.paddle_width_v, gs.paddle_height_v, py2_Color)

        if gs.FourPlayers:
            drawpaddle(screen,gs.p3x, gs.p3y, gs.paddle_width_h, gs.paddle_height_h, py3_Color)
            drawpaddle(screen,gs.p4x, gs.p4y, gs.paddle_width_h, gs.paddle_height_h, py4_Color)
        
        pygame.display.flip()
        pygame.time.wait(wt)


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
                        client.send(f"{key}:down".encode(FORMAT))
                elif event.type == pygame.KEYUP:
                    if event.key in keys:
                        key = keys[event.key]
                        client.send(f"{key}:up".encode(FORMAT))
        except BrokenPipeError:
            print(f"[EXCEPTION] Broken pipe error: Server not connected")
            os._exit(0)
        pygame.time.wait(wt)


def main():
    # connect to server
    global client, player, gs

    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to {IP}:{PORT}")

    player = int(client.recv(SIZE).decode(FORMAT))
    print(f"[PLAYER] Player {player}")

    game_thread = threading.Thread(target=game_loop)
    game_thread.start()

    update_thread = threading.Thread(target=update_loop)
    update_thread.start()

    game_thread.join()
    update_thread.join()

    disconnect_server(client, "client")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[EXCEPTION] Keyboard Interrupt.")
        disconnect_server(client, "client")