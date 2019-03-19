import socket
import threading

connections = {}  # "ip": socket
DEFAULT_PORT = 1516

class Client:
  def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())

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


if __name__ == "__main__":

    start_listening()

    connect(input("ip: "))
    print(list(connections.keys()))
    # send("WHOAHSDIJDOADC")
