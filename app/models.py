import socket
import random
import threading

connections = {}    # "ip": socket
DEFAULT_PORT = 1515


class Client:

    def __init__(self):
        self.ip = socket.gethostbyname(socket.getfqdn())


class Listener:

    # init runs until it receives a connection
    def __init__(self, port):
        # init socket and bind to port
        self.host = ''
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        # wait for someone to connect
        self.socket.listen()
        self.connection, self.addr = socket.accept()
        # add new connection to dict with ip as key
        connections[self.addr] = self.connection
        print('Connected by', self.addr)


def connect(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, DEFAULT_PORT))
    connections[ip] = s  # add socket connection to list
    s.send(b'hello there')


# open for requests and automatically redirect to open port
def listen():
    while True:  # don't close socket after client disconnected
        listener = Listener(DEFAULT_PORT)  # listener waits for connections and adds them to the list


def send(ip, text):
    if ip not in connections:
        print("connection failed :/")
        return
    else:
        connections[ip].send(text)

