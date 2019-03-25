import json
import os
import socket
import threading
import random
from datetime import datetime


DEFAULT_PORT = 1516
DATA_URI = "app/data.json"


class BaseModel:

    def __init__(self,controller):
        self.controller = controller


class Client(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connections = {}  # "ip": socket
        self.ip = socket.gethostbyname(socket.gethostname())
        self.token = self.controller.profile.getToken()
        self.data = self.controller.storage.data
        threading.Thread(target=self.listen).start()

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, DEFAULT_PORT))
        print("Running at:", socket.gethostbyname(socket.gethostname()))
        while True:
            s.listen()
            conn, addr = s.accept()
            s.setblocking(False)
            conn.send(bytes(self.data['profile']))
            self.connections[addr] = conn
            print(self.connections)


    def connect_by_ip(self, ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, DEFAULT_PORT))
        self.connections[ip] = s  # add socket connection to list
        print("connected to", s)
        s.send(self.data['profile'])

    def connect_by_token(self, token):
        self.connect_by_ip(self.connections[self.data['contacts'][token]['ip']])

    def send(self, ip, text):
        if ip not in self.connections:
            print("connection doesn't exist :/")
            return
        else:
            self.connections[ip].sendall(text)

    def update(self):
        for s in self.connections.values():
            s.recv()


class Profile(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = self.controller.storage.data["profile"]["username"]
        self.token = self.getToken()


    def getToken(self):
        if self.controller.storage.data["profile"]["token"] == "":
            self.controller.storage.data["profile"]["token"] = self.generateToken()
            self.controller.storage.save()
        return self.controller.storage.data["profile"]["token"]


    def generateToken(self,l=5):
        chars = 'abcdefghijklmnopqrstuvwxyz'.upper()
        digits = '0123456789'
        all = chars+digits*3
        allLenght = len(all)
        token = ""
        for i in range(0, l):
            token += all[random.randint(0, allLenght-1)]
        return token


class ContactManager:

    def __init__(self, data):
        self.contacts = []
        self.getContacts(data)

    def getContacts(self, data):
        for token, contactData in data.items():
            self.contacts.append(Contact(token, contactData))

    def addContact(self,token, ip, username):
        data = {"token": token, "ip": ip, "username": username, "messages": []}
        self.contacts.append(Contact(data))

    def get(self, token):
        contact = [c for c in self.contacts if c.token == token] #filter(lambda c: c.token == token, self.contacts)
        if not contact[0]:
            return False
        return contact[0]

class Contact:

    def __init__(self, token, data):
        self.token = token
        self.ip = data["ip"]
        self.username = data["username"]
        self.messages = []
        self.getMessages(data["messages"])

    def getMessages(self, data):
        for message in data:
            self.messages.append(Message(message))

    def receiveMessage(self, text, time):
        data = {"text": text, "self": False, "utc": time}
        self.messages.append(Message(data))

    def sendMessage(self, text):
        data = {"text": text, "self": True, "utc": datetime.utcnow()}
        self.messages.append(Message(data))


class Message:

    def __init__(self, data):
        self.text = data["text"]
        self.self = data["self"]
        self.time = data["utc"]


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

