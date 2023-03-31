import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            rm = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    rm.add(word)
            for word in rm:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        rt = False
        rm = set()
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return rt
        else:
            x_i, y_j = overlap
        for wordx in self.domains[x]:
            flag = True
            for wordy in self.domains[y]:
                if wordx[x_i] == wordy[y_j]:
                    flag = False
                    break
            if flag:
                rm.add(wordx)
                rt = True
            
        for word in rm:
            self.domains[x].remove(word)

        return rt

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is not None:
            queue = list(arcs)
        else:
            queue = []
            for x, y in self.crossword.overlaps:
                queue.append((x, y))
        
        while len(queue) != 0:
            x, y = queue.pop(0)

            if self.revise(x, y):
                if len(self.domains) == 0:
                    return False
                neighbors = self.crossword.neighbors(x)
                neighbors.remove(y)
                for z in neighbors:
                    queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if not (var in assignment and assignment[var] is not None):
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        # check if all values are distinct
        is_distinct = set()
        for var in assignment:
            #check if every value if the correct length
            if var.length != len(assignment[var]):
                return False
            
            is_distinct.add(assignment[var])
        if len(is_distinct) != len(assignment):
            return False
        
        # check there are no conflicts between neighboring variables.
        for i, j in self.crossword.overlaps:
            if i in assignment and j in assignment:
                if self.crossword.overlaps[i, j] is None:
                    continue
                x_i, y_j = self.crossword.overlaps[i, j]
                if assignment[i][x_i] != assignment[j][y_j]:
                    return False
                
        # all constraints are fullfilled
        return True
            
        

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        def elimination_num(value):
            num = 0
            for y in self.crossword.neighbors(var):
                if y not in assignment:
                    if (var, y) in self.crossword.overlaps:
                        var_i, y_j = self.crossword.overlaps[var, y]
                    elif (y, var) in self.crossword.overlaps:
                        y_j, var_i = self.crossword.overlaps[y, var]
                    for val in self.domains[y]:
                        if value[var_i] != val[y_j]:
                            num += 1
            return num
        
        rt_list = list(self.domains[var])
        #print(rt_list)
        sorted(rt_list, key=elimination_num)
        #print(rt_list)
        return rt_list
    

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassained = {
            var: self.domains[var]
            for var in self.domains.keys() - assignment.keys()
        }
        #print(unassained)
        unassained = dict(sorted(unassained.items(), key = lambda item: item[1]))
        minimun = []
        for item in unassained:
            if len(minimun) == 0:
                minimun.append(item)
            elif len(unassained[minimun[len(minimun) - 1]]) == len(unassained[item]):
                minimun.append(item)
            else:
                break
        if len(minimun) == 1:
            return minimun[0]
        
        rt = minimun[0]
        for var in minimun:
            if self.crossword.neighbors(var) > self.crossword.neighbors(rt):
                rt = var
        return rt

        


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var, assignment):
            assignment_copy = assignment.copy()
            assignment_copy[var] = val
            if self.consistent(assignment_copy):
                result = self.backtrack(assignment_copy)
                if result is not None:
                    return result
        
        return None




def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)

    #creator.enforce_node_consistency()

    #=======================================#
    #This is for debug
    #print(creator.select_unassigned_variable({}))
    #
    #=======================================#

    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
