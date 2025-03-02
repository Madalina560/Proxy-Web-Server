import socket

serverPort = 6040

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 6040))
s.listen(5)
print("Server ready to recieve")

while True: 
    #Establish the connection 
    print('Ready to serve...') 
    connectionSocket, addr = s.accept()
    print(f"Connection established with {addr}")
    try: 
        message =  connectionSocket.recv(1024).decode()
        print("Recieved request:", message)

        filename = message.split()[1][1:]                  
        print(f"Client requested file: {filename}")                    
        
        with open(filename, "rb") as f:
            connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())
            connectionSocket.send("Content type: text/html\r\n\r\n".encode())

            chunk = f.read()
            while chunk:
                connectionSocket.send(chunk)
                chunk = f.read(1024)

    except FileNotFoundError: 
        error_message = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
        connectionSocket.send(error_message.encode())
    
    except Exception as e:
        print("Error:", e)
    
    finally:
        connectionSocket.close()
                     