#!/usr/bin/env python

import socket
import json
from json import JSONDecodeError


def serialize_data(data):
    return json.dumps(data)


# Function to print the grid
def print_table(grid):
    # Print header with column numbers
    header = "   " + " ".join(str(i) for i in range(1, len(grid[0]) + 1))
    print(header.rstrip())  # Remove trailing space
    print("-" * (len(header) + 1))  # Header separator

    # Print rows with row numbers and contents
    for row_num, row in enumerate(grid, start=1):
        row_display = [str(cell) for cell in row]  # Convert each cell to string
        print(f"{row_num} | {' '.join(row_display)}")


# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get the local machine hostname
host = socket.gethostname()
port = 1200

# Connect to the server
client_socket.connect((host, port))

try:
    # Receive welcome message from server
    received_data = client_socket.recv(1024).decode()
    received_data = json.loads(received_data)
    print(received_data[0])

    # Receive his table from server (with 3 random battleships)
    # received_data = client_socket.recv(1024).decode()
    table = received_data[1]
    print("Incepe jocul, pregateste-te sa introduci coordonatele liniei si a coloanei unde vrei sa faci tragerea.")

    # Print the table
    print_table(table)
    try:
        while True:
            # Enter a move and send it to the server
            row = input('Introdu coordonatele liniei: ')
            col = input('Introdu coordonatele coloanei: ')
            row = int(row)
            col = int(col)
            client_socket.send(serialize_data([row, col]).encode())
            received_data = client_socket.recv(1024).decode()
            if 'Invalid' in received_data:
                print(received_data)
                continue
            else:
                print(received_data)

            client_socket.send("ACK".encode())

            print("Tabela ta cu avioane este:\n")
            received_data = client_socket.recv(1024).decode()
            table = json.loads(received_data)
            print_table(table[0])  # my table
            print("Tabela inamicului cu avioane este:\n")
            table[1] = [['O' if cell == 'X' else cell for cell in row] for row in table[1]]
            print_table(table[1])  # enemy table

            # wait for confirmation
            # received_data = client_socket.recv(1024).decode()
            # if "OK" in received_data:
            #     # receive tables after the move
            #     print("Tabela ta cu avioane este:\n")
            #     received_data = client_socket.recv(1024).decode()
            #     table = json.loads(received_data)
            #     print_table(table[0])  # my table
            #     print("Tabela inamicului cu avioane este:\n")
            #     table[1] = [['O' if cell == 'X' else cell for cell in row] for row in table[1]]
            #     print_table(table[1])  # enemy table

            received_data = client_socket.recv(1024).decode()
            if 'castigat' in received_data:
                print(received_data)
                client_socket.close()
                break
            elif 'pierdut' in received_data:
                print(received_data)
                client_socket.close()
                break
            else:
                print(received_data)
                continue
    except ConnectionResetError as e:
        print('\nConexiunea cu server-ul s-a pierdut.', e)
    except ConnectionAbortedError as e:
        print('\nConexiunea cu server-ul s-a pierdut.', e)
    except JSONDecodeError as e:
        print('\nConexiunea cu server-ul s-a pierdut.', e)

except KeyboardInterrupt:
    print("\nCTRL+C detected, exiting...")
