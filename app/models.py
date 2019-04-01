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

    def __init__(self, controller):
        self.controller = controller


class Client(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.token = self.controller.Profile.getToken()
        self.data = self.controller.storage.data
        self.contacts = self.controller.contacts
        threading.Thread(target=self.listen).start()

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, DEFAULT_PORT))
        print("[log: listening at]", self.ip)

        s.listen()
        conn, addr = s.accept()
        msg = dict(str(conn.recv()))

        token = msg['profile']['token']
        ip = msg['profile']['ip']
        username = msg['profile']['username']

        contact = self.contacts.get(token)  # get contact or add new if not existent
        if not contact:
            contact = self.contacts.add(token, ip, username)

        contact.receiveMessage(msg['text'], msg['utc'])  # store msg in ContactManager

        print("[log: received]", msg)  # tmp testing
        s.close()   # socket is closed on receiving end
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

