#!/usr/bin/python

import os
import socket, pickle
import pickle
import select
import Queue
import struct

table = [['*' for x in range(4)] for y in range(4)]
x_moves = []
y_moves = []
win = False
draw = False
players = {"X": "", "0": ""}


def serializer(table, x_moves, y_moves, state, role):
    data = {}
    data['table'] = table
    data['x_moves'] = x_moves
    data['y_moves'] = y_moves
    data['state'] = state
    data['role'] = role
    return pickle.dumps(data)


def deserializer(data):
    return pickle.loads(data)


def send_data(s, data):
    length = struct.pack('!I', len(data))  # Number of bytes sended in the payload (for packet delimitation)
    data = length + data
    s.send(data)


def recv_data(s):
    buf = b''
    while len(buf) < 4:  # Get the length of the payload (fixed size)
        buf += s.recv(4 - len(buf))
    length = struct.unpack('!I', buf)[0]
    data = b''
    while len(data) < length:  # Get the payload
        data += s.recv(length - len(data))
    return deserializer(data)


def open_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)  # ipv4 + TCP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(0)
    host = ''
    port = 1600
    server.bind((host, port))
    server.listen(2)
    print("Server listening on port %s. Waiting for clients...\n" % port)
    return server


def monitor_sockets(server):
    try:
        inputs = [server, ]
        outputs = []
        message_queues = {}
        i = 0
        turn = ['X', '0']
        jackpot = ''
        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            if server in readable:
                if len(inputs) < 3:  # not enough players to start the game
                    c, addr = server.accept()
                    print("New connection: ", addr)
                    c.setblocking(0)
                    inputs.append(c)
                    if players['X'] == '':
                        players['X'] = c
                    if players['0'] == '':
                        players['0'] = c
                    outputs.append(c)
                    message_queues[c] = Queue.Queue()
                else:  # rest of the clients will be rejected
                    c, addr = server.accept()
                    c.close()
            if len(inputs) == 3:  # server + 2 x client | The game can start
                for s in readable:
                    if s is not server:
                        data = recv_data(s)
                        if data:
                            # A readable client socket has data
                            print("Received '%s' from " % data, s.getpeername())
                            state = play(table, turn[i], data['x'], data['y'], data['quit'])
                            if "valid" in state.keys():  # if the move is valid => other player turn
                                if state['valid'] == 0:
                                    i = (i + 1) % 2  # index in turn ['X','0']
                            state['turn'] = turn[i]
                            role = ''
                            if players['X'] == s:
                                role = 'X'
                            else:
                                role = '0'
                            if state['win'] == 'X' or state['win'] == '0':
                                jackpot = state['win']  # holder for the winner
                            state['win'] = jackpot
                            client_payload = serializer(table, x_moves, y_moves, state,
                                                        role)  # server response in binary
                            message_queues[s].put(client_payload)  # put server response in client queue
                            # Add output channel for response
                            if s not in outputs:
                                outputs.append(s)
                for s in writable:
                    try:
                        data = message_queues[s].get_nowait()  # fetch data from client queues (server responses)
                        print("Getting data from queue..")
                    except Queue.Empty:
                        # No messages waiting so stop checking for writability.
                        print("Output queue for ", s.getpeername(), " is empty")
                        outputs.remove(s)
                    else:
                        print("Sending data to ", s.getpeername())
                        send_data(s, data)  # send server response to clients
                for s in exceptional:
                    print("Handling exceptional condition for", s.getpeername())
                    # Stop listening for input on the connection
                    inputs.remove(s)
                    if s in outputs:
                        outputs.remove(s)
                    s.close()
                    del message_queues[s]
    except KeyboardInterrupt:
        server.close()
        print("Server closed \n")


def print_table(table):
    print("\n>>>>> XO GAME <<<<<\n")
    print("\n".join([''.join(['{:4}'.format(item) for item in row]) for row in table]))
    print("\n")


def column(matrix, i):
    return [row[i] for row in matrix]


def diag1(matrix):
    return [matrix[i][i] for i in range(4)]


def diag2(matrix):
    return [matrix[3 - i][i] for i in range(4)]


def check_winner(table, turn):  # returns the name of the winner ('X','0') or an empty string if no winner
    for row in table:
        if row == [turn] * 4:
            return turn
    for i in range(4):
        if column(table, i) == [turn] * 4:
            return turn
    if diag1(table) == [turn] * 4:
        return turn
    if diag2(table) == [turn] * 4:
        return turn
    return ''


def check_draw(table, turn):  # Returns True if no available moves. Else it returns False
    draw = True
    if turn == 'X':
        for row in table:
            if '0' not in row:
                draw = False
                return draw
        for i in range(4):
            if '0' not in column(table, i):
                draw = False
                return draw
        if ('0' not in diag1(table)) or ('0' not in diag2(table)):
            draw = False
            return draw
    if turn == '0':
        for row in table:
            if 'X' not in row:
                draw = False
                return draw
        for i in range(4):
            if 'X' not in column(table, i):
                draw = False
                return draw
        if ('X' not in diag1(table)) or ('X' not in diag2(table)):
            draw = False
            return draw
    return draw


def new_move(table, turn, line, col):
    valid = 0  # 0 - Valid move | 1 - Field in use | 2 - Invalid option
    try:
        x = int(line)
        y = int(col)
        if table[x - 1][y - 1] == '*':
            table[x - 1][y - 1] = turn
            print_table(table)
            if turn == 'X':
                x_moves.append((x, y))
            else:
                y_moves.append((x, y))
        else:
            valid = 1
            return valid
        return valid
    except (ValueError, IndexError, UnboundLocalError):
        valid = 2
        return valid


def play(table, turn, x, y, quit):
    state = {}
    try:
        state['turn'] = turn
        print_table(table)
        print("X moves : %s\n" % x_moves)
        print("0 moves : %s\n" % y_moves)
        print("\n => %s turn" % turn)
        valid = new_move(table, turn, x, y)
        state['valid'] = valid
        state['win'] = check_winner(table, turn)
        if state['win'] == 'X' or state['win'] == '0':
            print("%s is the winner !\n" % turn)
            raise KeyboardInterrupt
        state['draw'] = check_draw(table, turn)
        if draw:
            print("It is a draw !\n")
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("\nGame over ! Thanks for playing \n")
        return state
    return state


def main():
    os.system("clear")
    server = open_server()
    monitor_sockets(server)


main()

