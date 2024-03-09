import re
from HidatoSolver import HidatoSolver

solver = HidatoSolver()

while True:
    solver.clear()
    print("Menu:\n1) Input board manually\n2) Fetch board from hidato.com")
    option = input("Choose option: ")
    if option in ['1', '2']:
        option = int(option)
        break

if option == 1:
    solver.get_board_from_input()
elif option == 2:
    while True:
        solver.clear()
        board_id = input("Board id (h-x-xxxxxx): ")
        if bool(re.match(r'^h-[1-6]-[0-9]{6}$', board_id.strip())):
            break
    solver.clear()
    print("Fetching board...")
    solver.get_board_from_web(board_id)

solver.clear()
solver.print_board()
print("Solving...")
if solver.solve_board() == False:
    print("No solution!")
else:
    solver.print_board(title="Solution:")