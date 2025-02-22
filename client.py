import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 6040))

msg = s.recv(2048)

print(f"Message recieved: {msg}")