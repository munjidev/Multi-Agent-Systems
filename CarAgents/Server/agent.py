from mesa import Agent
# from graph import a_star_search
from bfs import breadth_first_search


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
        

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        # self.path, self.cost = self.calculate_route()
        print(f"> Agent: {self.unique_id} -> Destination: {self.destination}")
        print(f"> Path: {self.path[0:5]}...{self.path[-5:-1]}")
        next_move = self.path[0]
        self.path = self.path[1:]
        print(f"> Next move: {next_move}")

        neighbors = self.model.coord_graph[str(self.pos)]
        
        # Cehck wether the goal position has not been reached
        if self.pos != self.destination:
            # Iterate possible moves list and check wether the agent is blocked. Else if no viable path can be found, the agent is stuck, and should remain in its current position.
            if self.check_pos_contents(next_move) == "Go":
                self.model.grid.move_agent(self, next_move)
            else:
                for neighbor in neighbors:
                    if self.check_pos_contents(neighbor) == "Go": 
                        self.model.grid.move_agent(self, neighbor)
                        self.path = self.calculate_route()
                        break
                    elif self.check_pos_contents(neighbor) == "Switch":
                        continue
                    else:
                        self.path = self.calculate_route()
                        break
        else:
            # Remove self from grid
            self.model.grid.remove_agent(self)

    def check_pos_contents(self, pos):
        """
        Checks the contents of the cell the agent is trying to move to.
        Return False if the agent is being blocked by another agent, or if the next cell contains a red light.
        """
        # print("> Checking position contents.")
        cell_contents = self.model.grid.get_cell_list_contents(pos)[0]
        
        # Check if the desired cell has the same direction as the current cell in order to chage lanes
        if isinstance(cell_contents, Road_Agent) or isinstance(cell_contents, Destination_Agent):  
            if len(self.model.grid.get_cell_list_contents(pos)) < 2:
                # print(f"> Agent: {self.unique_id} is moving to {pos}!")
                return "Go"
            else:
                # print(f"> Agent: {self.unique_id} is switching lanes to {pos}!")
                return "Switch"
        # Else check if the next cell is a traffic light on green or red
        elif isinstance(cell_contents, Traffic_Light_Agent): 
            if cell_contents.state == True:
                # print(f"> Agent: {self.unique_id} is moving to {pos}!")
                return "Go"
            elif cell_contents.state == False:
                # print(f"> Agent: {self.unique_id} is waiting at {pos}!")
                return "Wait"
        else:
            # print(f"> Agent: {self.unique_id} is waiting at {pos}!")
            return "Wait"

    def calculate_route(self):
        # Generate path by calling the A* search algorithm with the current position and a randomly chosen destination
        print(f"> My current position: {self.pos}")
        print(f"> My current destination: {self.destination}")
        # path_dict, total_cost = a_star_search(self.model.graph, self.pos, self.destination)
        path_dict = breadth_first_search(self.model.coord_graph, self.pos, self.destination)

        # Position list in the order in which A* generated the path dictionary
        path_list = []

        for coord in path_dict:
            if coord not in path_list:
                path_list.append(coord) 
        
        # return path_list, total_cost
        return path_list
        
    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.move()
        # pass

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
        

