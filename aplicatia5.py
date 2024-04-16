import socket
import sys

hostname = sys.argv[1]
print(socket.gethostbyname(hostname))