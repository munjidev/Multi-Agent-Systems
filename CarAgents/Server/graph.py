# Sample code from https://www.redblobgames.com/pathfinding/a-star/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

from __future__ import annotations
# some of these types are deprecated: https://www.python.org/dev/peps/pep-0585/
from typing import Protocol, Tuple, TypeVar, Optional
import heapq

T = TypeVar('T')
Location = TypeVar('Location')
GridLocation = Tuple[int, int]

class Graph(Protocol):
    def neighbors(self, id: Location) -> list[Location]: pass


class WeightedGraph(Graph):
    def cost(self, from_id: Location, to_id: Location) -> float: pass


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
    # Initialize priority queue with start node
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Location, Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                # Recalculate cost, priority, and add to priority queue
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                # Update origin
                came_from[next] = current
    
    return came_from, cost_so_far