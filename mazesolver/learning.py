import numpy as np

from pyailib.learning import qlearning
from pyailib.core import aicore
from pyailib.common import datastructs

class RLProblemImpl(qlearning.RLProblem):
    """Implementation of the reinforcemnt learning problem. 
    This acts as the interface between the learning agent and the environment.
    
    Attributes:
        _world (environment.World): The world object.
        _initial (int):             The initial state. Defaults to None.
        _terminal (int):            The terminal state. Defaults to None.
        _cdf (numpy.Array):         The cumulative transition probabilties read from the configuration.  

    Args:
        world (environment.World):  The world object.
    """
    _actionMap = {
            0: "up",
            1: "right",
            2: "down",
            3: "left"
        }


    def __init__(self, world):
        """Initializes the RLProblem class"""
        super(RLProblemImpl, self).__init__(world, None, [cell.y*world.width+cell.x for cell in world.findCells('?')])
        self._cdf = cdf = np.array(world.getConfig('probabilities')).cumsum()



    def getActionStr(self, action):
        """Converts the action into a string."""
        return self._actionMap[action]

    def stateFromLocation(self, loc):
        """Determins the state from the given x, y location
        
        Args:
            loc (datastructs.Point2D):    The location to determine the state from

        Returns:
            int:    The state
        """
        return loc.y * self._world.width + loc.x

    def locationFromState(self, state):
        """Determins the location from the given state
        
        Args:
            state (int):    The state

        Returns:
            datastructs.Point2D:    The location determined from the state
        """
        return datastructs.Point2D(state % self._world.width, state / self._world.width)

    def actions(self, state):
        """Returns the actions available in the given state
        
        Args:
            state (int):   The state to find the actions for
        
        Returns:
            list: A list of actions
        """
        loc = self.locationFromState(state)
        cell = self._world.getCell(loc)

        #actions = []
        #for i, loc in enumerate(cell.neighbors):
        #    cell = self._world.getCell(loc)
        #    if not cell.isOccupied():
        #        actions.append(i)
        #return actions

        return [i for i, loc in enumerate(cell.neighbors)]

    def act(self, state, action):
        """"Determines the reward and new state based on the given state and action.
        This function is subject to the transition probabilities.

        Note: transition probabilities from self._world.getConfig("transition")
        
        Args:
            state (int):   The state to consider
            action (int):  The action to perform
            
        Returns:
            float:  The reward
            int:    The new state
        """
        randVal = np.random.random()
        for probAction, prob in enumerate(self._cdf):
            if prob > randVal:
                break
        
        loc = self.locationFromState(state)
        cell = self._world.getCell(loc)

        if probAction == 5:
            # Stay put
            return self.__getReward(cell), state

        if probAction is not 0:
            # A random action is chosen
            action = probAction - 1

        _loc = self._world.moveCoords(cell, action)
        newCell = self._world.getCell(_loc)
        if newCell.isOccupied():
            return self.__getReward(newCell), state

        return self.__getReward(newCell), self.stateFromLocation(_loc)

    def __getReward(self, cell):
        """Determine reward for the current state based on the configuration.
        
        Args:
            cell (environment.Cell):    The current cell

        Returns:
            float:  The reward for the cell.
        """
        rewards = self._world.getConfig("rewards")
        for x in rewards:
            if x["id"] == cell.data:
                return x["value"]
        return 0.0


class LearnAgent(aicore.Agent):
    """Implementation of an agent performing Q-learning (reinforcement learning)
    on a problem definition.
    
    Attributes:
        _id (string):               The agent identifier.
        _loc (datastructs.Point2D):   The current location of the agent.
        _facing (float):            The current facing of the agent.
        _ai (object):               The AI module.
        _state (int):               The agents current state.

    Args:
        id (string):                The agent identifier.
        loc (datastructs.Point2D):    The location of the agent.
        facing (float):             The facing of the agent.
        ai (object):                The AI module.
    """
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value


    def __init__(self, id, loc, facing, ai):
        """Initialization of the agent"""
        super(LearnAgent, self).__init__(id, loc, facing, ai)
        self._state = self._ai.problem.stateFromLocation(loc)

    def update(self):
        """Update the agent at every time step. The agent performs its 
        think-action loop here."""
        action = self._ai.chooseAction(self.state)
        reward, newState = self._ai.problem.act(self.state, action)
        self._ai.learn(self.state, action, reward, newState)
        self.state = newState
        self._loc = self._ai.problem.locationFromState(newState)

    def isDone(self):
        """Checks if the terminal state has been reached.
        
        Returns:
            boolean:    True if the terminal state has been reached, False otherwise.
        """
        return self._ai.problem.isTerminal(self.state)

    def setLocation(self, loc):
        """Set the agents location to the new coordinates.
        
        Args:
            loc (datastructs.Point2D):    The new location of the agent.
        """
        super(LearnAgent, self).setLocation(loc)
        self._state = self._ai.problem.stateFromLocation(loc)
