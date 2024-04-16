import sys

file_name = sys.argv[1]
nr_lines = int(sys.argv[2])
try:
    f = open(file_name, 'r')
    lines = 0
    ok = 1
    while ok == 1:
        for _ in range(nr_lines):
            line = f.readline()
            if not line:
                ok = 0
                break
            print(line, end='')
        command = input()
        if command == 'q':
            break
except FileNotFoundError:
    print('Invalid filename')



