import socket
DEFAULT_PORT = 1516
LOCAL = "172.16.0.192"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((LOCAL, DEFAULT_PORT))
print("[log: listening at]", LOCAL)

s.listen()
conn, addr = s.accept()
print("WOWOWOWO")
msg = str(conn.recv(), 'utf8')
