import socket
import threading


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

    def connect(ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, DEFAULT_PORT))
        connections[ip] = s  # add socket connection to list
        s.send(b'hello there')


    def send(token, text):
        if ip not in connections:
            print("connection failed :/")
            return
        else:
            connections[ip].send(text)

