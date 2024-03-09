import os
import requests
from z3 import *



class HidatoSolver:
    def __init__(self):
        self.board = []
        self.pairs = []
        self.holes = []
        self.max_num = 0

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_board_from_input(self):
        while True:
            self.clear()
            k = input("Board size: ")
            if k.isdigit() and int(k) >= 2:
                break

        k = int(k)
        t_height = 2 * (k - 1)
        t_width = 4 * (k - 1)
        self.max_num = 3 * k * (k - 1) + 1
        # build pairs list
        first = 0
        last = t_width

        for i in range(int(t_height / 2), -1, -1):
            for j in range(first, last + 1, 2):
                self.pairs.append((i, j))
            first += 1
            last -= 1

        first = 1
        last = t_width - 1
        for i in range(int(t_height / 2) + 1, t_height + 1):
            for j in range(first, last + 1, 2):
                self.pairs.append((i, j))
            first += 1
            last -= 1
        
        self.pairs.sort(key=lambda pair: pair[0])

        # build board
        self.board = [[' '] * (t_width + 1) for _ in range(t_height + 1)]
        for (i, j) in self.pairs:
            self.board[i][j] = '-'

        # fill user input
        exists = []
        index = 0
        while index < len(self.pairs):
            i, j = self.pairs[index]
            while True:
                self.clear()
                if self.board[i][j] != '-':
                    if self.board[i][j] == '0':
                        self.holes.remove((i, j))
                    else:
                        exists.remove(int(self.board[i][j]))
                    self.board[i][j] = '-'
                self.print_board(highlight=(i, j))
                value = input("Enter a number for the marked spot (-1 to go back, 0 for hole): ")
                if not value:
                    index += 1
                    break
                if value == '-1':
                    if index == 0: 
                        continue
                    index -= 1
                    break
                if value.isdigit():
                    value = int(value)
                    if value < 0 or value > self.max_num or value in exists:
                        continue 
                    if value == 0:
                        self.holes.append((i ,j))
                    if value >= 1 and value <= self.max_num and value not in exists:
                        exists.append(value)
                    self.board[i][j] = str(value)
                    index += 1
                    break
        self.pairs = [pair for pair in self.pairs if pair not in self.holes]
        self.max_num = len(self.pairs)

    def get_board_from_web(self, board_id):
        board_id = board_id.split('-')
        level = board_id[1]
        id = board_id[2]
        url = "https://www.doo-bee-toys.com/src/getpuzz.php?level=" + level + "&id=" + id + "&type=h"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
        result = requests.get(url, headers=headers)
        data = result.json()
        t_height = data['r']
        t_width = data['c']
        self.max_num = t_width * t_height
        for row in range(t_height):
            newrow = []
            even = row % 2 == 0
            for col in range(t_width):
                value = data['p'][row * t_width + col]
                if value == -2:
                    value = ' '
                elif value == -4:
                    value = '0'
                elif value > self.max_num:
                    value = '-'
                else:
                    value = str(value)
                if even:
                    newrow.append(str(value))
                    newrow.append(' ')
                else:
                    newrow.append(' ')
                    newrow.append(str(value))
            self.board.append(newrow)

        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                value = self.board[row][col]
                if value == '-' or (value != '0' and value.isdigit()):
                    self.pairs.append((row,col))
                elif value == '0':
                    self.holes.append((row, col))

        self.max_num = len(self.pairs)

    def print_board(self, highlight=None, title="Board:"):
        print(title + "\n")
        for row in range(len(self.board)):
            rowtext = ""
            for col in range(len(self.board[row])):
                text = "X" if highlight and (row, col) == highlight else self.board[row][col]
                padding = len(str(self.max_num)) - len(text)
                padding_left = ' ' * int(padding / 2)
                padding_right = ' ' * (int(padding / 2) + (padding % 2))
                rowtext += padding_left + text + padding_right
            print(rowtext)
        print()

    def neighbors(self, pair):
        i, j = pair
        potentials =  [(i, j-2), (i, j+2), (i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
        neighbors = [(x, y) for (x,y) in potentials if (x, y) in self.pairs]
        return neighbors

    def solve_board(self):
        # make vars
        vars = [[None] * (len(self.board[0])) for _ in range(len(self.board))]
        for (i, j) in self.pairs:
                vars[i][j] = Int(f'pair_({i}, {j})') 

        s = Solver()
        # constraints:
        # values should be distinct (except for self.holes) and within the range of [1, max_num]
        s.add(Distinct([vars[i][j] for (i, j) in self.pairs]))
        s.add(And([vars[i][j] > 0 for (i, j) in self.pairs]))
        s.add(And([vars[i][j] <= self.max_num for (i, j) in self.pairs]))
        # fixed values
        for (i, j) in self.pairs:
            if self.board[i][j] != '-':
                s.add(vars[i][j] == self.board[i][j])
        # for each cell, if its value isn't max_num, one of its neighbors must be its successor
        for (i, j) in self.pairs:
                s.add(
                    Or(
                        Or([vars[n_i][n_j] == (vars[i][j] + 1) for (n_i, n_j) in self.neighbors((i, j))]),
                        vars[i][j] == self.max_num))

        if str(s.check()) == "unsat":
            return False
        else:
            try:
                m = s.model()
            except:
                print("Terminated")
            else:
                for (i, j) in self.pairs:
                    self.board[i][j] = "0" if (i, j) in self.holes else str(m.eval(vars[i][j]))