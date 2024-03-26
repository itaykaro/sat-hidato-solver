import os
import requests
from sat import SAT

class Board:
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
        sat = SAT()

        # CONSTRAINTS

        # must have a value
        for pair in self.pairs:
            sat.add_clause([sat[pair, n] for n in range(1, self.max_num + 1)])

        # distinct
        for i in range(len(self.pairs)):
            for j in range(0, i):
                for n in range(1, self.max_num + 1):
                    sat.add_clause([-sat[self.pairs[i], n], -sat[self.pairs[j], n]])

        # fixed values
        for pair in self.pairs:
            i, j = pair
            if self.board[i][j] != '-':
                sat.add_clause([sat[pair, int(self.board[i][j])]])

        # neighbor successor
        for pair in self.pairs:
            for n in range(1, self.max_num):
                clause = [sat[pair, self.max_num], -sat[pair, n]]
                for neighbor in self.neighbors(pair):
                    clause.append(sat[neighbor, n + 1])
                sat.add_clause(clause)

        # END CONSTRAINTS

        # solve
        if not sat.solve():
            return 1
        
        # VERIFY

        # must have a value
        for pair in self.pairs:
            if not any([sat.value(pair, n) for n in range(1, self.max_num + 1)]):
                return 1

        # distinct
        for i in range(len(self.pairs)):
            for j in range(0, i):
                for n in range(1, self.max_num + 1):
                    if sat.value(self.pairs[i], n) and sat.value(self.pairs[j], n):
                        return 1

        # fixed values
        for pair in self.pairs:
            i, j = pair
            if self.board[i][j] != '-':
                if not sat.value(pair, int(self.board[i][j])):
                    return 1

        # neighbor successor
        for pair in self.pairs:
            if not sat.value(pair, self.max_num):
                for n in range(1, self.max_num):
                    if sat.value(pair, n) and not any(sat.value(neighbor, n + 1) for neighbor in self.neighbors(pair)):
                        return 1
        
        # END VERIFY

        # update solution
        for pair in self.pairs:
            for n in range (1, self.max_num + 1):
                if sat.value(pair, n):
                    i, j = pair
                    self.board[i][j] = str(n)  

        # CHECK IF LEGAL BOARD
        
        # add clause to make a different solution - atleast one pair has a different value
        clause = []
        for pair in self.pairs:
            for n in range (1, self.max_num + 1):
                if sat.value(pair, n):
                    clause.append(-sat[pair, n])
        sat.add_clause(clause)

        # if there is another solution, the board is illegal
        if sat.solve():
            return 2
        
        # END CHECK IF LEGAL BOARD

        return 0