class Graph:
    def __init__(self, dict):
        self.weighted_graph = {}

        # Build dictionary
        for key, val in dict:
            self.add_node((key, val), 1)

    def add_node(self, node, weight):
        self.weighted_graph[node[0]] = [node[1], weight]
    
    def neighbors(self, pos):
        return self.weighted_graph[pos][1]

class WeightedGraph(Graph):
    def cost(self, from_id: Location, to_id: Location) -> float: pass

    
