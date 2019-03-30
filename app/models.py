import json
import os
import socket
import threading
import random
from datetime import datetime

'''
sample message: "{"profile": {"token":"12345", "ip":"1.1.1.1", "username":"rueblibuur"}, "text": "hello there", "utc":0}
'''

DEFAULT_PORT = 1516
DATA_URI = "app/data.json"

class BaseModel:

    def __init__(self, core):
        self.core = core


class Client(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.token = self.core.profile.getToken()
        self.data = self.core.storage.data
        self.contacts = self.core.contacts
        
        threading.Thread(target=self.listen).start()

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, DEFAULT_PORT))
        print("listening at", self.ip)

        s.listen()
        conn, addr = s.accept()
        msg = dict(conn.recv())

        token = msg['profile']['token']
        ip = msg['profile']['ip']
        username = msg['profile']['username']

        contact = self.contacts.get(token)
        if not contact:
            contact = self.contacts.add(token, ip, username)

        contact.receiveMessage(msg['text'], msg['utc'])

        print("[log: received]", msg)  # tmp testing
        s.close()
        self.listen()   # listen for next msg

    def send(self, ip, text):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, DEFAULT_PORT))
        self.contacts.getByIP(ip).createMessage(text)   # store msg for local display
        msg = {'profile': self.data['profile'], 'text': text, 'utc': datetime.utcnow()}
        s.sendall(bytes(str(msg)))
        print("[log: sent]", msg)


class Profile(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = self.core.storage.data["profile"]["username"]
        self.token = self.getToken()


    def getToken(self):
        if self.core.storage.data["profile"]["token"] == "":
            self.core.storage.data["profile"]["token"] = self.generateToken()
            self.core.storage.save()
        return self.core.storage.data["profile"]["token"]


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

    def __init__(self, core):
        self.core = core
        self.contacts = []
        self.getContacts(self.core.storage.data["contacts"])

    def getContacts(self, data):
        for token, contactData in data.items():
            self.contacts.append(Contact(self.core, token, contactData))

    def add(self, token, ip, username):
        data = {"ip": ip, "username": username, "messages": []}
        self.contacts.append(Contact(token, data))
        return self.contacts[-1]

    def get(self, token):
        contact = [c for c in self.contacts if c.token == token]
        if not contact[0]:
            return False
        return contact[0]

    def getByIP(self, ip):
        contact = [c for c in self.contacts if c.ip == ip]
        if not contact[0]:
            return False
        return contact[0]

    def toArray(self):
        return [c.toArray() for c in self.contacts]

    def save(self):
        self.core.storage.data["contacts"] = self.toArray()
        self.core.storage.save()


class Contact:

    def __init__(self, core, token, data):
        self.core = core
        self.token = token
        self.ip = data["ip"]
        self.username = data["username"]
        self.messages = []
        self.getMessages(data["messages"])

    def getMessages(self, data):
        for message in data:
            self.messages.append(Message(self.core, message))

    def receiveMessage(self, text, time):
        data = {"text": text, "self": False, "utc": time}
        self.messages.append(Message(data))

    def createMessage(self, text):
        data = {"text": text, "self": True, "utc": datetime.utcnow()}
        self.messages.append(Message(data))
        return self.messages[-1]

    def toArray(self):
        return {
            "ip": self.ip,
            "username": self.username,
            "messages": [m.toArray() for m in self.messages]
        }


class Message:

    def __init__(self, core, data):
        self.core = core
        self.text = data["text"]
        self.self = data["self"]
        self.time = data["utc"]

    def toArray(self):
        return {
            "text": self.text,
            "self": self.self,
            "time": self.time,
        }

    def toJSON(self):
        return {
            "profile": self.profile.t
        }


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
            f.write(json.dumps(self.data, indent=4))

    def createData(self):
        self.data = {"profile": {"username": "Nutzername", "token": ""}, "contacts": {}}
        self.writeData()

