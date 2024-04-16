import random


# Function to print the grid
def print_grid(grid):
    for row in grid:
        print(" ".join(row))


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


# Create an empty 8x8 grid
grid = [["O" for _ in range(8)] for _ in range(8)]


# Place battleships
place_battleship(grid, 2)  # Battleship 1 (2 cells)
place_battleship(grid, 3)  # Battleship 2 (3 cells)
place_battleship(grid, 4)  # Battleship 3 (4 cells)

# Print the grid
print_grid(grid)

ok = 0
for row in grid:
    for cell in row:
        if cell == 'X':
            ok += 1

if ok > 0:
    print("True")
else:
    print("False")
grid[0][0] = 'H'
grid = [['O' if cell == 'X' else cell for cell in row] for row in grid]
print_grid(grid)