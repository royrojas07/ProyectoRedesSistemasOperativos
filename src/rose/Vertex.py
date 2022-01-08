"""
Clase Vertex que representa un vertice de un
grafo. Utilizada para formar el grafo que representa
la red y en el cual se aplica Dijkstra.
Autor: Roy Rojas.
"""

class Vertex:
    def __init__(self, node):
        self.value = node
        self.neighbours = {}
    
    def add_neighbour(self, node, cost):
        self.neighbours[node] = cost
    
    def get_neighbours(self):
        return list(self.neighbours.keys())
    
    def get_cost(self, neighbour):
        return self.neighbours[neighbour]
    
    def get_value(self):
        return self.value
    
    def __str__(self):
        return "(%s)" % self.value