import socket
import sys

# Create a new socket object
s = socket.socket()
print("Successfully created socket")


# Reserve a port on your computer
port = 53530

# IP to Bind
ip = ''
if len(sys.argv) == 2:
    ip = sys.argv[1] # Take ip from command line

# Bind to the port
s.bind((ip, port))
if ip:
    print(f"Successfully binded to {ip}:{port}")
else:
    print(f"Successfully binded to localhost:{port}")


# Put the socket into listening mode
s.listen(5) # Max number of connections
print("Socket is listening")

try:
    while True:
        # Establish connection with client
        c, addr = s.accept()
        print(f"Got connection from {addr}")

        # Send connection confirmation message
        c.send("Connection message sent from python server \n\t\t\t\t\t--Thank You".encode())

        # Close the connection with the client
        c.close()
except KeyboardInterrupt:
    print("Server stopped by the user")
    s.close()
    sys.exit(0)
