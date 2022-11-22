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

depots = {}
# Global dictionary with all existing depot locations

class RandomAgent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of four directions (WASD)
    """
    has_package = False

    def __init__(self, unique_id, type_str, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.direction = 4
        self.type_str = type_str

    def move(self):
        """
        Moves the agent according to its current state.
        """
        # Check if robot is carrying a package
        print(f"Click, {self.has_package}")
        if(self.has_package):
            self.seek_depot()
        else:
            self.seek_package()
        
    def seek_package(self):
        """
        Moves the agent to a package if in neighboring cells.
        If no package is found, the agent moves randomly.
        """
        print(f"Agent {self.unique_id} is seeking a package at {self.pos}")
        # print(f"Agent {self.unique_id} is seeking package")
        # Get the neighbors of the agent
        neighbors = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right).
            include_center=True)

        content = []
        # Check if there is a package in the neighbors
        for pos in neighbors:
            content = self.model.grid.get_cell_list_contents(pos)
            # If there is a package, move to it
            if(len(content) > 0):
                print(f"Agent {self.unique_id} has found a {content[0].type_str} at {pos}")
                if(content[0].type_str == "PKG"):
                    print(f"Agent {self.unique_id} has picked up package {content[0].unique_id}")
                    self.model.grid.move_agent(self, pos)
                    self.has_package = True
                    return
        
        # # If no package is found, move randomly using the possible steps scope
        self.random_move(neighbors)

    def seek_depot(self):
        """
        Check all depot locations and approach the closest one.
        """
        print(f"Agent {self.unique_id} is seeking a depot to drop a package")
        # Read the global dictionary with all depot pointers and obtain their positions
        agent_position = self.pos
        closest_depot = None
        for val in depots.values():
            print(f"Depot {val.unique_id} found, available: {val.available()}")
            if(val.available()):
                if(closest_depot == None):
                    closest_depot = val
                else:
                    if(self.distance(agent_position, val.pos) < self.distance(agent_position, closest_depot.pos)):
                        closest_depot = val
                    # If distance is the same, choose depot with fewer packages
                    elif(self.distance(agent_position, val.pos) == self.distance(agent_position, closest_depot.pos)):
                        if(val.packages < closest_depot.packages):
                            closest_depot = val
                        # If number of packages is the same, choose randomly
                        elif(val.packages == closest_depot.packages):
                            if(self.random.random() > 0.5):
                                closest_depot = val
            else:
                print(f"Depot {val.unique_id} is full")
            

        # If the agent is not in the same cell as the depot, approach it by one step
        if(closest_depot.pos != agent_position):
            self.move_towards(closest_depot.pos)

        # If the agent is in the same cell as the depot, drop the package
        if(closest_depot.pos == agent_position):
            self.has_package = False
            closest_depot.load_package()
            return
        

    def distance(self, pos1, pos2):
        """
        Calculates the distance between two points.
        """
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def move_towards(self, target_position):
        """
        Moves the agent towards a target position.
        """
        agent_x = self.pos[0]
        agent_y = self.pos[1]
        target_x = int(target_position[0])
        target_y = int(target_position[1])
        possible_steps = []
        if(agent_x < target_x):
            possible_steps.append((agent_x + 1, agent_y))
        elif(agent_x > target_x):
            possible_steps.append((agent_x - 1, agent_y))

        if(agent_y < target_y):
            possible_steps.append((agent_x, agent_y + 1))
        elif(agent_y > target_y):
            possible_steps.append((agent_x, agent_y - 1))

        content = []
        # Ensure that each step is to an empty cell
        for pos in possible_steps:
            content = self.model.grid.get_cell_list_contents(pos)
            if(len(content) != 0):
                print(f"{pos} is not empty, and contains a {content[0].type_str}")
                if(content[0].type_str != "DPT"):
                    possible_steps.remove(pos)
            else:
                print(f"{pos} is in fact empty")

        if len(possible_steps) > 0:
            # Choose a random direction
            new_position = self.random.choice(possible_steps)

            # Move the agent
            print(f"Agent {self.unique_id} moved to {new_position}")
            self.model.grid.move_agent(self, new_position)
            return
        else:
            print(f"Agent {self.unique_id} is stuck. (There is a {content[0].type_str} in the way)")
            return

    def random_move(self, neighbors):
        """
        Move the agent to a random position.
        """
        print("(While moving randomly...)")
        # Get the neighbors of the agent
        content = []
        possible_steps = []
        # Navigate to empty cells only
        print(f"Neighbors: {neighbors}")
        for pos in neighbors:
            content = self.model.grid.get_cell_list_contents(pos)
            print(len(content))
            if(len(content) != 0):
                print(f"{pos} is not empty, and contains a {content[0].type_str}")
            else:
                print(f"{pos} is in fact empty")
                possible_steps.append(pos)
        print(f"Possible steps: {possible_steps}")

        # Ensure that the agent can move
        if len(possible_steps) > 0:
            # Choose a random direction
            new_position = self.random.choice(possible_steps)
        else:
            new_position = self.pos
            print(f"Agent {self.unique_id} is stuck! :(")

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
    def __init__(self, unique_id, type_str, model):
        super().__init__(unique_id, model)
        self.type_str = type_str

    def step(self):
        pass   

class PackageAgent(Agent):
    """
    Package agent. Package can be picked up by agent and placed in a port.
    """
    def __init__(self, unique_id, type_str, model):
        super().__init__(unique_id, model)
        self.type_str = type_str     

    def step(self):
        pass

class DepotAgent(Agent):
    """
    Depot agent. Depot can receive up to X packages, stacked on top of each other.
    """
    def __init__(self, unique_id, type_str, model):
        super().__init__(unique_id, model)
        self.type_str = type_str
        self.packages = 0

    def available(self):
        return self.packages < 5

    def get_packages(self):
        return self.packages

    def step(self):
        pass

    def load_package(self):
        """
        Load package into depot.
        """
        self.packages += 1
        print(f"Depot {self.unique_id} was loaded with package #{self.packages}")
        if self.packages == 5:
            print(f"Depot {self.unique_id} is now full!")

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
            # self.grid.place_agent(a, (3,3))

        # Add the package to a random empty grid cell
        for i in range(self.num_packages):
            b = PackageAgent(i+2000, "PKG", self) 
            self.schedule.add(b)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(b, pos)
            # self.grid.place_agent(b, (4,3))

        # Add the depots at chosen locations
        for i in range(self.num_depots):
            c = DepotAgent(i+3000, "DPT", self)
            self.schedule.add(c)

            pos_gen = lambda w, h: (self.random.randrange(w), 1)
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            # Add pointer to depot into global dictionary
            depots[i+3000] = c
            self.grid.place_agent(c, pos)

    def step(self):
        '''Advance the model by one step.'''
        # Check if all boxes are in a depot and stop the simulation if so
        if all([depots[i].get_packages() == 5 for i in depots]):
            self.running = False
            print("All boxes are in a depot, simulation is over!")
        self.schedule.step()
