from Vertex import *

"""
Clase Graph que representa un grafo a utilizarse para
aplicar Dijkstra sobre la informacion de adyacencias
de los nodos del grafo de la red.
Autor: Roy Rojas.
"""

class Graph:
    def __init__(self):
        self.vertices = {}
        self.vertices_count = 0

    def add_vertex(self, node):
        self.vertices_count = self.vertices_count + 1
        new_vertex = Vertex(node)
        self.vertices[node] = new_vertex
        return new_vertex

    def get_vertex(self, node):
        if node in self.vertices:
            return self.vertices[node]
        else:
            return None

    def add_edge(self, src, dest, cost=0):
        if src not in self.vertices:
            self.add_vertex(src)
        if dest not in self.vertices:
            self.add_vertex(dest)

        self.vertices[src].add_neighbour(self.vertices[dest], cost)
    
    def get_vertices(self):
        return list(self.vertices.values())