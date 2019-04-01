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
        self.ip = self.core.profile.ip
        self.token = self.core.profile.token
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
        self.username = self.getUsername()
        self.token = self.getToken()
        self.ip = self.getIP()

    def getUsername(self,):
        if self.core.storage.data["profile"]["username"] == "":
            self.setUsername("Anonymous")
        return self.core.storage.data["profile"]["username"]

    def setUsername(self,name):
        self.core.storage.data["profile"]["username"] = name
        self.core.storage.save()

    def getIP(self):
        self.core.storage.data["profile"]["ip"] = socket.gethostbyname(socket.gethostname())
        self.core.storage.save()
        return self.core.storage.data["profile"]["ip"]

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
        self.nearby = []
        self.getContacts(self.core.storage.data["contacts"])

    def getContacts(self, data):
        for token, contactData in data.items():
            self.contacts.append(Contact(self.core, token, contactData))

    def addNearBy(self, profile):
        found = [c for c in self.nearby if c.token == profile["token"]]
        if len(found) > 0:
            return
        self.nearby.append(Contact(self,profile["token"],profile))
        self.core.view.switch.get("SearchView").sider.nearbyList.update()

    def addFromNearBy(self, token):
        found = [c for c in self.nearby if c.token == token][0]
        if not found:
            return False
        self.contacts.append(found)
        del found
        self.core.view.switch.get("MainView").sider.contactList.update()
        self.core.view.switch.get("SearchView").sider.nearbyList.update()

    def add(self, data):
        self.contacts.append(Contact(self.core, data["token"], data))
        self.core.view.switch.get("MainView").sider.contactList.update()
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
        allContacts = {} 
        for contact in self.contacts:
            allContacts[contact.token] = contact.toArray()
        return allContacts

    def receiveMessage(self,data):
        contact = self.get(data["profile"]["token"])
        if not contact:
            contact = self.add(data["profile"])
        return contact.receiveMessage(data)

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

    def update(self,profile):
        self.username = profile["username"]
        self.ip = profile["ip"] #RISKY

    def receiveMessage(self, data):
        msg = {"text": data["text"], "self": False, "utc": data["utc"]}
        self.messages.append(Message(self.core, msg))
        self.core.view.switch.get("MainView").content.chat.receiveMessage(self.token, self.messages[-1])
        self.core.contacts.save()
        return True

    def createMessage(self, text):
        data = {"text": text, "self": True, "utc": datetime.utcnow()}
        self.messages.append(Message(self.core, data))
        self.core.contacts.save()
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
            "utc": self.time,
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
        with open(DATA_URI, "rb") as f:
            self.data = json.loads(f.read().decode("UTF-8"))
            self.dataLoaded = True

    def writeData(self):
        with open(DATA_URI, "wb") as f:
            out = json.dumps(self.data, indent=4).encode("UTF-8")
            f.write(out)

    def createData(self):
        self.data = {"profile": {"username": "Nutzername", "token": ""}, "contacts": {}}
        self.writeData()

