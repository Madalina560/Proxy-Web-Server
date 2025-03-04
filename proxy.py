import socket
import threading

Host = '127.0.0.1'
Port = 8080
blocked = set() # for blocking URLs

def handle(client:socket.socket):
    try:
        request = client.recv(1024) # recieve data 1024 bytes at a time
        if not request:
            client.close() # close if no data
            return
        
        host, port = getAddressInfo(request) # extract host + port number
        if not host:
            client.close() # close if host isn't present
            return
        
        if host in blocked:
            print(f"Blocked request to {host}")
            client.close() # close connection if host is blocked
            return

        if port == 443:
            handleHTTPS(client, host, port) # handles HTTPS requests
        else:
            handleHTTP(client, request, host, port) # handles HTTP requests
        
    except Exception as e:
        print(f"Error handling request: {e}") # gives back any errors that may occur
    finally:
        client.close() # close socket once finished


def getAddressInfo(request):
    try:
        headers = request.decode(errors = "ignore") # decode incoming request
        start = headers.find("Host: ") # extract start of request
        if start == -1:
            return None, None # return nothing if no start

        start += len("Host: ")
        end = headers.find("\r\n", start) # find carriage return
        if end == -1:
            return None, None # return nothing if no carriage return

        host = headers[start:end].strip() # combine start of request & carriage return
        if ":" in host:
            host, port = host.split(":") # extract port #
            port = int(port) # cast to int
        else:
            port = 80 # default HTTP port
        return host, port
    except Exception as e:
        print(f"Error parsing headers: {e}") # gives back any errors that may occur
        return None, None

def handleHTTP(client:socket.socket, request, host, port):
    try:
        webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up socket
        webSocket.connect((host, port))
        webSocket.sendall(request)

        while True:
            response = webSocket.recv(1024) # recieve data 1024 bytes at a time
            if not response:
                break # exit if no response
            client.sendall(response) # send through all data
            #print(f"HTTP Host: {host}") # for testing purposes
    except Exception as e:
        print(f"Error forwarding HTTP request: {e}") # gives back any errors that may occur
    finally:
        webSocket.close() # close socket once finished

def handleHTTPS(client:socket.socket, host, port):
    try:
        client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n") # send handshake

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as webSocket: # set up socket
            webSocket.connect((host, port))

            client.setblocking(False) # set blocking flag off
            webSocket.setblocking(False) #set blocking flag off

            while True:
                try:
                    data = client.recv(1024) # recieve data 1024 bytes at a time
                    if not data:
                        break # exit if no data
                    webSocket.sendall(data) # send all data otherwise
                    #print(f"1. HTTPS Host: {host}") # for testing purposes
                except BlockingIOError:
                    pass # skip over

                try:
                    data = webSocket.recv(1024) # recieve data 1024 bytes at a time
                    if not data:
                        break # exit if no data
                    client.sendall(data) # send all data otherwise
                    #print(f"2. HTTPS Host: {host}") # for testing purposes
                except BlockingIOError:
                    pass # skip over
    
    except Exception as e:
        print(f"Error handling HTTPS: {e}") # gives back any errors that may occur

def blockURL():
    print("\tWelcome to WhiskerProx, a Python proxy server")
    print("----------------------------------------------------- •<:30~\n")
    print(f"\tCurrently listening on: {Host}:{Port}\n")
    print("----------------------------------------------------- •<:30~\n") # management console

    while True:
        userInput = input("Enter CMD (/block | /unblock): ").lower() # get cmd input from user
        if "/block" in userInput:
            blocked.add(userInput[userInput.find("www."):]) # block URL
            print(f"BLOCKED: {(userInput[userInput.find("www."):])}")

        elif "/unblock" in userInput:
            if (userInput[userInput.find("www."):]) in blocked:
                blocked.remove(userInput[userInput.find("www."):]) # if already blocked, unblock URL
                print(f"UNBLOCKED: {(userInput[userInput.find("www."):])}")
            else:
                print("ERROR: ", (userInput[userInput.find("www."):]), " not in Blocked URLs") # don't unblock, as not blocked before

        else:
            print("ERROR: CMD not recognised") # in case user mis-inputs

def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up proxy socket
    s.bind(('127.0.0.1', Port))
    s.listen(5)

    blockURLS = threading.Thread(target=blockURL, args=())
    blockURLS.start() # start management console with threads
    
    while True:
        client, addr = s.accept() # accept incoming connection
        print(f"Connection established with {addr}")
        thread = threading.Thread(target= handle, args=(client,))
        thread.start() # handle multiple requests

if __name__ == "__main__":
    start()

