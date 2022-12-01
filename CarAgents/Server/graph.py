# Sample code from https://www.redblobgames.com/pathfinding/a-star/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

# some of these types are deprecated: https://www.python.org/dev/peps/pep-0585/
from typing import Tuple, TypeVar
import heapq

T = TypeVar('T')
Location = TypeVar('Location')
GridLocation = Tuple[int, int]

class WeightedGraph:
    def __init__(self, dict):
        self.weighted_graph = {}

        # Build dictionary
        print(dict)
        for key in dict:
            self.add_node((key, dict[key]), 1)


    def add_node(self, node, weight):
        self.weighted_graph[node[0]] = [node[1], weight]
        # print(self.weighted_graph[node[0]])
    

    def neighbors(self, pos):
        neighbor_list = self.weighted_graph[f"({pos[0]}, {pos[1]})"][0]
        # print(f"> NEIGHBOR LIST: {neighbor_list}")
        return neighbor_list
    

    def cost(self, pos):
        cost = self.weighted_graph[f"({pos[0]}, {pos[1]})"][1]
        # print(f"> COST: {cost}")
        return cost


class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, T]] = []

    # Return whether the queue is empty
    def empty(self) -> bool:
        return not self.elements
    
    # Add an item to the queue depending on its priority
    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))
    
    # Remove and return the item with the highest priority
    def get(self) -> T:
        return heapq.heappop(self.elements)[1]


def heuristic(a: GridLocation, b: GridLocation) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def a_star_search(graph: WeightedGraph, start: Location, goal: Location):
    print(f"> A_STAR GOAL: {goal}")
    # Initialize priority queue with start node
    frontier = PriorityQueue()
    # Add start position without cost
    frontier.put(start, 0)

    came_from: dict[Location] = {}
    cost_so_far: dict[Location, float] = {}

    # Define start location as None and cost as 0 for initial cost
    came_from[start] = None
    cost_so_far[start] = 0
    
    # While the queue contains elements
    while not frontier.empty():
        # Obtain queue item to evaluate
        current: Location = frontier.get()
        
        if current == goal:
            print(">>> BROKE OFF SEARCH !!! ")
            break
        
        for next in graph.neighbors(current):
            print(f"> Next of {current}: {next}")
            new_cost = cost_so_far[current] + graph.cost(current)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                # Recalculate cost, priority, and add to priority queue
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                # Update origin
                came_from[next] = current
                
    return came_from, cost_so_far