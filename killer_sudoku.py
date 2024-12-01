import subprocess
from itertools import permutations
from argparse import ArgumentParser

# Load the instance
def load_instance(file_name):
    with open(file_name, "r") as file:
        n = int(next(file))
        cages = []
        for line in file:
            line = line.strip()
            if line:
                cage_str, sum_str = line.split(":")
                cage_sum = int(sum_str)
                cage = []
                for cell in cage_str.strip().split():
                    x, y = cell.split(",")
                    cage.append((int(x),int(y)))
                cages.append((cage,cage_sum))
    return cages, n

# Helper function for the cage sum constraints that finds all permutations for a sum using the number of cells provided, and the digits provided
def find_permutations(start, end, cells, cage_sum):
    numbers = list(range(start, end + 1))
    
    all_permutations = permutations(numbers, cells)
    
    valid_permutations = [perm for perm in all_permutations if sum(perm) == cage_sum]
    
    return valid_permutations

# Encodes the grid to a cnf DMACS format
def encode(cages, n):
    clauses = []

    def variable_id(row, column, number):
        return row * n * n + column * n + number + 1
    
    id_count = n*n*n
    
    # Exactly one number on each cell
    for row in range (n):
        for column in range(n):
            clause = []
            # At least one number on each cell
            for number in range(n):
                variable = variable_id(row,column,number)
                clause.append(variable)
            clauses.append(clause)
            # At most one number on each cell
            for number_1 in range(n):
                v_1 = variable_id(row,column,number_1)
                for number_2 in range(number_1 +1, n):
                    v_2 = variable_id(row,column,number_2)
                    clause = [-v_1,-v_2]
                    clauses.append(clause)

    # Every number is in every row exactly once
    for row in range(n):
        for number in range(n):
            clause = []
            # At least once
            for column in range(n):
                variable = variable_id(row,column,number)
                clause.append(variable)
            clauses.append(clause)
            # At most once
            for column_1 in range(n):
                v_1 = variable_id(row,column_1,number)
                for column_2 in range(column_1 +1, n):
                    v_2 = variable_id(row,column_2,number)
                    clause = [-v_1,-v_2]
                    clauses.append(clause)

    # Every number is in every colymn exactly once
    for column in range(n):
        for number in range(n):
            clause = []
            # At least once
            for row in range(n):
                variable = variable_id(row,column,number)
                clause.append(variable)
            clauses.append(clause)
            # At most once
            for row_1 in range(n):
                v_1 = variable_id(row_1, column, number)
                for row_2 in range(row_1 + 1, n):
                    v_2 =variable_id(row_2, column, number)
                    clause = [-v_1, -v_2]
                    clauses.append(clause)
            
    #  Every number is in every subsquare
    sqrt_n = int(n ** 0.5)
    # Go through the top left corner of every subsquare
    for sub_row in range(0,n,sqrt_n):
        for sub_column in range(0,n,sqrt_n):
            # Go through every number
            for number in range(n):
                clause = []
                # At least once
                for row in range(sub_row, sub_row+ sqrt_n):
                    for column in range(sub_column, sub_column+sqrt_n):
                        variable = variable_id(row, column, number)
                        clause.append(variable)
                clauses.append(clause)
                subsquare = clause
                # At most once
                for cell_1 in range(n):
                    v_1 = subsquare[cell_1]
                    for cell_2 in range(cell_1 + 1, n):
                        v_2 = subsquare[cell_2]
                        clause = [-v_1, -v_2]
                        clauses.append(clause)

    # All cages must sum to their respective sum
    for cells, cage_sum in cages:
        additional_variables = []
        # Find permutations, and ensure that two same numbers cannot be in one cage
        permutations = find_permutations(1,n,len(cells),cage_sum)
        for perm in permutations:
            id_count +=1
            # Helper variable for cage constraint
            new_var = id_count
            additional_variables.append(new_var)
            for i in range(len(cells)):
                row, column = cells[i]
                value = perm[i]
                var = variable_id(row, column, value - 1)
                # If new_var is true, then, var is true also
                clause = [var, -new_var]
                clauses.append(clause)
        clauses.append(additional_variables)

    return clauses, id_count

# Calls the SAT solver and inserts the cnf file
def call_solver(clauses, variables_count, output, solver, verb):
    with open(output, "w") as file:
        file.write(f"p cnf {variables_count} {len(clauses)}\n")
        for clause in clauses:
            file.write(' '.join(str(var) for var in clause) + ' 0\n')

    return subprocess.run(['./' + solver, '-model', '-verb=' + str(verb) , output], stdout=subprocess.PIPE)

# Prints the solution
# Decodes the results from the SAT solver to a human readable format
def print_result(result, n):
    for line in result.stdout.decode('utf-8').split('\n'):
        print(line)

    if (result.returncode == 20):
        return
    
    model = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if line.startswith("v"):
            vars = line.split(" ")
            vars.remove("v")
            model.extend(int(v) for v in vars)      
    model.remove(0)

    print()
    print("Human readable result of solved Sudoku grid:")
    print()

    grid = [[0 for _ in range(n)] for _ in range(n)]

    # Create a grid that uses the solution variables
    for var in model:
        if var > 0 and var <= n * n * n:
            var_id = var - 1
            row = var_id // (n * n)
            col = (var_id % (n * n)) // n
            num = (var_id % n) + 1
            grid[row][col] = num

    # Print the grid in a human-readable format
    for row in grid:
        print(' '.join(str(num) for num in row))

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help=(
            "Input file, default: input.in"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file whre the CNF formula is printed, default: formula.cnf"
        ),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose",
        type=str,
        help=(
            "SAT Solver, default: glucose"
        ),
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0,2),
        help=(
            "Verbosity of SAT Solver, try 0 or 1, default: 1"
        ),
    )

    arguments = parser.parse_args()

    # get the cages and the length/width of the grid
    cages, n = load_instance(arguments.input)

    # get the clauses and the number of variables
    clauses, variables_count = encode(cages, n)

    # call SAT solver to get the result
    result = call_solver(clauses, variables_count, arguments.output, arguments.solver, arguments.verb)

    # print the result from SAT solver, together with a humanly readable format
    print_result(result, n)

