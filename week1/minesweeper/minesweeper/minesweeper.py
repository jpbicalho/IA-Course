import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        #If the number of cells are equal of the number of mines
        if len(self.cells) == self.count:
            return self.cells
        else: 
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set() 

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # take out the cell from set and decrement the mines counter
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        #take out the cell from set but not decrementing the mines counter
        if cell in self.cells:
            self.cells.remove(cell)



class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_neighborhood(self,cell):
       
        neighbors = set()
        (i,j) = cell
        
        if i - 1 >= 0:
            if j - 1 >= 0:
                neighbors.add((i - 1, j - 1)) 
            else:
                neighbors.add((i - 1, j))  
        elif j - 1 >= 0:
            neighbors.add((i, j - 1))  

        if i + 1 < self.height:  
            if j + 1 < self.width:
                neighbors.add((i + 1, j + 1))
            else:
                neighbors.add((i + 1, j))  
        elif j + 1 < self.width:
            neighbors.add((i, j + 1))  

        return neighbors    

    def mark_cells(self):
        updated = True
        while updated:
            
            updated = False

            for sentence in self.knowledge:
                safes = sentence.known_safes()
                mines = sentence.known_mines()

                if safes:
                    self.safes.update(safes)
                    updated = True

                if mines:
                    self.mines.update(mines)
                    updated = True

                if safes or mines:
                    sentence.cells -= safes.union(mines)
                    sentence.count -= len(mines)
            self.knowledge = [s for s in self.knowledge if s.cells] 
    
    def infer_new_sentences(self):
        
        new_sentences = []
        
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1 == s2:
                    continue
            
                if s1.cells.issubset(s2.cells):
                    new_cells = s2.cells - s1.cells
                    new_count = s2.count - s1.count
                    new_sentence = Sentence(new_cells,new_count)
                    if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                        new_sentences.append(new_sentence)
        
        self.knowledge.extend(new_sentences)     

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        #1) marking the cell
        self.moves_made.add(cell)

        #2) marking as safe
        self.safes.add(cell)
        neighbors = self.get_neighborhood(cell)

        #3) add a new sentence
        unknown_nbg = {n for n in neighbors if n not in self.safes and n not in self.mines}
        if unknown_nbg:
            new_sentence = Sentence(unknown_nbg,count)
            self.knowledge.append(new_sentence)

        #4)mark cells 
        if count == 0:
            for n in neighbors:
                self.mark_safe(n)
        self.mark_cells()

        #5)infer new sentences
        self.infer_new_sentences()
        


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = self.safes - self.moves_made 
        if safe_moves:
            return safe_moves.pop()
        else: return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        #select all cells from the board
        all_cells = set()
        for i in range(self.width):
            for j in range(self.height):
                all_cells.add((i,j))

        #clean the mine's cells and the moves made
        random_moves = all_cells - self.mines - self.moves_made

        if random_moves:
            return random.choice(list(random_moves))
        else: return None