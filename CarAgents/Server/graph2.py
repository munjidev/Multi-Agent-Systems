class Node:
    def __init__(self, uniqueid, pos):
        self.uniqueid = uniqueid
        self.pos = pos
        self.neighbors = []

class Graph:
    def __init__(self, model):
        self.model = model
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)