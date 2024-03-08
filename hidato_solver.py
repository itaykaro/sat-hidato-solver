import os
from z3 import *

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

clear()
k = input("Board size: ")
while not k.isdigit():
    os.system('cls' if os.name == 'nt' else 'clear')
    k = input("Board size: ")
k = int(k)
s = Solver()
t_size = 4 * (k - 1)
max_num = 3 * k * (k - 1) + 1

def print_board(board, highlight=None, solution=False, title=True):
    print(("Solution:\n" if solution else "Board:\n") if title else "")
    for row in range(len(board)):
        rowtext = ""
        for col in range(len(board)):
            text = "X" if highlight and (row, col) == highlight else board[row][col]
            padding = len(str(max_num)) - len(text)
            padding_left = ' ' * int(padding / 2)
            padding_right = ' ' * (int(padding / 2) + (padding % 2))
            rowtext += padding_left + text + padding_right
        if not rowtext.isspace():
            print(rowtext)
    print()

def neighbors(pair):
    i, j = pair
    potentials =  [(i, j-2), (i, j+2), (i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
    neighbors = [(x, y) for (x,y) in potentials if (x, y) in pairs]
    return neighbors

first = 0
last = t_size

#  build pairs list
pairs = []
for i in range (int(t_size / 2), k - 2, -1):
    for j in range(first, last + 1, 2):
        pairs.append((i, j))
    first += 1
    last -= 1

first = 1
last = t_size - 1
for i in range (int(t_size / 2) + 1, t_size - k + 2):
    for j in range(first, last + 1, 2):
        pairs.append((i, j))
    first += 1
    last -= 1

pairs.sort(key=lambda pair: pair[0])

# build board
board = [[' '] * (t_size + 1) for _ in range(t_size + 1)]
for (i, j) in pairs:
    board[i][j] = '-'

# make vars
vars = [[None] * (t_size + 1) for _ in range(t_size + 1)]
for (i, j) in pairs:
    vars[i][j] = Int(f'pair_({i}, {j})') 

# add constraints - values should be distinct and within the range of [1, max_num]
s.add(Distinct([vars[i][j] for (i, j) in pairs]))
s.add(And([vars[i][j] > 0 for (i, j) in pairs]))
s.add(And([vars[i][j] <= max_num for (i, j) in pairs]))

# fill user input
exists = []
index = 0
while index < len(pairs):
    i, j = pairs[index]
    while True:
        clear()
        if board[i][j] != '-':
            exists.remove(int(board[i][j]))
            board[i][j] = '-'
        print_board(board, (i, j))
        value = input("Enter number for the marked spot (-1 to go back): ")
        if not value:
            index += 1
            break
        if value == '-1':
            if index == 0: continue
            index -= 1
            break
        if value.isdigit():
            value = int(value)
            if value >= 1 and value <= max_num and value not in exists:
                exists.append(value)
                board[i][j] = str(value)
                index += 1
                break

# add constraints - fixed values
for (i, j) in pairs:
    if board[i][j] != '-':
        s.add(vars[i][j] == board[i][j])

clear()
print_board(board)
print("Solving...")

# add constraints - for each cell, if its value isn't max_num, one of its neighbors must be its successor
for (i, j) in pairs:
    s.add(Or(Or([vars[n_i][n_j] == (vars[i][j] + 1) for (n_i, n_j) in neighbors((i, j))]), vars[i][j] == max_num))

if str(s.check()) == "unsat":
    print("No solution!")
else:
    clear()
    print_board(board)
    print("Solved!")
    m = s.model()
    for (i, j) in pairs:
        board[i][j] = str(m.eval(vars[i][j]))
    print_board(board, solution=True)
