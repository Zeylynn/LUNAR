import socket
import time
import os

HOST = "127.0.0.1"
PORT = 9001

for i in range(1000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send(b'{"cmd":"config", "data": null}\n')  # optional, kann auch leer sein
    os._exit(1)  # brutaler Prozesskill
    # s.close()  # NICHT benutzen, wir wollen abrupt