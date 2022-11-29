class WeightedGraph:
    def __init__(self, dict):
        # self.model = model
        self.weighted_nodes = []
        for key, val in dict:
            self.add_node((key, val), 1)

    def add_node(self, node, weight):
        self.weighted_nodes.append((node, weight))
        