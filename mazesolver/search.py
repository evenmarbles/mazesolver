import math, random
from pyailib.planner import search
from pyailib.common import datastructs

class ProblemImpl(search.Problem):
    """Implementation of the search problem 
    
    Attributes:
        _world (environment.World): The world object.
        _initial (int):             The initial state.
        _terminal (int):            The terminal state.

    Args:
        world (environment.World):  The world object.
    """
    def __init__(self, world):
        super(ProblemImpl, self).__init__(world, [(cell.x, cell.y) for cell in world.findCells('o')], random.choice([(cell.x, cell.y) for cell in world.findCells('?')]))

    def getSuccessor(self, state):
        """Finds all valid successors.
        
        Args:
            state (int):    The state.

        Returns:
            list:  A list of (action, state) tuples, representing the valid neighbors
        """
        cell = self._world.getCell(datastructs.Point2D(state[0], state[1]))

        successor = []
        for i, loc in enumerate(cell.neighbors):
            cell = self._world.getCell(loc)
            if not cell.isOccupied():
                successor.append((i, (loc.x, loc.y)))

        return successor

    def h(self, n):
        """The hypothesis function. Here the Euclidean distance is used.
        
        Args:
            n (planner.search.Node):    The current node.
        
        Returns:
            float:  The hypothesised cost to the terminal state.
        """
        dx = abs(n.state[0] - self._terminal[0])
        dy = abs(n.state[1] - self._terminal[1])
        n.h = math.sqrt(dx * dx + dy * dy)
        return n.h
