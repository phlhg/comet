import json
import os
import math
import socket
import threading
import random
import time
'''
sample message: "{"profile": {"token":"12345", "ip":"1.1.1.1", "username":"rueblibuur"}, "text": "hello there", "utc":0, "command":"searching/found/none"}
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
        self.profile = self.core.profile
        self.data = self.core.storage.data
        self.contacts = self.core.contacts
        
        #PH: Needed to change this in order to quit the thread.
        self.listeningThread = threading.Thread(target=self.listen)
        self.listeningThread.start()  # open for connection

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, DEFAULT_PORT))
        print("[log] listening at", self.ip, DEFAULT_PORT)

        s.listen()
        conn, addr = s.accept()
        print("[log] received connection")
        msg = str(conn.recv(4096), 'utf8')
        msg = msg.replace("'", '"')
        print("[log, msg in]", msg)  # debug log

        msg = json.loads(msg)
        command = msg['command']
        print("command:", command)
        profile = msg['profile']

        # command handling
        if command == "searching":
            self.send(profile['ip'], self.profile.toJSON(), command="found")    # send own profile with found cmd
        elif command == "found":
            self.contacts.addNearby(profile)
        elif command == "none":
            self.contacts.receiveMessage(msg)

        s.close()   # socket is closed on receiving end
        self.listen()   # listen for next msg

    def send(self, ip, text="", command="none"):
        print("[log] building connection to {} : {}...".format(ip, DEFAULT_PORT))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, DEFAULT_PORT))
        self.contacts.getByIP(ip).createMessage(text)   # store msg for local display
        msg = {"profile": self.profile.toJSON(), "text": text, "utc": round(time.time()), "command":command}
        s.sendall(bytes(str(msg), 'utf8'))
        print("[log] sent:", msg)

    def search(self):
        pass  # contactManager.addNearby(profile)


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
        self.username = name
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

    def toJSON(self):
        json = {"username": self.username, "token":self.token, "ip":self.ip}
        return json


class ContactManager:

    def __init__(self, core):
        self.core = core
        self.contacts = []
        self.nearby = []
        self.getContacts(self.core.storage.data["contacts"])
        self.sort()

    def getContacts(self, data):
        for token, contactData in data.items():
            self.contacts.append(Contact(self.core, token, contactData))

    def addNearby(self, profile):
        found = [c for c in self.nearby if c.token == profile["token"]]
        if len(found) > 0:
            return
        self.nearby.append(Contact(self,profile["token"],profile))
        self.core.view.update()

    def addFromNearby(self, token):
        found = [c for c in self.nearby if c.token == token][0]
        if not found:
            return False
        self.contacts.append(found)
        del found
        self.save()

    def add(self, data):
        c = {"username": data["username"], "ip": data["ip"], "messages": []}
        self.contacts.append(Contact(self.core, data["token"], c))
        self.save()
        return self.contacts[-1]

    def get(self, token):
        contact = [c for c in self.contacts if c.token == token]
        if len(contact) < 1:
            return False
        return contact[0]

    def getByIP(self, ip):
        contact = [c for c in self.contacts if c.ip == ip]
        if len(contact) < 1:
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

    def sort(self):
        self.contacts.sort(key=lambda c: c.key(), reverse=True)

    def save(self):
        self.sort()
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
        self.core.contacts.save()

    def receiveMessage(self, data):
        msg = {"text": data["text"], "self": False, "utc": data["utc"]}
        self.messages.append(Message(self.core, msg))
        self.update(data["profile"])
        self.core.contacts.save()
        return True

    def createMessage(self, text):
        data = {"text": text, "self": True, "utc": round(time.time())}
        self.messages.append(Message(self.core, data))
        self.core.contacts.save()
        return self.messages[-1]

    def sendMessage(self,text):
        self.core.client.send(self.ip, text)
        self.core.contacts.save()

    def key(self):
        if len(self.messages) < 1:
            return -1
        return self.messages[len(self.messages)-1].time

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
        self.raw = ""
        self.dataLoaded = False
        self.data = {}
        self.loadData()

    def save(self):
        self.writeData()
        self.core.view.update()

    def loadData(self):
        if not os.path.isfile(DATA_URI):
            self.createData()
        with open(DATA_URI, "rb") as f:
            self.raw = f.read().decode("UTF-8")
            self.data = json.loads(self.raw)
            self.dataLoaded = True

    def writeData(self):
        with open(DATA_URI, "wb") as f:
            self.raw = json.dumps(self.data, indent=4)
            f.write(self.raw.encode("UTF-8"))

    def createData(self):
        self.data = {"profile": {"username": "Nutzername", "token": ""}, "contacts": {}}
        self.writeData()

    def getSize(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk("."):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def getSizeReadable(self):
        units = ["Bytes","KB","MB","GB","TB"]
        countBytes = self.getSize()
        if countBytes == 0:
            return '0 Byte'
        i = int(math.floor(math.log(countBytes) / math.log(1024)))
        return str(round(countBytes / math.pow(1024, i), 0)) + ' ' + units[i]


