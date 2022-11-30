from mesa import Agent
from graph import a_star_search

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
        self.destination = self.random.choice(self.model.destinations)
        print(f"+ Agent: {self.unique_id} -> Destination: {self.destination}")
        

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        path_list, total_cost = self.calculate_route()
        # print(f"> PATH LIST: {path_list[0:10]}...")
        next_move = path_list[0]
        possible_moves = self.model.node_dict[str(self.pos)]
        # print(f"> POSSIBLE MOVES: {possible_moves[0:10]}...")

        all_moves = []
        all_moves.append(next_move)
        for move in possible_moves:
            # Discard path_list[0] already in possible_moves
            if move not in all_moves:
                all_moves.append(move)
        
        # Cehck wether the goal position has not been reached
        if self.pos != path_list[-1]:
            # Iterate possible moves list and check wether the agent is blocked. Else if no viable path can be found, the agent is stuck, and should remain in its current position.
            for pos in possible_moves:
                if self.check_pos_contents(pos) == "Wait":
                    break
                elif self.check_pos_contents(pos) == "Go":
                    # Move agent to the position
                    self.model.grid.move_agent(self, pos)
                    # print(f"> Agent: {self.unique_id} is moving to {pos}!")
                elif self.check_pos_contents(pos) == "Switch":
                    pass
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
        if isinstance(cell_contents, Road_Agent):
            if (cell_contents.direction == self.model.grid.get_cell_list_contents(pos)[0].direction) and len(self.model.grid.get_cell_list_contents(pos)) < 2:
                # print(f"> Agent: {self.unique_id} is moving to {pos}!")
                return "Go"
        # Else check if the next cell is a traffic light on green or red
        elif isinstance(cell_contents, Traffic_Light_Agent): 
            if cell_contents.state == True:
                # print(f"> Agent: {self.unique_id} is moving to {pos}!")
                return "Go"
            elif cell_contents.state == False:
                # print(f"> Agent: {self.unique_id} is waiting at {pos}!")
                return "Wait"
        else: 
            # print(f"> Agent: {self.unique_id} is switching lanes to {pos}!")
            return "Switch"

    def calculate_route(self):
        # Generate path by calling the A* search algorithm with the current position and a randomly chosen destination
        path_dict, total_cost = a_star_search(self.model.graph, self.pos, self.destination)

        # Position list in the order in which A* generated the path dictionary
        path_list = []

        for coord in path_dict:
            if coord not in path_list:
                path_list.append(coord) 
        
        return path_list, total_cost
        
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
            print(f"> Agent: {car.unique_id} spawned at {self.pos}!")
        return car

