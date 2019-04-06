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
    """Template for all Models
    
    Args:
        core (Controller): Controller responsible for the model

    Attributes:
        core (Controller): Controller to refer from the model.
    """

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
        self.listeningThread.setDaemon(True)
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
            self.send(profile['ip'], self.profile.toDict(), command="found")    # send own profile with found cmd
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
        msg = {"profile": self.profile.toDict(), "text": text, "utc": round(time.time()), "command":command}
        s.sendall(bytes(str(msg), 'utf8'))
        print("[log] sent:", msg)

    def search(self):
        pass  # contactManager.addNearby(profile)


class Profile(BaseModel):
    """Manages the profile of the user
    
    Attributes:
        username (str): The current name of the user.
        token (str): The token for identifictation of the user.
        ip (str): The current IP-Adress of the user.
    
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = self.getUsername()
        self.token = self.getToken()
        self.ip = self.getIP()

    def getUsername(self):
        """Returns the username
        
        Returns:
            str: The current username
        """
        if self.core.storage.data["profile"]["username"] == "":
            self.setUsername("Anonymous")
        return self.core.storage.data["profile"]["username"]

    def setUsername(self,name):
        """Sets the username

        Args:
            name (str): A new name for the user
        """
        self.username = name
        self.core.storage.data["profile"]["username"] = name
        self.core.storage.save()

    def getIP(self):
        """Returns the IP-Adress

        Returns:
            str: The current IP-Adress
        """
        self.core.storage.data["profile"]["ip"] = socket.gethostbyname(socket.gethostname())
        self.core.storage.save()
        return self.core.storage.data["profile"]["ip"]

    def getToken(self):
        """Returns the token. If none exists creates one.
        
        Returns:
            str: The current token.
        """
        if self.core.storage.data["profile"]["token"] == "":
            self.core.storage.data["profile"]["token"] = self.generateToken()
            self.core.storage.save()
        return self.core.storage.data["profile"]["token"]

    def generateToken(self,lenght=5):
        """Generates a random token

        Args:
            lenght (int): The lenght of the new token (default 5)
        Returns:
            str: A new random token.
        """
        chars = 'abcdefghijklmnopqrstuvwxyz'.upper()
        digits = '0123456789'
        all = chars+digits*3
        allLenght = len(all)
        token = ""
        for i in range(0, lenght):
            token += all[random.randint(0, allLenght-1)]
        return token

    def toDict(self):
        """Returns username, token and the ip of the user as a dictionary
        
        Returns:
            dict: Data of the profile {username, token, ip}
        """
        json = {"username": self.username, "token":self.token, "ip":self.ip}
        return json


class ContactManager:
    """Manages all contacts of the user

    Attributes:
        contacts ('list' of 'Contacts'): List of saved contacts
        nearby ('list' of 'Contacts'): List of nearby users (temporary contacts)
    """

    def __init__(self, core):
        self.core = core
        self.contacts = []
        self.nearby = []
        self.getContacts()

    def getContacts(self):
        """Loads all contacts from storage
        
        Returns:
            None
        """
        for token, contactData in self.core.storage.data["contacts"].items():
            self.contacts.append(Contact(self.core, token, contactData))
        self.sort()

    def addNearby(self, profile):
        """Adds a nearby user
        
        Args:
            profile (dict): Data of the profile ({username, token, ip})

        Returns:
            None
        """
        found = [c for c in self.nearby if c.token == profile["token"]]
        if len(found) > 0:
            return
        self.nearby.append(Contact(self,profile["token"],profile))
        self.core.view.update()

    def addFromNearby(self, token):
        """Moves a nearby user into the permanent contacts
        
        Args:
            token (str): Token of the user to move into contacts.
        Returns:
            Bool: True if successful, False otherwise.
        """
        found = [c for c in self.nearby if c.token == token][0]
        if not found:
            return False
        self.contacts.append(found)
        del found
        self.save()
        return True

    def add(self, data):
        """Add a user to the permanent contacts
        
        Args: 
            data (dict): Data of the user to add.
        Returns:
            Contact: Instance of the added user.
        """
        c = {"username": data["username"], "ip": data["ip"], "messages": []}
        self.contacts.append(Contact(self.core, data["token"], c))
        self.save()
        return self.contacts[-1]

    def get(self, token):
        """Returns a contact by token
        
        Args:
            token (str): Token of the desired user.
        Returns:
            Contact/Bool: Returns the Contact if successful, otherwise False.
        """
        contact = [c for c in self.contacts if c.token == token]
        if len(contact) < 1:
            return False
        return contact[0]

    def getByIP(self, ip):
        """Returns a contact by IP-adress
        
        Args:
            ip (str): IP_adress of the desired user.
        Returns:
            Contact/Bool: Returns the Contact if successful, otherwise False.
        """
        contact = [c for c in self.contacts if c.ip == ip]
        if len(contact) < 1:
            return False
        return contact[0]

    def toDict(self):
        """Returns a dictionary with all contacts formated like:
        
        {"[token]": {[contactData]}...}
            
        Returns:
            dict: All permanent contacts
        """
        allContacts = {} 
        for contact in self.contacts:
            allContacts[contact.token] = contact.toArray()
        return allContacts

    def receiveMessage(self,data):
        """Handles the entry of a message for all contacts an creates a contact if the contact is missing.
        
        Args:
            data (dict): Received data - {profile: {username, token, ip}, text, utc}
        Returns:
            Message: Instance of the received message
        """
        contact = self.get(data["profile"]["token"])
        if not contact:
            contact = self.add(data["profile"])
        return contact.receiveMessage(data)

    def sort(self):
        """Sorts contacts by latest messages"""
        self.contacts.sort(key=lambda c: c.key(), reverse=True)

    def save(self):
        """Saves all contacts"""
        self.sort()
        self.core.storage.data["contacts"] = self.toDict()
        self.core.storage.save()


class Contact:
    """Manages a contact.
    
    Args:
        core (controller): The controller responsible for the model.
        token (str): Token to identify the contact.
        data (dict): Data about the contact {username, ip, messages}

    Attributes:
        core (Controller): The controller responsible for the model.
        token (str): Token to identify the contact.
        ip (str): IP-adress of the contact.
        username (str): Username of the contact.
        messages (list): List of all Messages of the contact.
    """

    def __init__(self, core, token, data):
        self.core = core
        self.token = token
        self.ip = data["ip"]
        self.username = data["username"]
        self.messages = []
        self.getMessages(data["messages"])

    def getMessages(self, data):
        """Load all messages from a list

        Args:
            data (list): List of dicts with data about each messages [{text,self,utc}...]
        Returns:
            None
        """
        for message in data:
            self.messages.append(Message(self.core, message))

    def update(self,profile):
        """Updates username and ip of the contact
        
        Args:
            profile (dict): Data about the contact {username, ip}
        Returns:
            None
        """
        self.username = profile["username"]
        self.ip = profile["ip"] #RISKY
        self.core.contacts.save()

    def receiveMessage(self, data):
        """Handles the entry of a message for the managed contact
        
        Args:
            data (dict): Received data - {profile: {username, token, ip}, text, utc}
        Returns:
            Message: Instance of the received message
        """
        msg = {"text": data["text"], "self": False, "utc": data["utc"]}
        self.messages.append(Message(self.core, msg))
        self.update(data["profile"])
        self.core.contacts.save()
        return self.messages[-1]

    def createMessage(self, text):
        """Creats message sent by the client to this user
        
        Args:
            text (str): Text of the message
        Returns:
            Message: Instance of the message.
        """
        data = {"text": text, "self": True, "utc": round(time.time())}
        self.messages.append(Message(self.core, data))
        self.core.contacts.save()
        return self.messages[-1]

    def sendMessage(self,text):
        """Sends a message to this contact
        
        Args:
            text (str): Text of the message.
        Returns:
            None
        """
        self.core.client.send(self.ip, text)
        self.core.contacts.save()

    def key(self):
        """Returns key for the sorting of contacts
        
        Returns:
            Int: key to sort by
        """
        if len(self.messages) < 1:
            return -1
        return self.messages[len(self.messages)-1].time

    def toArray(self):
        """Returns the contact as an dict

        Returns:
            dict: Data of the profile {ip, username, messages}
        """
        return {
            "ip": self.ip,
            "username": self.username,
            "messages": [m.toArray() for m in self.messages]
        }


class Message:
    """Holds and manages a message
    
    Args:
        core (Controller): Controller responible for the model.
        data (dict): Data of the message - {text (str), self (bool), utc (int)}

    Arguments:
        core (Controller): Controller responible for the model.
        text (str): Text of the message
        self (bool): Indicates if the message is sent by the user himself
        time (int): UTC-Timestamp, which indicates the time of sending
    """

    def __init__(self, core, data):
        self.core = core
        self.text = data["text"]
        self.self = data["self"]
        self.time = data["utc"]

    def toArray(self):
        """Returns the message as a dict
        
        Returns:
            dict: Data of the message - {text (str), self (bool), utc (int)}
        """
        return {
            "text": self.text,
            "self": self.self,
            "utc": self.time,
        }

class Storage(BaseModel):
    """Manages the storage of the application

    Note:
        !! The storage doesn't provide support for UTF-16-chars such as EMOJIS

    Arguments:
        raw (str): Raw data of the JSON-file
        data (dict): Data as a dict generated from the JSON-file
        dataLoaded (bool): Indicates if the data was loaded yet.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw = ""
        self.dataLoaded = False
        self.data = {}
        self.loadData()

    def save(self):
        """Saves the data and tells the view to update"""
        self.writeData()
        self.core.view.update()

    def loadData(self):
        """Loads the data from the JSON-file and if none exists creates one"""
        if not os.path.isfile(DATA_URI):
            self.createData()
        with open(DATA_URI, "rb") as f:
            self.raw = f.read().decode("UTF-8")
            self.data = json.loads(self.raw)
            self.dataLoaded = True

    def writeData(self):
        """Writes the data to the JSON-file"""
        with open(DATA_URI, "wb") as f:
            self.raw = json.dumps(self.data, indent=4)
            f.write(self.raw.encode("UTF-8"))

    def createData(self):
        """Creates a template to initialize the JSON-file"""
        self.data = {"profile": {"username": "Nutzername", "token": "", "ip": ""}, "contacts": {}, "settings": {}}
        self.writeData()

    def getSize(self):
        """Returns the total size of the application.
        
        Returns: 
            Int: Size of the application in bytes.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk("."):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def getSizeReadable(self):
        """Returns a reabale size of the application.
        
        Available Units: Bytes, KB, MB, GB, TB

        Returns:
            Str: Size of the application - for example: "12 MB"
        """
        units = ["Bytes","KB","MB","GB","TB"]
        countBytes = self.getSize()
        if countBytes == 0:
            return '0 Byte'
        i = int(math.floor(math.log(countBytes) / math.log(1024)))
        return str(round(countBytes / math.pow(1024, i), 0)) + ' ' + units[i]


