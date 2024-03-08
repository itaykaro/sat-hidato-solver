# Hidato Puzzle Solver

Hidato puzzle solver using the Z3 SMT solver.<br />
Hidato is an Israeli puzzle game.<br />
Solving hidato, similarly to sudoku, [is an NP-complete problem](https://www.nearly42.org/cstheory/hidato-is-np-complete/)

## Instructions
Currently, the solver only works with regular-hexagon-shaped boards.<br />
Support for other board shapes will be added in the future.<br />
First, choose the board size, i.e. the length of each size of the hexagon:
```
Board size: 6
```
Then, fill in the board, for example:
```
          35  32  -   -   -   -
        -   -   -   -   -   26  -
      -   -   -   42  -   27  -   -
    -   -   -   -   -   -   19  -   3
  -   -   -   46  -   -   -   -   1   -
52  -   -   48  -   13  10  -   -   -   -
  55  -   -   -   -   -   -   -   -   -
    -   -   -   73  -   -   83  85  -
      -   58  74  -   70  -   -   -
        -   -   -   -   -   -   -
          -   63  -   -   91  -
```
Finally, the solver will print the correct solution, if it exists:
```
Solution:

          35  32  31  30  24  23
        36  34  33  29  25  26  22
      37  40  41  42  28  27  20  21
    38  39  45  44  43  16  19  2   3
  51  50  47  46  14  15  17  18  1   4
52  53  49  48  79  13  10  9   8   7   5
  55  54  77  78  80  12  11  84  86  6
    56  76  75  73  81  82  83  85  87
      57  58  74  72  70  69  68  88
        59  61  62  71  66  67  89
          60  63  64  65  91  90
```
