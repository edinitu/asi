#!/usr/bin/python

import socket, pickle
import os
import struct
import time
import sys

quit = False


def print_table(table):
    print("\n>>>>> XO GAME <<<<<\n")
    print("\n".join([''.join(['{:4}'.format(item) for item in row]) for row in table]))
    print("\n")


def serializer(xo, x, y, quit):
    data = {}
    data['xo'] = xo
    data['x'] = x
    data['y'] = y
    data['quit'] = quit
    return pickle.dumps(data)  # pickle.dumps(data)


def deserializer(data):
    return pickle.loads(data)


def send_data(s, data):
    length = struct.pack('!I', len(data))
    data = length + data
    s.send(data)


def recv_data(s):
    buf = b''
    while len(buf) < 4:
        buf += s.recv(4 - len(buf))
    length = struct.unpack('!I', buf)[0]
    data = b''
    while len(data) < length:
        data += s.recv(length - len(data))
    return deserializer(data)


def connect(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = addr
    port = 1600
    print("Connecting to %s:%s...\n" % (host, port))
    sock.connect((host, port))
    return sock


os.system("clear")
valid_ip = True
try:
    addr = sys.argv[1]
    socket.inet_aton(addr)
except (socket.error, IndexError):
    print("usage: ./client.py '<server-ip>'\n")
    valid_ip = False

if valid_ip:
    try:
        server = connect(addr)
    except socket.error:
        print("Unable to reach the server. Try again later \n")
        valid_ip = False
if valid_ip:
    send_data(server, serializer('X', 5, 5, quit))
    rec_data = recv_data(server)
    print("Welcome to my X0 game ! You will play with '%s'\n" % rec_data['role'])
    print("You can press 'CTRL+C' at any moment if you want to close the game\n")
    my_role = rec_data['role']
    print_table(rec_data['table'])
    print("'X' moves : %s\n" % rec_data['x_moves'])
    print("'0' moves : %s\n" % rec_data['y_moves'])

    playing = True
    while playing:
        try:
            if (rec_data['state']['turn'] == my_role) and (rec_data['state']['win'] == ''):
                print("=> Your turn [%s]\n" % my_role)
                x = raw_input('Line[1-4]: ')
                y = raw_input('Column[1-4]: ')
                os.system("clear")
                send_data(server, serializer(my_role, x, y, quit))
                rec_data = recv_data(server)
                print_table(rec_data['table'])
                print("'X' moves : %s\n" % rec_data['x_moves'])
                print("'0' moves : %s\n" % rec_data['y_moves'])
                if rec_data['state']['valid'] == 1:
                    raise ValueError
                if rec_data['state']['valid'] == 2:
                    raise IndexError
                if rec_data['state']['win'] == my_role:
                    print("You won !\n")
                    raise KeyboardInterrupt
                if (rec_data['state']['win'] != my_role) and (rec_data['state']['win'] != ''):
                    print("You lost !\n")
                    raise KeyboardInterrupt
                if rec_data['state']['draw']:
                    print("It's a draw \n")
                    raise KeyboardInterrupt
            elif rec_data['state']['win'] == '':
                print("=> Your opponents turn ...\n")
                while rec_data['state']['turn'] != my_role:
                    time.sleep(2)
                    send_data(server, serializer('X', 5, 5, quit))
                    rec_data = recv_data(server)
                    if (rec_data['state']['win'] != my_role) and (rec_data['state']['win'] != ''):
                        print("You lost !\n")
                        raise KeyboardInterrupt
                    if rec_data['state']['draw']:
                        print("It's a draw \n")
                        raise KeyboardInterrupt
                os.system("clear")
                print_table(rec_data['table'])
                print("'X' moves : %s\n" % rec_data['x_moves'])
                print("'0' moves : %s\n" % rec_data['y_moves'])
        except KeyboardInterrupt:
            quit = True
            send_data(server, serializer('X', 5, 5, quit))
            server.close()
            playing = False
            print("Game closed\n")
        except socket.error:
            print("Game closed by server\n")
        except ValueError:
            print("\nYou selected ('%s','%s'). That field is already in use. Try again \n" % (x, y))
        except IndexError:
            print(
                "\nYou selected ('%s','%s'). Please choose numbers between 1 and 4, or press 'CTRL+C' for quiting\n" % (
                x, y))

