
import socket
import os
import threading

HTML_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/html'
SERVER_HOST = '0.0.0.0' # Todas as interfaces de rede
SERVER_PORT = 6789
MAX_CONNECTIONS = 10
PAYLOAD_SIZE = 1024

class MultiThreadWebServer(object):
    def __init__(self, host, port):
        self.port = port
        # Cria socket
        self.server = socket.socket(
            socket.AF_INET, # IPV4
            socket.SOCK_STREAM, # TCP
        )
        self.server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR, # Liberar porta
            1,
        )
        self.server.bind((host, port))

    def get_file(filename):
        """Return the contents of a file as a string."""
        with open(filename, 'r') as f:
            return f.read()

    def listen(self):
        self.server.listen(MAX_CONNECTIONS)
        print('Listening on port %s ...' % self.port)
        while True:
            client, address = self.server.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient, args = (client,address)).start() # Abre thread

    def listenToClient(self, client, address):
        while True:
            try:
                request = client.recv(PAYLOAD_SIZE).decode()
                if request:
                    parts = request.split()
                    method = parts[0]
                    path = parts[1]

                    if(method != 'GET'):
                        response = 'HTTP/1.0 405 Method Not Allowed'
                        client.sendall(response.encode())
                        client.close()

                    if(path == '/'):
                        path = '/index.html'

                    filename = os.path.join(HTML_FOLDER, path.lstrip('/'))
                    if os.path.isfile(filename):
                        content = self.get_file(filename)
                        response = 'HTTP/1.0 200 OK\n\n' + content
                    else:
                        content = self.get_file(os.path.join(HTML_FOLDER, '404.html'))
                        response = 'HTTP/1.0 404 Not Found\n\n' + content

                    client.sendall(response.encode())
                    client.close()
                else:
                    raise 'Client disconnected'
            except:
                client.close()
                return False

if __name__ == '__main__':
    server = MultiThreadWebServer(SERVER_HOST, SERVER_PORT)
    server.listen()