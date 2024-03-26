from subprocess import PIPE, call

class SAT:
    def __init__(self):
        self._clauses = []
        self._variables = {}
        self._value = None
        self.solved = False

    def __getitem__(self, *args) -> int:
        if not args in self._variables:
            ix = len(self._variables) + 1
            self._variables[args] = ix
        return self._variables[args]
    
    def add_clause(self, clause):
        self._clauses.append(clause)

    def num_variables(self):
        return len(self._variables)

    def num_clauses(self):
        return len(self._clauses)

    def print(self, io):
        print(f'p cnf {self.num_variables()} {self.num_clauses()}', file=io)
        for clause in self._clauses:
            print(' '.join(map(str, clause + [0])), file=io)

    def value(self, *args) -> int:
        return self._value[self[args]-1]

    def solve(self):
        with open('hidato_sat.cnf', 'w') as f:
            self.print(f)

        call(['minisat', 'hidato_sat.cnf', 'hidato_sat.out'], stdout=PIPE)

        self._solved = True

        with open('hidato_sat.out') as f:
            lines = f.read().strip(' \n').split('\n')
            if lines[0] == 'SAT':
                self._value = [int(x) > 0 for x in lines[1].split()[:-1]]
                return True
            else:
                return False