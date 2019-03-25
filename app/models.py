import json
import os
import socket
import threading
import random


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
            conn.send(bytes(self.controller.storage.data["profile"]))
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


class Profile(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = self.controller.storage.data["profile"]["username"]
        self.token = self.getToken()


    def getToken(self):
        if self.controller.storage.data["profile"]["token"] == 0:
            self.controller.storage.data["profile"]["token"] = self.generateToken()
            self.controller.storage.save()
        return self.controller.storage.data["profile"]["token"]


    def generateToken(lenght=5):
        chars = 'abcdefghijklmnopqrstuvwxyz'.upper()
        digits = '0123456789'
        all = chars+digits*3
        allLenght = len(all)
        token = ""
        for i in range(lenght):
            token += all[random.randint(0, allLenght-1)]
        return token


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




