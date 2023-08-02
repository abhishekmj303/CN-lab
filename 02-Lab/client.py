import socket
import sys

# Create a new socket object
s = socket.socket()
print("Successfully created socket")

# Define port and ip to connect
ip, port = "127.0.0.1", 53530
if len(sys.argv) == 2:
    ip, port = sys.argv[1].split(":")

# Connect to the server
s.connect((ip, int(port)))
print(f"Successfully connected to {ip}:{port}")

# Receive connection confirmation message
print(s.recv(1024).decode())

# Close the connection with the server
s.close()