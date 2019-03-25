import json
import os
import socket
import threading
from . import base

connections = {}  # "ip": socket
DEFAULT_PORT = 1516
DATA_URI = "app/data.json"


class Client:
    def __init__(self):

class BaseModel:

    def __init__(self,controller):
        self.controller = controller


class Client(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


class Storage(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataLoaded = False
        self.data = {}
        self.loadData()

    def save(self):
        self.writeData()

    def loadData(self):
        if not os.path.isfile(DATA_URI):
            self.createData()
        with open(DATA_URI, "r") as f:
            self.data = json.loads(f.read())
            self.dataLoaded = True

    def writeData(self):
        with open(DATA_URI, "w") as f:
            f.write(json.dumps(self.data))

    def createData(self):
        self.data = {"profile": {"username": "", "token": ""}, "contacts": {}}
        self.writeData()


def listen():
    host = ''
    port = DEFAULT_PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("Running at:", socket.gethostbyname(socket.gethostname()))

    while True:
        s.listen()
        conn, addr = s.accept()
        connections[addr] = conn
        print(connections)


def start_listening():
    threading.Thread(target=listen).start()


def connect(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, DEFAULT_PORT))
    connections[ip] = s  # add socket connection to list
    s.send(b'hello there')


def send(ip, text):
    if ip not in connections:
        print("connection failed :/")
        return
    else:
        connections[ip].send(text)

# testing
if __name__ == "__main__":

    start_listening()

    connect(input("ip: "))
    print(list(connections.keys()))
    # send("WHOAHSDIJDOADC")
