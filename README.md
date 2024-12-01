
# Killer Sudoku SAT Solver

This project presents a Killer Sudoku solver that reduces the puzzle to a SAT problem by encoding the constraints into a CNF (Conjunctive Normal Form) formula. The solver uses the Glucose SAT Solver.


## Problem Description

Killer Sudoku is a Sudoku puzzle, for which the objective is to fill an `n x n` grid with digits from 1 to `n` so that:

   - Each row contains each digit exactly once.
   - Each column contains each digit exactly once.
   - Each `√n x √n` block contains each digit exactly once.
   - The grid is partitioned into "cages," each with a specified target sum.
   - The sum of the digits within a cage must equal the target sum.
   - Digits within a cage must be unique (no repeats).

This solver finds a valid assignment of digits to the grid that satisfies all constraints.

## Encoding into CNF

The problem is encoded into CNF clauses suitable for input to a SAT solver. The encoding has these components:

### Propositional Variables

Variables are defined to represent the assignment of digits to cells:

- **Variables:** 
    $X_{r,c,d}$:
  - $(r)$: Row index (from 0)
  - $(c)$: Column index (from 0)
  - $(d)$: Digit (from 1 to $n$)

Each variable $( X_{r,c,d} )$ is **True** if and only if digit $( d )$ is placed in cell $(r, c)$.

**Variable IDs:**

Variables are mapped to unique positive integers using the formula:


$Variable ID = r 	\times n^2 + c 	\times n + (d - 1) + 1$

This mapping ensures compliance with the DIMACS CNF format, which requires variable IDs to be positive integers starting from 1.

### Constraints

The encoding includes the following constraints:

#### 1. **Cell Constraints**

Each cell must contain exactly one digit.

- **At least one digit in each cell:**

  For each cell $(r, c)$:

  $X_{r,c,1} \lor X_{r,c,2} \lor \dots \lor X_{r,c,n}$

- **At most one digit in each cell:**

  For each cell $(r, c)$ and all pairs $d_1 = d_2$:
  
  $\neg X_{r,c,d_1} \lor \neg X_{r,c,d_2}$

#### 2. **Row Constraints**

Each digit must appear exactly once in each row.

- **At least one occurrence of each digit in a row:**

  For each row $r$ and digit $d$:

  $X_{r,0,d} \lor X_{r,1,d} \lor \dots \lor X_{r,n-1,d}$

- **At most one occurrence of each digit in a row:**

  For each row $r$ , digit $d$, and columns $c_1 = c_2$:
  
  $\neg X_{r,c_1,d} \lor \neg X_{r,c_2,d}$


#### 3. **Column Constraints**

Each digit must appear exactly once in each column.

- **At least one occurrence of each digit in a column:**

  For each column $c$ and digit $d$:

  $X_{0,c,d} \lor X_{1,c,d} \lor \dots \lor X_{n-1,c,d}$

- **At most one occurrence of each digit in a column:**

  For each column $c$, digit $d$, and rows $r_1 = r_2$:
  
$\neg X_{r_1,c_1,d} \lor \neg X_{r_2,c_2,d}$

#### 4. **Block (Subgrid) Constraints**

Each digit must appear exactly once in each $\sqrt{n} 	\times \sqrt{n}$ block.

- **At least one occurrence of each digit in a block:**

  For each block and digit $d$, sum over all cells $(r, c)$ in the block:

  $X_{r,c,d}$

- **At most one occurrence of each digit in a block:**

  For each block, digit $d$, and pairs of cells $(r_1, c_1) = (r_2, c_2)$:

  $\neg X_{r_1,c_1,d} \lor \neg X_{r_2,c_2,d}$

#### 5. **Cage Sum Constraints**

For each cage with a target sum and a set of cells:

- **Generate Valid Combinations:**
  - Generate all permutations of digits (from 1 to $n$) for the number of cells in the cage.
  - Filter permutations where the digits are unique and sum to the target sum.

- **Helper Variables:**
  - Introduce a helper variable $H_i$ for each valid permutation $i$.

- **Linking Helper Variables to Cell Assignments:**
  - For each permutation $i$ and corresponding helper variable $H_i$:

    $(X_{r_1,c_1,d_1} \lor \neg H_i) \land (X_{r_2,c_2,d_2} \lor \neg H_i) \land \dots$

- **At Least One Valid Combination:**
  - Ensure that at least one helper variable is true:

    $H_1 \lor H_2 \lor \dots \lor H_k$


## User Documentation

### Script Usage

Run the solver using the following command:

```
python killer_sudoku.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}]
```

#### Command-Line Options

- `-h`, `--help`: Show a help message and exit.
- `-i INPUT`, `--input INPUT`: Input file, default: 'input.in'
- `-o OUTPUT`, `--output OUTPUT`: Output file whre the CNF formula is printed, default: 'formula.cnf'
- `-s SOLVER`, `--solver SOLVER`: SAT Solver, default: 'glucose'
- `-v {0,1}`, `--verb {0,1}`: Verbosity of SAT Solver,0 or 1, default: 1

### Input Format

The input file should contain:

- **First Line:** An integer $n$ specifying the size of the grid (e.g., `9` for a 9x9 grid).
- **Subsequent Lines:** Each line represents a cage in the format:

  ```
  x1,y1 x2,y2 ... xk,yk : sum
  ```

  - `x`, `y`: Row and column of the cage, starting from 0.
  - `sum`: Target sum for the cage.

**Example:**

```
4
0,0 0,1: 4
0,2 0,3: 6
1,0 1,1: 6
1,2 1,3: 4
2,0 3,0: 5
2,1 3,1: 5
2,2 2,3: 4
3,2 3,3: 6
```


## Example instances


* `4by4.in`: A solvable easy instance of a 4x4 grid
* `4by4-unsat.in`: An unsolvable instance of a 4x4 grid
* `9by9.in`: A solvable instance of a 9x9 grid
* `9by9-unsat.in`: An unsolvable instance of a 9x9 grid
* `16by16.in`: A solvable instance of a 16x16 grid (easy)
* `16by16-unsat.in`: An unsolvable instance of a 16x16 grid
* `16by16-hard.in`: A hard solvable instance of a 16x16 grid, it took my computer appx. 14 seconds to solve

Instances can be found in "instances" folder.

## Experiments

Experiments were conducted with gruds of different sizes (from 4x4 to 16x16) and different complexities. The execution time was measured using Python's `time` module. The results were plotted using`matplotlib`.

| *Grid Size* | *Avg Time SAT (s)* | *Avg Time UNSAT (s)* |
|------------:|:-------------------|:--------------------:|
|           4 | 0.037             | 0.034               |
|           9 | 0.059             | 0.057               |
|          16 | 4.094             | 8.584               |

A plot of the results can be found at (experiment_results/results-plot.jpg)

Looking at the data from the experiments, I can make a guess that time grows exponentially with respect to the grid size. Also, unsatisfiable instances take more time than satisfiable instances. I can guess that this happens because, once the solver finds the first solution, it stops looking, while for an unsatisfiable instance, it needs to continue looking for a solution until the end.