import socket

class Client:

    def __init__(self):
        self.ip = socket.gethostbyname(socket.getfqdn())
