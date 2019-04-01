import socket
import time
DEFAULT_PORT = 1516
LOCAL = "172.16.0.192"
mask = "172.16.0."

for i in range(255):
    ip = mask + str(i)
    if ip != LOCAL:
        print("searching for", ip)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setblocking(False)
            s.connect((ip, DEFAULT_PORT))
            time.sleep(1000)
            s.send(b"hello")
            print("connected?")
        except Exception as e:
            pass
