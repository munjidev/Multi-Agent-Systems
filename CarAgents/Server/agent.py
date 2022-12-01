from mesa import Agent
# from graph import a_star_search
from bfs3 import bfs_shortest_path


class Car_Agent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        # Obtain random destination position from the list within the model
        # self.destination = self.random.choice(list(self.model.destinations.values()))
        self.destination = None
        self.path = []
        self.at_destination = False
        

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        print(f"> Agent {self.unique_id} has destination: {self.destination}")
        print(f"> Agent {self.unique_id} has path: {self.path[0:3]}...{self.path[-4:-1]}")
        print(f"> Agent {self.unique_id} at {self.pos} has next move: {self.path[1]}")

        # Get neighbors of current cell
        neighbors = self.model.coord_graph[str(self.pos)]
        
        # Check if goal position has been reached
        if self.pos != self.destination:
            if self.check_pos_contents(self.path[1]) == "Go":
                # If the forst cell of the BFS list is evaluated as a valid move, move to that cell
                print(f"> Agent {self.unique_id} is moving to: {self.path[1]}")
                self.model.grid.move_agent(self, self.path[1])
                if self.pos == self.destination:
                    self.at_destination = True
                    self.model.schedule.remove(self)
                # Remove the first cell from the BFS list
                self.path.pop(0)
            else:
                # Else, Iterate Neighbors and pick first that is valid, also recalculate route from current position
                for neighbor in neighbors:
                    if self.check_pos_contents(neighbor) == "Go": 
                        print(f"> Agent {self.unique_id} is moving to: {neighbor}")
                        self.model.grid.move_agent(self, neighbor)
                        if self.pos == self.destination:
                            self.at_destination = True
                            self.model.schedule.remove(self)
                        else:
                            self.path = self.calculate_route()
                        print(f">>> Agent {self.unique_id} is recalculating route")
                        break
                    elif self.check_pos_contents(neighbor) == "Switch":
                        # Evaluate next neighbor
                        continue
                    elif self.check_pos_contents(neighbor) == "Wait":
                        # If it has to wait, break from loop and evaluate original BFS cell in the next iteration
                        break
        else:
            self.model.schedule.remove(self)

    def check_pos_contents(self, pos):
        cell_contents = self.model.grid.get_cell_list_contents(pos)[0]
        
        # Check if the desired cell has the same direction as the current cell in order to chage lanes
        if isinstance(cell_contents, Road_Agent) or isinstance(cell_contents, Destination_Agent):  
            if len(self.model.grid.get_cell_list_contents(pos)) < 2 or isinstance(cell_contents, Destination_Agent):
                return "Go"
            else:
                return "Switch"

        # Else check if the next cell is a traffic light on green or red
        elif isinstance(cell_contents, Traffic_Light_Agent): 
            if cell_contents.state == True and len(self.model.grid.get_cell_list_contents(pos)) < 2:
                return "Go"
            elif cell_contents.state == False:
                print(">>> Waiting")
                return "Wait"
        else:
            return "Wait"


    def calculate_route(self):
        # Generate path by calling the A* search algorithm with the current position and a randomly chosen destination
        print(f"> Agent {self.unique_id} current position: {self.pos}")
        print(f"> Agent {self.unique_id} current destination: {self.destination}")

        # path_dict = breadth_first_search(self.model.coord_graph, self.pos, self.destination)
            
        path_dict = bfs_shortest_path(self.model.coord_graph, self.pos, self.destination)

        # Position list in the order in which A* generated the path dictionary
        path_list = []

        for coord in path_dict:
            if coord not in path_list:
                path_list.append(coord)

        print(f"> Path list: {path_list}")

        return path_list
        
    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.move()

class Traffic_Light_Agent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        # if self.model.schedule.steps % self.timeToChange == 0:
        #     self.state = not self.state
        pass

class Destination_Agent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle_Agent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road_Agent(Agent):
    """
    Road agent. Just to add roads to the grid.
    """
    def __init__(self, unique_id, model, direction="Left"):
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass

class Car_Spawner_Agent(Agent):
    """
    Car spawner agent. Spawns cars regularly in a given position.
    """
    def __init__(self, unique_id, model, direction="Left"):
        super().__init__(unique_id, model)
        self.direction = direction
        self.spawned = 0
    
    def spawn_car(self):
        if len(self.model.grid.get_cell_list_contents(self.pos)) < 2:
            self.spawned += 1
            car = Car_Agent(f"c_{self.spawned+1000}", self.model)
            self.model.grid.place_agent(car, self.pos)
            self.model.schedule.add(car)
            print(f"+ Agent: {car.unique_id} spawned at {self.pos}!")
            return car
        

