#!/usr/bin/python
# fisierul server.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
host = ''
port = 12345
s.bind((host, port))
suma = 0
s.listen(20)
while True:
    c, addr = s.accept()
    suma += int(c.recv(1024).decode())
    print('Suma curenta:', suma)
    c.close()
