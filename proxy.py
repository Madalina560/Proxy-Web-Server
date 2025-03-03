import socket
import threading

# followed the tutorial at: https://brightdata.com/blog/proxy-101/python-proxy-server

def start():
    port = 8080
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', port))
    s.listen(5)
    print(f"Server listening on port {port}...")
    
    while True:
        client, addr = s.accept()
        print(f"Connection established with {addr}")

        comms(client)


def getAddressInfo(fullInfo:bytes) -> tuple[str,int]:
    startOfIndex = fullInfo.find(b'Host: ')

    if startOfIndex == -1:
        print("Error: 'Host' header not found")
        return "", 0
    
    startOfIndex += len(b'Host: ')
    endOfIndex = fullInfo.find(b"\r\n", startOfIndex)

    if endOfIndex == -1:
        print("Error: Host line not properly formatted")
        return "", 0
    
    mainInfo = fullInfo[startOfIndex:endOfIndex].decode().strip()

    if ":" in mainInfo:
        host, port = mainInfo.split(":")
        port = int(port)
    else:
        host = mainInfo
        port = 80 # default HTTP port
    
    return host, port

def comms(client:socket.socket):
    client.settimeout(50)

    info = b""

    try:
        while True:
            data = client.recv(1024)
            if not data:
                break
            info += data
    except socket.timeout:
        print("Timeout while reading request")
        client.close()
        return

    host, port = getAddressInfo(info)

    if not host:
        print("Error: Invalid host, closing connection.")
        client.close()
        return
    
    # Block HTTPS for testing HTTP
    if port == 443:
        print(f"Blocked HTTPS request to {host}")
        client.close()
        return

    print(f"Host: {host}, port: {port}")

    try:
        webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        webSocket.connect((host, port))
        webSocket.sendall(info)

        print(("Recieved response:\n"))

        while True:
            response = webSocket.recv(1024)
            if not response:
                break
            client.sendall(response)
    
    except Exception as e:
        print(f"Error forwarding request: {e}")
    
    finally:
        webSocket.close()
        client.close()

if __name__ == "__main__":
    start()

