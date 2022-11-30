from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
from graph2 import *

roads = {}
cars = {}
traffic_lights = {}
destinations = {}
spawners = {}
buildings = {}

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, map_path):

        dataDictionary = json.load(open("mapDictionary.txt"))
        self.graph = Graph(self)

        with open(f"../TrafficVisualization/{map_path}") as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0]) - 1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height,torus = False) 
            self.schedule = RandomActivation(self)

            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road_Agent(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col in ["S", "s"]:
                        agent = Traffic_Light_Agent(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        # Additionally, add a road agent with same direction as road before traffic light

                    elif col == "#":
                        agent = Building_Agent(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col == "D":
                        agent = Destination_Agent(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col == "z":
                        agent = Car_Spawner_Agent(f"cs_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

        
        graph = self.generate_graph()
        # self.print_graph()
        self.num_agents = 5
        print(self.num_agents)
        # Add N cars to the grid at random positions on cells where a road agent is present
        for i in range(self.num_agents):
            c = Car_Agent(f"car_{i}", self)
            # self.schedule.add(agent)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.width, self.height)

            # Add car only if there is a road agent at the position and no other cars.
            while not isinstance(self.grid.get_cell_list_contents([pos])[0], Road_Agent) or len(self.grid.get_cell_list_contents([pos])) > 1:
                pos = pos_gen(self.width, self.height)
            cars[c.unique_id] = c
            self.grid.place_agent(c, pos)

        # Loop through all agents and add them to their respective dictionary
        for agents, x, y in self.grid.coord_iter():
            for agent in agents:
                if isinstance(agent, Road_Agent):
                    roads[agent.unique_id] = agent
                elif isinstance(agent, Building_Agent):
                    buildings[agent.unique_id] = agent
                elif isinstance(agent, Car_Agent):
                    cars[agent.unique_id] = agent
                elif isinstance(agent, Traffic_Light_Agent):
                    traffic_lights[agent.unique_id] = agent
                elif isinstance(agent, Destination_Agent):
                    destinations[agent.unique_id] = agent
                elif isinstance(agent, Car_Spawner_Agent):
                    spawners[agent.unique_id] = agent

        self.running = True

    def generate_graph(self):
        # Generate a graph of the streets
        self.graph = {}    # Generate graph dictionary
        for agents, x, y in self.grid.coord_iter():   # Iterate through all agents
            for agent in agents:
                if isinstance(agent, Road_Agent) or isinstance(agent, Traffic_Light_Agent):
                    # Check neighbors depending on the direction of the road

                    # Get grid width and height values
                    gridWidth = self.grid.width - 1
                    gridHeight = self.grid.height - 1

                    n_up = None
                    n_ul = None
                    n_ur = None
                    n_left = None
                    n_right = None
                    n_down = None
                    n_dr = None
                    n_dl = None

                    # Check if the agents neighbors are not out of bounds

                    if (not x+1 > gridWidth) and (not y+1 > gridHeight):
                        n_ur = self.grid.get_cell_list_contents((x+1, y+1))[0]
                    if (not x-1 < 0) and (not y+1 > gridHeight):
                        n_ul = self.grid.get_cell_list_contents((x-1, y+1))[0]
                    if (not x+1 > gridWidth) and (not y-1 < 0):
                        n_dr = self.grid.get_cell_list_contents((x+1, y-1))[0]
                    if (not x-1 < 0) and (not y-1 < 0):
                        n_dl = self.grid.get_cell_list_contents((x-1, y-1))[0]
                    if not x+1 > gridWidth:
                        n_right = self.grid.get_cell_list_contents((x+1, y))[0]
                    if not x-1 < 0:
                        n_left = self.grid.get_cell_list_contents((x-1, y))[0]
                    if not y+1 > gridHeight:
                        n_up = self.grid.get_cell_list_contents((x, y+1))[0]
                    if not y-1 < 0:
                        n_down = self.grid.get_cell_list_contents((x, y-1))[0]

                    # Check if coordinate contains a road or a traffic light, and generate their neighbors

                    if isinstance(agent, Road_Agent):
                        # print(f"Road: {agent.unique_id} Direction: {agent.direction}")
                        if(agent.direction == "Up"):   
                            neighbors = [n_left, n_ul, n_up, n_ur, n_right]
                        elif(agent.direction == "Right"):
                            neighbors = [n_up, n_ur, n_right, n_dr, n_down]
                        elif(agent.direction == "Down"):
                            neighbors = [n_right, n_dr, n_down, n_dl, n_left]
                        elif(agent.direction == "Left"):
                            neighbors = [n_down, n_dl, n_left, n_ul, n_up]

                        

                    elif isinstance(agent, Traffic_Light_Agent):
                        #Check that relative neighbors are roads
                        if n_down != None:
                            if isinstance(n_down, Road_Agent):
                                if n_down.direction == "Up":
                                    # print("facing up")
                                    neighbors = [n_left, n_ul, n_up, n_ur, n_right]
                        if n_left != None:
                            if isinstance(n_left, Road_Agent): 
                                if n_left.direction == "Right":
                                    # print("facing right")
                                    neighbors = [n_up, n_ur, n_right, n_dr, n_down]
                        if n_up != None:
                            if isinstance(n_up, Road_Agent):
                                if n_up.direction == "Down":
                                    # print("facing down")
                                    neighbors = [n_right, n_dr, n_down, n_dl, n_left]
                        if n_right != None:
                            if isinstance(n_right, Road_Agent):
                                if n_right.direction == "Left":
                                    # print("facing left")
                                    neighbors = [n_down, n_dl, n_left, n_ul, n_up]
                    
                    new_neighbors = []
                    # Filter out neighbors that are not roads, or if they are roads pointing towards the current road
                    for neighbor in neighbors:
                        if neighbor != None:
                            
                            # print(neighbor.unique_id)
                            if isinstance(neighbor, Road_Agent):
                                # If it is any of the given 4 adjacent cells, and it doesn't point at me, include it.
                                if (neighbor == n_up and (neighbor.direction == "Left" or neighbor.direction == "Up" or neighbor.direction == "Right")) or (neighbor == n_right and (neighbor.direction == "Up" or neighbor.direction == "Right" or neighbor.direction == "Down")) or (neighbor == n_down and (neighbor.direction == "Right" or neighbor.direction == "Down" or neighbor.direction == "Left")) or (neighbor == n_left and (neighbor.direction == "Down" or neighbor.direction == "Left" or neighbor.direction == "Up")):
                                    # print(f"    I can go to {neighbor.unique_id}!")
                                    new_neighbors.append(neighbor)
                                # If any of the 4 diagonals points outwards, include it
                                elif(neighbor == n_ur and (neighbor.direction == "Up" or neighbor.direction == "Right")) or (neighbor == n_dr and (neighbor.direction == "Right" or neighbor.direction == "Down")) or (neighbor == n_dl and (neighbor.direction == "Down" or neighbor.direction == "Left")) or (neighbor == n_ul and (neighbor.direction == "Left" or neighbor.direction == "Up")):
                                    # print(f"    I can go to {neighbor.unique_id}!")     
                                    new_neighbors.append(neighbor)

                            elif isinstance(neighbor, Traffic_Light_Agent):
                                if not isinstance(agent, Traffic_Light_Agent):
                                    if agent.direction == "Up" or agent.direction == "Down":
                                        if not (neighbor == n_right or neighbor == n_left):
                                            # print(f"    I can go to {neighbor.unique_id}")
                                            new_neighbors.append(neighbor)
                                    elif agent.direction == "Left" or agent.direction == "Right":
                                        if not(neighbor == n_up or neighbor == n_down):
                                            # print(f"    I can go to {neighbor.unique_id}")
                                            new_neighbors.append(neighbor)
                                    else:
                                        # print(f"    I can go to {neighbor.unique_id}")
                                        new_neighbors.append(neighbor)
                            # else:
                            #     print(f"    I can't go to a {neighbor.unique_id}")
                    # Add the current agent to the dictionary with its id as the key and its neighbors as the value
                    # self.graph[f"{agent.unique_id}{agent.pos}"] = new_neighbors
                    
                    self.graph[f"{agent.pos}"] = new_neighbors

        print("Finished generating graph.")
        return self.graph   

    def print_graph(self):
        for key, value in self.graph.items():
            neighbors = ""
            for neighbor in value:
                if neighbor != None:
                    neighbors += f"{neighbor.unique_id}{neighbor.pos}  |  "
            print(f"Node {key} -->  {neighbors}")

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        if self.schedule.steps % 10 == 0:
            for agents, x, y in self.grid.coord_iter():
                for agent in agents:
                    if isinstance(agent, Traffic_Light_Agent):
                        agent.state = not agent.state