import sys

class Node():
    """Generate a node.
    
    Make a node that has been searched, and the node has
    the information of a state, a parent, and an action.
    
    Attributes:
        state: A string indicating if the current state is 
        the goal or not.
        parent: A node just before.
        action: An movement information of agent.
    """
    
    def __init__(self, state, parent, action):
        """Init Node Class with a state, a parent, and an action."""
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    """Manage a frontier for DFS(Depth-First Search).
    
    DFS uses 'stack' data structure featuring the LIFO(Last In First Out)
    So a new node goes into the last of a frontier.
    And the last one comes out first.
    """
    
    def __init__(self):
        """Init StackFrontier Class with a empty list."""
        self.frontier = []

        
    def add(self, node):
        """Add a node to the frontier."""
        self.frontier.append(node)

        
    def contains_state(self, state):
        """Check a node is already in the frontier."""
        return any(node.state == state for node in self.frontier)

    
    def empty(self):
        """Check the frontier is empty."""
        return len(self.frontier) == 0

    
    def remove(self):
        """Remove the last node from the frontier."""
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):
    """Manage a frontier for BFS(Breadth-First Search).
    
    BFS uses 'queue' data structure featuring the FIFO(First In First Out)
    So a new node goes into the last of a frontier.
    And the first one comes out first.
    """
    
    def remove(self):
        """Remove the first node from the frontier."""
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze():
    """Find a optimal route from the start to the end of a given maze.
    
    Figure out whole of the maze by reading a file.
    Find the best route from the start to the end of it.
    
    Attributes:
        filename: A file of the maze structure.
        state: A condition of the agent in the environments.
    """
    
    def __init__(self, filename):
        """Figure out a structure of maze by reading a file."""
        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("S") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("E") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "S":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "E":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None


    def print_out(self):
        """Print out the best route from the start to the end."""
        solution = self.solution[1] if self.solution is not None else None
        print '\n'
        pre_solution_list = []
        for i, row in enumerate(self.walls):
            temp_route_list = []
            for j, col in enumerate(row):
                if col:
                    temp_route_list.append("x")
                elif (i, j) == self.start:
                    temp_route_list.append("S")
                elif (i, j) == self.goal:
                    temp_route_list.append("E")
                elif solution is not None and (i, j) in solution:
                    temp_route_list.append("*")
                else:
                    temp_route_list.append(" ")
            pre_solution_list.append(temp_route_list)
        solution = [ ''.join(each_solution) for each_solution in pre_solution_list ]
        print '\n'.join(solution) + '\n'


    def neighbors(self, state):
        """Move to adjacent node."""
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result


    def solve(self):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)
                print action, state


    def output_image(self, filename, show_solution=True, show_explored=False):
        """Draw an image of a optimal route."""
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)


if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
print "Maze:"
m.print_out()
print "Solving..." 
m.solve()
print "States Explored:", m.num_explored
print "Solution:"
m.print_out()
m.output_image("maze.png", show_explored=True)
