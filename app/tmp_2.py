import socket
import time
import os

DEFAULT_PORT = 1516
LOCAL = socket.gethostbyname(socket.gethostname())

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
socket.setdefaulttimeout(0.01)

parts = LOCAL.split(".")
pre = parts[0]+"."+parts[1]+"."

found = []

for i in range(0,1):
        for j in range(0,256):
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                ip = pre + str(i) + "." + str(j)
                ex = s.connect_ex((ip,80))
                print(ip+" \t\t --> "+str(ex))
                if ex == 0:
                        found.append(ip)
                s.close()

for ip in found:
        print(" > "+ip)
