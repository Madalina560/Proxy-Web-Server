import socket
import threading

# followed the tutorial at: https://brightdata.com/blog/proxy-101/python-proxy-server

Port = 8080
BLOCKED = set()

def handle(client:socket.socket):
    try:
        request = client.recv(1024)
        if not request:
            client.close()
            return
        
        host, port = getAddressInfo(request)
        if not host:
            client.close()
            return
        
        if host in BLOCKED:
            print(f"Blocked request to {host}")
            client.close()
            return
        
        if port == 443:
            handleHTTPS(client, host, port)
        else:
            handleHTTP(client, request, host, port)
        
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client.close()


def getAddressInfo(request):
    try:
        headers = request.decode(errors = "ignore")
        start = headers.find("Host: ")
        if start == -1:
            return None, None

        start += len("Host: ")
        end = headers.find("\r\n", start)
        if end == -1:
            return None, None

        host = headers[start:end].strip()
        if ":" in host:
            host, port = host.split(":")
            port = int(port)
        else:
            port = 80 # default HTTP port
        return host, port
    except Exception as e:
        print(f"Error parsing headers: {e}")
        return None, None

def handleHTTP(client:socket.socket, request, host, port):
    try:
        webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        webSocket.connect((host, port))
        webSocket.sendall(request)

        while True:
            response = webSocket.recv(1024)
            if not response:
                break
            client.sendall(response)
            #print(f"HTTP Host: {host}") # for testing purposes
    except Exception as e:
        print(f"Error forwarding HTTP request: {e}")
    finally:
        webSocket.close()

def handleHTTPS(client:socket.socket, host, port):
    try:
        client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as webSocket:
            webSocket.connect((host, port))

            client.setblocking(False)
            webSocket.setblocking(False)

            while True:
                try:
                    data = client.recv(1024)
                    if not data:
                        break
                    webSocket.sendall(data)
                    #print(f"1. HTTPS Host: {host}") # for testing purposes
                except BlockingIOError:
                    pass

                try:
                    data = webSocket.recv(1024)
                    if not data:
                        break
                    client.sendall(data)
                    #print(f"2. HTTPS Host: {host}") # for testing purposes
                except BlockingIOError:
                    pass
    except Exception as e:
        print(f"Error handling HTTPS: {e}")
        

def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', Port))
    s.listen(5)
    print(f"Server listening on port {Port}...")
    
    while True:
        client, addr = s.accept()
        print(f"Connection established with {addr}")
        thread = threading.Thread(target= handle, args=(client,))
        thread.start()

if __name__ == "__main__":
    start()

