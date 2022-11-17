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
import math
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import Grid

# Global dictionary with all existing depot locations
depots = {}

class RandomAgent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of four directions (WASD)
    """
    hasPackage = False

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
        Moves the agent according to its current state.
        """
        # Check if robot is carrying a package
        print(f"Click, {self.hasPackage}")
        if(self.hasPackage):
            self.seekDepot()
        else:
            self.seekPackage()
        
    def seekPackage(self):
        """
        Moves the agent to a package if in neighboring cells.
        If no package is found, the agent moves randomly.
        """
        print("Seeking package")
        # print(f"Agent {self.unique_id} is seeking package")
        # Get the neighbors of the agent
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right).
            include_center=True)

        # Check if there is a package in the neighbors
        for pos in possible_steps:
            # If there is a package, move to it
            if(len(self.model.grid.get_cell_list_contents(pos)) > 0):
                if(self.model.grid.get_cell_list_contents(pos)[0].typeStr == "PKG"):
                    self.model.grid.move_agent(self, pos)
                    self.hasPackage = True
                    return
        
        # # If no package is found, move randomly
        self.random_move()

    def seekDepot(self):
        """
        Check all depot locations and approach the closest one.
        """
        print("Seeking depot")
        # Read the global dictionary with all depots, and get the closest one to the agent
        agentPositon = self.pos
        closestDepotPosition = None
        for val in depots.values():
            print(f"Depot: {val}")
            if(closestDepotPosition == None):
                closestDepotPosition = val
            else:
                if(self.distance(agentPositon, val) < self.distance(agentPositon, closestDepotPosition)):
                    closestDepotPosition = val          

        # If the agent is in the same cell as the depot, drop the package
        if(self.pos == closestDepotPosition):
            self.hasPackage = False
            return
        
        # Move to the closest depot by one step
        self.moveTowards(closestDepotPosition)

    def moveTowards(self, targetPosition):
        agentX = self.pos[0]
        agentY = self.pos[1]
        print(f"Rob: {self.pos}")
        depotX = int(targetPosition[0])
        depotY = int(targetPosition[1])
        print(f"Dep: {targetPosition}")
        possible_steps = []
        if(agentX < depotX):
            possible_steps.append((agentX + 1, agentY))
        elif(agentX > depotX):
            possible_steps.append((agentX - 1, agentY))

        if(agentY < depotY):
            possible_steps.append((agentX, agentY + 1))
        elif(agentY > depotY):
            possible_steps.append((agentX, agentY - 1))

        if len(possible_steps) > 0:
            # Choose a random direction
            new_position = self.random.choice(possible_steps)

            # Move the agent
            self.model.grid.move_agent(self, new_position)

    def random_move(self):
        """
        Move the agent to a random position.
        """
        # Get the neighbors of the agent
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right).
            include_center=True)

        # Choose a random direction
        new_position = self.random.choice(possible_steps)

        # Move the agent
        self.model.grid.move_agent(self, new_position)

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
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

    def pickup(self, agent):
        """
        Pick up package by agent.
        """
        print(f"Agent {agent.unique_id} picked up package {self.unique_id}")
        # self.model.grid.remove_agent(self)
        agent.hasPackage = True

    def drop(self, agent):
        """
        Drop package by agent.
        """
        print(f"Agent {agent.unique_id} dropped package {self.unique_id}")
        self.model.grid.place_agent(self, self.pos)
        agent.hasPackage = False
        

    def step(self):
        pass

class DepotAgent(Agent):
    """
    Depot agent. Depot can receive up to X packages, stacked on top of each other.
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
    def __init__(self, N, P, D, width, height):
        self.num_agents = N
        self.num_packages = P
        self.num_depots = D
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

            # pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            # pos = pos_gen(self.grid.width, self.grid.height)
            # while (not self.grid.is_cell_empty(pos)):
            #     pos = pos_gen(self.grid.width, self.grid.height)
            # self.grid.place_agent(a, pos)
            self.grid.place_agent(a, (3,3))

        # Add the package to a random empty grid cell
        for i in range(self.num_packages):
            b = PackageAgent(i+2000, "PKG", self) 
            self.schedule.add(b)

            # pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            # pos = pos_gen(self.grid.width, self.grid.height)
            # while (not self.grid.is_cell_empty(pos)):
            #     pos = pos_gen(self.grid.width, self.grid.height)
            # self.grid.place_agent(b, pos)
            self.grid.place_agent(b, (4,3))

        # Add the depots at chosen locations
        for i in range(self.num_depots):
            c = DepotAgent(i+3000, "DPT", self)
            self.schedule.add(c)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            # Add depot location to the global dictionary
            depots[f"{i+3000}"] = pos
            self.grid.place_agent(c, pos)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
