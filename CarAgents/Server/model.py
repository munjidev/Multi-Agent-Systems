from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
# from graph import WeightedGraph

cars = {}
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

        self.coord_graph = {}

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
                        # self.destinations.append((c, self.height - r - 1))
                    elif col == "z":
                        agent = Car_Spawner_Agent(f"cs_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

        # Generate weighted graph for A* pathfinding
        # self.graph = WeightedGraph(self.generate_graph())
        # self.print_graph()
        self.generate_graph()

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
        # self.graph = {}    # Generate graph dictionary
        for agents, x, y in self.grid.coord_iter():   # Iterate through all agents
            for agent in agents:
                if isinstance(agent, Road_Agent) or isinstance(agent, Traffic_Light_Agent) or isinstance(agent, Car_Spawner_Agent) or isinstance(agent, Destination_Agent):
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

                    elif isinstance(agent, Car_Spawner_Agent):
                        neighbors = []
                        if n_up != None:
                            if isinstance(n_up, Road_Agent):
                                neighbors.append(n_up)
                        if n_right != None:
                            if isinstance(n_right, Road_Agent):
                                neighbors.append(n_right)
                        if n_down != None: 
                            if isinstance(n_down, Road_Agent):
                                neighbors.append(n_down)
                        if n_left != None:
                            if isinstance(n_left, Road_Agent):
                                neighbors.append(n_left)

                    new_neighbors = []
                    # Filter out neighbors that are not roads or destinations, or if they are roads pointing towards the current road
                    for neighbor in neighbors:
                        if neighbor != None:
                            
                            # print(neighbor.unique_id)
                            if isinstance(neighbor, Road_Agent):
                                if isinstance(agent, Car_Spawner_Agent):
                                    if neighbor == n_up or neighbor == n_right or neighbor == n_down or neighbor == n_left:
                                        new_neighbors.append(neighbor.pos)
                                # If it is any of the given 4 adjacent cells, and it doesn't point at me, include it.
                                elif (neighbor == n_up and (neighbor.direction == "Left" or neighbor.direction == "Up" or neighbor.direction == "Right")) or (neighbor == n_right and (neighbor.direction == "Up" or neighbor.direction == "Right" or neighbor.direction == "Down")) or (neighbor == n_down and (neighbor.direction == "Right" or neighbor.direction == "Down" or neighbor.direction == "Left")) or (neighbor == n_left and (neighbor.direction == "Down" or neighbor.direction == "Left" or neighbor.direction == "Up")):
                                    # print(f"    I can go to {neighbor.unique_id}!")
                                    new_neighbors.append(neighbor.pos)
                                # If any of the 4 diagonals points outwards, include it
                                elif (neighbor == n_ur and (neighbor.direction == "Up" or neighbor.direction == "Right")) or (neighbor == n_dr and (neighbor.direction == "Right" or neighbor.direction == "Down")) or (neighbor == n_dl and (neighbor.direction == "Down" or neighbor.direction == "Left")) or (neighbor == n_ul and (neighbor.direction == "Left" or neighbor.direction == "Up")):
                                    # print(f"    I can go to {neighbor.unique_id}!")     
                                    new_neighbors.append(neighbor.pos)

                            elif isinstance(neighbor, Traffic_Light_Agent) or isinstance(neighbor, Destination_Agent):
                                if not isinstance(agent, Traffic_Light_Agent) and not isinstance(agent, Destination_Agent):
                                    if agent.direction == "Up" or agent.direction == "Down":
                                        if not (neighbor == n_right or neighbor == n_left):
                                            # print(f"    I can go to {neighbor.unique_id}")
                                            new_neighbors.append(neighbor.pos)
                                    elif agent.direction == "Left" or agent.direction == "Right":
                                        if not(neighbor == n_up or neighbor == n_down):
                                            # print(f"    I can go to {neighbor.unique_id}")
                                            new_neighbors.append(neighbor.pos)
                                    else:
                                        # print(f"    I can go to {neighbor.unique_id}")
                                        new_neighbors.append(neighbor.pos)
                            # else:
                            #     print(f"    I can't go to a {neighbor.unique_id}")
                    # Add the current agent to the dictionary with its id as the key and its neighbors as the value        
                    self.coord_graph[str(agent.pos)] = new_neighbors

        print("> Finished generating graph.")
        # self.print_graph()
        # return self.coord_graph

    def print_graph(self):
        for key, value in self.coord_graph.items():
            neighbors = ""
            for neighbor in value:
                if neighbor != None:
                    neighbors += f"{neighbor} "
            print(f"+ Cell: {key} -> Neighbors: {neighbors}")

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        # Get total number of cars spawned and total number of arrived cars
        total_cars_spawned = 0
        total_arrivals = 0
        for spawner in spawners.values():
            total_cars_spawned += spawner.spawned
        for destination in destinations.values():
            total_arrivals += destination.arrivals
        print(f"Cars spawned: {total_cars_spawned}")
        print(f"Total arrivals: {total_arrivals}")

        for agents, x, y in self.grid.coord_iter():
            for agent in agents:
                if self.schedule.steps % 2 == 0: # and len(cars) < self.num_agents:
                    if isinstance(agent, Car_Spawner_Agent):
                        car = agent.spawn_car()
                        if car != None:
                            car.destination = self.random.choice(list(destinations.values()))
                            car.path = car.calculate_route()
                            cars[car.unique_id] = car
                        else:
                            print(f"Spawner {agent.unique_id} is jammed.")
        if self.schedule.steps % 10 == 0:
            for agents, x, y in self.grid.coord_iter():
                for agent in agents:
                    if isinstance(agent, Traffic_Light_Agent):
                        agent.state = not agent.state