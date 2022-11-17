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
        if(self.hasPackage):
            self.seekDepot()
        else:
            self.seekPackage()
        
    def seekPackage(self):
        """
        Moves the agent to a package if in neighboring cells.
        If no package is found, the agent moves randomly.
        """
        print(f"Agent {self.unique_id} is seeking package")
        # Get the neighbors of the agent
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right).
            include_center=True)

        # Check for packages in surrounding 4 cells
        availableSpaces = []
        for pos in possible_steps:
            if(len(self.model.grid.get_cell_list_contents(pos)) > 0 ):
                if (self.model.grid.get_cell_list_contents(pos)[0].typeStr == "PKG"):
                    availableSpaces.append(True)
                else:
                    availableSpaces.append(False)
            elif(self.model.grid.is_cell_empty(pos)):
                availableSpaces.append(True)
            else:
                availableSpaces.append(False)
        next_moves = [p for p,f in zip(possible_steps, availableSpaces) if f == True]

        # Prioritize packages when choosing where to move
        packages = [p for p in next_moves if (len(self.model.grid.get_cell_list_contents(p))> 0) and (self.model.grid.get_cell_list_contents(p)[0].typeStr == "PKG")]

        if(len(packages) > 0):
            next_moves = packages

        # If there are no packages in the surrounding cells, move randomly
        if(len(next_moves) > 0):
            next_move = self.random.choice(next_moves)
            self.model.grid.move_agent(self, next_move)

        # Pick up package if in same cell
        if(len(self.model.grid.get_cell_list_contents(self.pos)) > 0):
            print("Larger than 0")
            for obj in self.model.grid.get_cell_list_contents(self.pos):
                print(obj.typeStr)
                if(obj.typeStr == "PKG"):
                    self.hasPackage = True
                    self.model.grid.remove_agent(obj)
                    print(f"Agent {self.unique_id} picked up package {obj.unique_id}")
                    break

    def seekDepot(self):
        """
        Check all depot locations and move to the closest one.
        If there are two depots with the same distance, choose depot
        with fewer packages.
        If there are two depots with the same distance and same number
        of packages, choose randomly.
        """
        print(f"Agent {self.unique_id} is seeking depot")
        # Get depot locations on grid
        depots = [p for p in self.model.grid.coord_iter() if (len(self.model.grid.get_cell_list_contents(p[1]))> 0) and (self.model.grid.get_cell_list_contents(p[1])[0].typeStr == "DPT")]

        # Check distance relative to each depot
        distances = []
        for d in depots:
            distances.append(math.sqrt((d[1][0] - self.pos[0])**2 + (d[1][1] - self.pos[1])**2))
        
        # Get depot with minimum distance
        minDist = min(distances)
        minDepots = [d for d in depots if math.sqrt((d[1][0] - self.pos[0])**2 + (d[1][1] - self.pos[1])**2) == minDist]

        # If there are two depots with the same distance, choose depot with fewer packages
        if(len(minDepots) > 1):
            minPackages = minDepots[0][0].numPackages
            minDepots = [d for d in minDepots if d[0].numPackages == minPackages]

        # If there are two depots with the same distance and same number of packages, choose randomly
        if(len(minDepots) > 1):
            minDepots = self.random.choice(minDepots)

        # Move to closest depot
        self.model.grid.move_agent(self, minDepots[1])

        # Drop package if in same cell
        if(len(self.model.grid.get_cell_list_contents(self.pos)) > 0):
            if (self.model.grid.get_cell_list_contents(self.pos)[0].typeStr == "DPT"):
                self.model.grid.get_cell_list_contents(self.pos)[0].drop(self)


    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        print("Click")
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

        # Add the depots at chosen locations
        for i in range(self.num_depots):
            c = DepotAgent(i+3000, "DPT", self)
            self.schedule.add(c)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(c, pos)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
