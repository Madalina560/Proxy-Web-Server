import socket

# socket programmed acording to: https://www.youtube.com/watch?v=JNzfG7XMYSg
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 6040))
s.listen(5)

while True:
    clientSocket, address = s.accept()
    print(f"Connecion established from address {address}")
    clientSocket.send(bytes("Welcome to the server!", "utf-8"))
    clientSocket.close()