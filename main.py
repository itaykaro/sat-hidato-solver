import re
from board import Board

board = Board()

while True:
    board.clear()
    print("Menu:\n1) Input board manually\n2) Fetch board from hidato.com")
    option = input("Choose option: ")
    if option in ['1', '2']:
        option = int(option)
        break

if option == 1:
    board.get_board_from_input()
elif option == 2:
    while True:
        board.clear()
        board_id = input("Board id (h-x-xxxxxx): ")
        if bool(re.match(r'^h-[1-6]-[0-9]{6}$', board_id.strip())):
            break
    board.clear()
    print("Fetching board...")
    board.get_board_from_web(board_id)

board.clear()
board.print_board()
print("Solving...")
res = board.solve_board()
if res == 1:
    print("No solution!")
elif res == 2:
    print("Illegal board!")
else:
    print("Solved!\n")
    board.print_board(title="Solution:")