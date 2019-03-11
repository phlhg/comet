import socket
import random
import threading

connections = {}

class Client:

    def __init__(self):
        self.ip = socket.gethostbyname(socket.getfqdn())


class Listener:

    def __init__(self):
        # init socket and bind to port
        self.host = ''
        self.port = random.randint(12345, 54321)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        # wait for someone to connect
        self.socket.listen()
        self.connection, self.addr = socket.accept()
        # add new connection to dict with ip as key
        connections[self.addr] = self.connection
        print('Connected by', self.addr)


def listen(self):
    l = Listener()
    l.connection.sendall()

while True:
    data = conn.recv(1024)
    print("data:", data)
    if not data:    # data == ''
        break
    conn.sendall(data)



