# -*- coding: utf-8 -*-
"""
TC2008B. Sistemas Multiagentes y Gráficas Computacionales
RandomAgents.py | 2022
Salvador Federico Milanes Braniff
Juan Muniain Otero
Miguel Bustamante Perez
Manuel Barrera Lopez Portillo

Random agents model. Based on the code provided by Sergio Ruiz & Octavio Navarro.
This model consists of a grid with a number of agents and packages. 
The agents move randomly and can pick up a package if they are in the same
cell. The agents can drop a package if they are in the same cell as
the depot. The depot is a special cell that is always in the same position and can store X packages.
"""

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import Grid

class RandomAgent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of four directions (WASD)
    """
    def __init__(self, unique_id, typeStr, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.direction = 4
        self.typeStr = typeStr

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right).
            include_center=True) 
        
        # Checks which grid cells are empty
        freeSpaces = list(map(self.model.grid.is_cell_empty, possible_steps))

        # If the cell is empty, moves the agent to that cell; otherwise, it stays at the same position
        if freeSpaces[self.direction]:
            self.model.grid.move_agent(self, possible_steps[self.direction])
            print(f"Moving from {self.pos} to {possible_steps[self.direction]}; direction {self.direction}")
        else:
            print(f"Can't move from {self.pos} in that direction.")

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.direction = self.random.randint(0,4)
        print(f"Agent: {self.unique_id} movement {self.direction}")
        self.move()

class ObstacleAgent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, typeStr, model):
        super().__init__(unique_id, model)
        self.typeStr = typeStr

    def step(self):
        pass   

class PackageAgent(Agent):
    """
    Package agent. Package can be picked up by agent and placed in a port.
    """
    def __init__(self, unique_id, typeStr, model):
        super().__init__(unique_id, model)
        self.typeStr = typeStr

    def step(self):
        pass

class PortAgent(Agent):
    """
    Port agent. Port can receive up to X packages, stacked on top of each other.
    """
    def __init__(self, unique_id, typeStr, model):
        super().__init__(unique_id, model)
        self.typeStr = typeStr

    def step(self):
        pass

class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, N, P, width, height):
        self.num_agents = N
        self.num_packages = P
        self.grid = Grid(width,height,torus = False) 
        self.schedule = RandomActivation(self)
        self.running = True

        # Creates the border of the grid
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]

        for pos in border:
            obs = ObstacleAgent(pos, "OBS",self)
            self.schedule.add(obs)
            self.grid.place_agent(obs, pos)

        # Add the agent to a random empty grid cell
        for i in range(self.num_agents):
            a = RandomAgent(i+1000, "ROB", self) 
            self.schedule.add(a)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(a, pos)

        # Add the package to a random empty grid cell
        for i in range(self.num_packages):
            b = PackageAgent(i+2000, "PKG", self) 
            self.schedule.add(b)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(b, pos)

        # Add the ports at chosen locations
        for i in range(self.num_ports):
            c = PortAgent(i+3000, "PRT", self)
            self.schedule.add(c)
    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
