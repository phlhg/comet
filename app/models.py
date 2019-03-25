import socket
import threading
from . import base

connections = {}  # "ip": socket
DEFAULT_PORT = 1516


class Client:
    def __init__(self):

        self.ip = socket.gethostbyname(socket.gethostname())
        threading.Thread(target=self.listen).start()

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, DEFAULT_PORT))
        print("Running at:", socket.gethostbyname(socket.gethostname()))
        while True:
            s.listen()
            conn, addr = s.accept()
            conn.send(bytes(base.storage.data["profile"]))
            connections[addr] = conn
            print(connections)

    def connect(self, ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, DEFAULT_PORT))
        connections[ip] = s  # add socket connection to list
        print("connected to", s)
        s.send(b'hello there')

    def connect_by_token(self, token):


    def send(self, token, text):
        if self.ip not in connections:
            print("connection doesn't exist :/")
            return
        else:
            connections[self.ip].send(text)

