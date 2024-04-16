#!/usr/bin/env python

import socket
import json
import random

# import keyboard


# def on_key_event(e):
#     if e.name == "q":
#         print("\nExiting...")
#         sys.exit()


def serialize_data(data):
    return json.dumps(data)


# Function to place a battleship
def place_battleship(grid, size):
    while True:
        # Randomly choose starting position
        start_row = random.randint(0, len(grid) - 1)
        start_col = random.randint(0, len(grid[0]) - 1)

        # Randomly choose direction (0 for horizontal, 1 for vertical)
        direction = random.randint(0, 1)

        # Check if battleship fits in chosen direction
        if direction == 0 and start_col + size <= len(grid[0]):
            end_row = start_row
            end_col = start_col + size - 1
        elif direction == 1 and start_row + size <= len(grid):
            end_row = start_row + size - 1
            end_col = start_col
        else:
            continue  # Battleship does not fit, try again

        # Check if battleship overlaps with existing ships
        overlaps = False
        for r in range(start_row, end_row + 1):
            for c in range(start_col, end_col + 1):
                if grid[r][c] != "O":
                    overlaps = True
                    break
            if overlaps:
                break

        if not overlaps:
            # Place the battleship
            for r in range(start_row, end_row + 1):
                for c in range(start_col, end_col + 1):
                    grid[r][c] = "X"
            break


# Function to check if a fire hits a battleship
def fire(grid, row, col):
    if grid[row][col] == "X":
        grid[row][col] = "H"  # Hit
        return True
    elif grid[row][col] == "M":
        return False
    else:
        grid[row][col] = "M"  # Miss
        return True


def send_table(client, table):
    client.send(serialize_data(table).encode())


def print_table(grid):
    # Print header with column numbers
    header = "   " + " ".join(str(i) for i in range(1, len(grid[0]) + 1))
    print(header.rstrip())  # Remove trailing space
    print("-" * (len(header) + 1))  # Header separator

    # Print rows with row numbers and contents
    for row_num, row in enumerate(grid, start=1):
        row_display = [str(cell) for cell in row]  # Convert each cell to string
        print(f"{row_num} | {' '.join(row_display)}")


def check_win(table):
    ok = 0
    for row in table:
        for cell in row:
            if cell == 'X':
                ok += 1
                return False
    if ok == 0:
        return True


# Start listening for key events
# keyboard.on_press(on_key_event)

# Create an empty 8x8 table
table1 = [["O" for _ in range(8)] for _ in range(8)]
table2 = [["O" for _ in range(8)] for _ in range(8)]

# Place battleships for client 1
place_battleship(table1, 2)  # Battleship 1 (2 cells)
place_battleship(table1, 3)  # Battleship 2 (3 cells)
place_battleship(table1, 4)  # Battleship 3 (4 cells)

# Place battleships for client 2
place_battleship(table2, 2)  # Battleship 1 (2 cells)
place_battleship(table2, 3)  # Battleship 2 (3 cells)
place_battleship(table2, 4)  # Battleship 3 (4 cells)

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get the local machine hostname
host = socket.gethostname()
port = 1200

# Bind to the port
server_socket.bind((host, port))

# Wait for client connection
server_socket.listen(2)

print('Server-ul asculta pe {}:{}'.format(host, port))

# Establish connection with client
client1_socket, addr1 = server_socket.accept()
client1_socket.send(serialize_data(['Player 1, vei face prima mutare!', table1]).encode())
# send_table(client1_socket, table1)

client2_socket, addr2 = server_socket.accept()
client2_socket.send(serialize_data(['Player 2, vei face a doua mutare!', table2]).encode())
# send_table(client2_socket, table2)

print(f'Player 1 cu adresa {addr1} s-a conectat')
print(f'Player 2 cu adresa {addr2} s-a conectat')
print('Incepe jocul!')

# Print clients tables
print("Avioanele de pe tabela lui Player 1")
print_table(table1)

print("Avioanele de pe tabela lui Player 2")
print_table(table2)

# Send the tables to the clients

try:
    while True:
        # Receive move from client 1
        move = client1_socket.recv(1024).decode()
        move = json.loads(move)
        while move[0] < 1 or move[0] > 8 or move[1] < 1 or move[1] > 8:
            client1_socket.send('Invalid. Coordonatele trebuie sa fie in intervalul [1; 8]'.encode())
            move = client1_socket.recv(1024).decode()
            move = json.loads(move)

        client1_socket.send('Coordonate valide, se face tragerea...'.encode())
        print(f'Player1 a mutat: {move[0]} {move[1]}')
        fire(table2, move[0] - 1, move[1] - 1)

        # Receive move from client 2
        move = client2_socket.recv(1024).decode()
        move = json.loads(move)
        while move[0] < 1 or move[0] > 8 or move[1] < 1 or move[1] > 8:
            client2_socket.send('Invalid. Coordonatele trebuie sa fie in intervalul [1; 8]'.encode())
            move = client2_socket.recv(1024).decode()
            move = json.loads(move)

        client2_socket.send('Coordonate valide, se face tragerea...'.encode())
        print(f'Player2 a mutat: {move[0]} {move[1]}')
        fire(table1, move[0] - 1, move[1] - 1)

        ack1 = client1_socket.recv(1024).decode()
        ack2 = client2_socket.recv(1024).decode()

        if "ACK" in ack1 and "ACK" in ack2:
            # send confirmation that the shots were fired by both players
            # if ok1 and ok2:
            #     client1_socket.send('Fire OK'.encode())
            #     client2_socket.send('Fire OK'.encode())
            # else:
            #     continue

            # Send the tables to the clients
            send_table(client1_socket, [table1, table2])
            send_table(client2_socket, [table2, table1])

            # Print clients tables
            print("Avioanele de pe tabela lui Player 1")
            print_table(table1)

            print("Avioanele de pe tabela lui Player 2")
            print_table(table2)

            # check win
            if check_win(table1):
                print("Player 2 a castigat!")
                client2_socket.send('Felicitari, ai castigat jocul!'.encode())
                client1_socket.send('De aceasta data ai pierdut! Mai incearca!'.encode())
                client1_socket.close()
                client2_socket.close()
                break
            if check_win(table2):
                print("Player 1 a castigat!")
                client1_socket.send('Felicitari, ai castigat jocul!'.encode())
                client2_socket.send('De aceasta data ai pierdut! Mai incearca!'.encode())
                client1_socket.close()
                client2_socket.close()
                break
            client1_socket.send('Jocul continua!'.encode())
            client2_socket.send('Jocul continua!'.encode())
            continue
except KeyboardInterrupt:
    print("\nCTRL+C detected, exiting...")
    client1_socket.close()
    client2_socket.close()
