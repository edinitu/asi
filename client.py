#!/usr/bin/python
# fisierul client.py
import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
host = socket.gethostname()
port = 12345
s.connect((host, port))
s.send(sys.argv[1].encode())
s.close
