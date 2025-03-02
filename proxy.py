import socket
import threading

# followed the tutorial at: https://brightdata.com/blog/proxy-101/python-proxy-server

def handle(client):
    request = b''

    while True:
        try:
            data = client.recv(1024)
            request = request + data
            print(f"{data.decode('utf-8')}")
        
        except:
            break

        host, port = getHostPortRequest(request)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall(request)

        print("Recieved response:\n")
        while True:
            data = s.recv(1024)
            print(f"{data.decode('utf-8')}")

            if len(data) > 0:
                client.sendall(data)
            else:
                break
        
        s.close()
        client.close()

def getHostPortRequest(request):
    hostStart = request.find(b'Host: ') + len(b'Host: ')
    hostEnd = request.find(b'\r\n', hostStart)
    hostStr = request[hostStart:hostEnd].decode('utf-8')

    webServer = hostStr.find("/")
    if webServer == -1:
        webServer = len(hostStr)
    
    findPort = hostStr.find(":")
    if findPort == -1 or webServer < findPort:
        #default port
        port = 80
        host = hostStr[:webServer]
    else:
        port = int((hostStr[(findPort + 1):]) [:webServer - findPort - 1])
        host = hostStr[:findPort]
    
    return host, port


def start_server():
    port = 6040
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen(5)
    print(f"Server listening on port {port}...")

    while True:
        client, addr = s.accept()
        print(f"Connection established with {addr}")
        
        handler = threading.Thread(target = handle, args = (client,))
        handler.start()

if __name__ == "__main__":
    start_server()