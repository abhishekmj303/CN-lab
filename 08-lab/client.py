# ClientProgram: client.py

import socket
import threading
import os
import re
from getmac import get_mac_address

import pygame
from pong4 import *
import tkinter as tk
from tkinter import messagebox

IP = socket.gethostbyname(socket.gethostname())
# IP = '192.168.12.219'
PORT = 53533
ADDR = (IP, PORT)
SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "QUIT!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
player = 0
connected = False


def game_entry():
    def register():
        try:
            mac = get_mac_entry()
        except ValueError as e:
            print(f"Registration Failed: {e}")
            messagebox.showerror("Registration Failed", e)
            return
        client.send(f"REGISTER/{mac};".encode(FORMAT))
        msg = recv_msg(client)
        if msg == "OK":
            print(f"Registered MAC Address: {mac}")
            messagebox.showinfo("Registration Successful", f"Registered MAC Address: {mac}")
        else:
            print(f"Registration Failed: {msg}")
            messagebox.showerror("Registration Failed", f"Registration Failed: {msg}")
    
    def login():
        try:
            mac = get_mac_entry()
        except ValueError as e:
            print(f"Login Failed: {e}")
            messagebox.showerror("Login Failed", e)
            return
        client.send(f"LOGIN/{mac};".encode(FORMAT))
        msg = recv_msg(client)
        if msg == "OK":
            print(f"Logged in with MAC Address: {mac}")
            start_tk.destroy()
        else:
            print(f"Login Failed: {msg}")
            messagebox.showerror("Login Failed", f"Login Failed: {msg}")
    
    def pay():
        try:
            mac = get_mac_entry()
            amount = get_amount_entry()
        except ValueError as e:
            print(f"Payment Failed: {e}")
            messagebox.showerror("Payment Failed", e)
            return 
        client.send(f"PAY/{mac}/{amount};".encode(FORMAT))
        msg = recv_msg(client)
        if msg == "OK":
            print(f"Paid {amount} for MAC Address: {mac}")
            messagebox.showinfo("Payment Successful", f"Paid {amount} for MAC Address: {mac}")
        else:
            print(f"Payment Failed: {msg}")
            messagebox.showerror("Payment Failed", f"Payment Failed: {msg}")

    def get_mac_entry():
        mac = mac_entry.get()
        # regex for mac
        mac_regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if re.match(mac_regex, mac):
            return mac.replace("-", ":")
        else:
            raise ValueError(f"Invalid MAC Address: {mac}")
    
    def get_amount_entry():
        amount = amount_entry.get()
        # regex for amount
        amount_regex = r"^[1-9]\d*$"
        if re.match(amount_regex, amount):
            return amount
        else:
            raise ValueError(f"Invalid Amount: {amount}")

    def end_tk():
        start_tk.destroy()
        disconnect_server(client, "client")
        

    start_tk = tk.Tk()
    start_tk.title("Game Registration/Login")

    # Create a label and entry widget for MAC Address
    mac_label = tk.Label(start_tk, text="MAC Address:")
    mac_label.grid(row=0, column=0)
    mac_entry = tk.Entry(start_tk)
    mac_entry.grid(row=0, column=1)

    mac_entry.insert(0, get_mac_address())

    # Create a label and entry widget for payment amount
    amount_label = tk.Label(start_tk, text="Amount (100/min):")
    amount_label.grid(row=2, column=0)
    amount_entry = tk.Entry(start_tk)
    amount_entry.grid(row=2, column=1)

    amount_entry.insert(0, "100")

    # Create Pay button
    pay_button = tk.Button(start_tk, text="Pay", command=pay)

    # Create Register and Login buttons
    register_button = tk.Button(start_tk, text="Register", command=register)
    login_button = tk.Button(start_tk, text="Login", command=login)

    register_button.grid(row=1, column=0, columnspan=2)
    pay_button.grid(row=3, column=0, columnspan=2)
    login_button.grid(row=4, column=0, columnspan=2)

    start_tk.protocol("WM_DELETE_WINDOW", end_tk)

    start_tk.mainloop()


def disconnect_server(client: socket.socket, recv_from: str):
    global connected
    connected = False
    client.send(DISCONNECT_MESSAGE.encode(FORMAT))
    if recv_from == "client":
        print(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")
    elif recv_from == "server":
        print(f"[DISCONNECTED] Server disconnected from Client.")
    client.close()
    # os._exit(0)


def recv_msg(client: socket.socket, disconnect_info: str = ""):
    msg = client.recv(SIZE).decode(FORMAT)
    if msg == DISCONNECT_MESSAGE:
        print(disconnect_info)
        disconnect_server(client, "server")
    return msg


def update_loop():
    global gs, connected
    prev_paused = False
    while True:
        try:
            client.send("GET;".encode(FORMAT))

            msg = recv_msg(client)

            gs.from_json(msg)
            # pltime = {1: gs.p1time, 2: gs.p2time, 3: gs.p3time, 4: gs.p4time}
            # print(f"[TIME] Player {player} time: {pltime[player]}")
        except (BrokenPipeError, ConnectionResetError):
            print(f"[EXCEPTION] Connection error: Server not connected")
            os._exit(0)
        except json.decoder.JSONDecodeError:
            print("[EXCEPTION] JSON Decode Error")
            continue

        if gs.paused:
            screen.blit(
                font.render("Waiting for other players...", True, WHITE), 
                (gs.W//2-150,gs.H//2)
            )
            pygame.display.flip()
            prev_paused = True
            continue

        # if prev_paused and not gs.paused:
        #     prev_paused = False
        #     game_countdown()

        screen.fill(BLACK)

        tag_pos = 50 if gs.FourPlayers else 5
        screen.blit(
            font.render(f"{pl[player]} Player", True, WHITE), 
            (gs.W//2-65,tag_pos)
        )

        drawscore(screen, font, gs.H, gs.FourPlayers, gs)
        drawtimer(screen, font, gs.H, gs.FourPlayers, gs)
        drawball(screen, gs.bx, gs.by, gs.bw)

        drawpaddle(screen,
                   gs.p1x, gs.p1y, 
                   gs.paddle_width_v, gs.paddle_height_v, 
                   py1_Color
        ) 
        drawpaddle(screen,
                   gs.p2x, gs.p2y, 
                   gs.paddle_width_v, gs.paddle_height_v, 
                   py2_Color
        )

        if gs.FourPlayers:
            drawpaddle(screen,
                       gs.p3x, gs.p3y, 
                       gs.paddle_width_h, gs.paddle_height_h, 
                       py3_Color
            )
            drawpaddle(screen,
                       gs.p4x, gs.p4y, 
                       gs.paddle_width_h, gs.paddle_height_h, 
                       py4_Color
            )
        
        pygame.display.flip()

        if gs.winner != 0:
            screen.blit(
                font.render(f"{pl[gs.winner]} Player Wins!", True, WHITE), 
                (gs.W//2-100,gs.H//2)
            )
            if gs.winner == player:
                screen.blit(
                    font.render("You Win!", True, WHITE), 
                    (gs.W//2-50,gs.H//2-50)
                )
            else:
                screen.blit(
                    font.render("You Lose!", True, WHITE), 
                    (gs.W//2-50,gs.H//2-50)
                )
            pygame.display.flip()
            break
        # pygame.time.wait(wt)
    disconnect_server(client, "client")
    connected = False


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

    while connected:
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
    global client, player, gs, connected

    client.connect(ADDR)
    connected = True
    print(f"[CONNECTED] Client connected to {IP}:{PORT}")

    game_entry()

    # Player number
    while True:
        msg = recv_msg(client)
        player = int(msg)
        print(f"[PLAYER] Player {player}")

        screen.fill(BLACK)
        pygame.display.flip()
        if player == -1:
            print("[SERVER] Server full.")
            screen.blit(
                font.render("Server full.", True, WHITE), 
                (gs.W//2-80,gs.H//2)
            )
            pygame.display.flip()
        else:
            break

    # update_thread = threading.Thread(target=update_loop)
    # update_thread.start()

    # game_loop()

    game_thread = threading.Thread(target=game_loop)
    game_thread.start()

    update_loop()

    # game_thread.join()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os._exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[EXCEPTION] Keyboard Interrupt.")
        disconnect_server(client, "client")
    except ConnectionRefusedError:
        print(f"[EXCEPTION] Connection Refused: Server not connected.")
    finally:
        os._exit(0)