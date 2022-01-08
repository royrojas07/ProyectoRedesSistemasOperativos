import os 
import sys
import time
import queue
import threading
import struct
from threading import Thread, Semaphore
from Graph import *
from PQueue import PQueue

class Router: 
    def __init__(self):
            self.green_agent = 0
            self.spanning_tree = 0
            self.sandbox = 0
            self.adj_table = []
            self.node_id = 0
            self.neighbours = 0
            self.adjacencies_packet = 0
            self.routing_queue = queue.Queue()
            self.stat_queue = queue.Queue()
            self.dijkstra_queue = queue.Queue()
            self.send_queue = queue.Queue()
            self.semaphore = Semaphore(0)
            self.threads = [Thread( target=self.dijkstra, args=()),
                            Thread( target=self.adj_table_init, args=()),
                            Thread( target=self.packet_send, args=()),
                            Thread( target=self.adjacencies_send, args=()),
                            Thread( target=self.adj_send_stat, args=())]
    def __del__(self):
        for x in self.threads:
            x.join()

    """
    Efecto: Carga los datos de adyacencias hacia vecinos.
            Carga y guarda el paquete de adyacencias.
            Envia los IDs de los nodos vecinos a spanning_tree.
            Da inicio a ejecucion de los diferentes hilos.
    Requiere: que llegue un paquete con los datos de los vecinos a routing_queue.
    Modifica: (self.node_id).
              (self.neighbours).
              (self.adjacenciaes_packet).
    Retorna: No aplica.
    Autor: Pablo Cheng.
    """
    def thread_init(self):
        buffer = self.routing_queue.get(block=True)
        self.node_id, self.neighbours = self.node_info_get(buffer)
        self.adjacencies_packet = self.adjacencies_packet_create()
        self.spanning_tree.nb_table_init( list ( self.neighbours.keys() )  )
        for x in self.threads:
            x.start()

    """
    Efecto: revisa si una adyacencia es nueva o no.
    Requiere: (value) ID del nodo que envia adyacencias.
    Modifica: No aplica.
    Retorna: (True) si ya estan las adyacencias de ese nodo.
             (False) en caso contrario.
    Autor: Pablo Cheng.
    """
    def repeated_check(self, value):
        for i in range(len(self.adj_table)):
            if(self.adj_table[i][0] == value):
                return True
        return False

    """
    Efecto: Carga la tabla de adyacencias conforme los paquetes de adyacencias
            van llegando. Indica a Dijkstra cuando puede correr y desbloquea el
            envio de adyacencias.
    Requiere: No aplica.
    Modifica: (adj_table) tabla de adyacencias.
              (semaphore) semaforo para indicar envio de adyacencias.
              (dijkstra_queue) agrega a la cola de Dijkstra la fila hasta la
              cual puede procesar la tabla de adyacencias.
    Retorna: No aplica.
    Autor: Pablo Cheng.
    """
    def adj_table_init(self):
        while(1):

            buffer = self.routing_queue.get(block=True)
            nb_count = buffer[7]

            if not self.repeated_check(struct.unpack("!H", buffer[5:7])[0]) :
                for i in range(nb_count):
                    a =[] 
                    a.append(struct.unpack("!H", buffer[5:7])[0])
                    # a.append(struct.unpack("!H", buffer[8+(3 * i):8+(3 * i)])[0])
                    a.append( struct.unpack("!H", buffer[8+(3 * i):10+(3 * i)])[0] )
                    a.append(struct.pack("B", buffer[10 + (3 * i)] ) [0] )
                    self.adj_table.append(a)
                self.adjacencies_send_unlock()
                self.dijkstra_queue.put(len(self.adj_table))
                stat = self.get_adj_stat()
                
    
    """
    Efecto: Obtiene información de vecinos de un arreglo de bytes
            y lo convierte a un diccionario, tambien el ID del nodo.
    Requiere: (neighbors) Arreglo de bytes con información de vecinos.
    Modifica: No aplica.
    Retorna: (neighbours_dict) Diccionario, siendo las llaves los identificadores
             de los vecinos y los valores tuplas (peso, orden de llegada).
             (node_id) ID de nodo verde.
    Autor: Roy Rojas.
    """
    def node_info_get(self, neighbours):
        node_id = struct.unpack("H", neighbours[5:7])[0]
        neighbours_dict = {}
        it = 8
        node_count = struct.unpack("B", neighbours[7:it])[0]
        it += node_count*2
        for i in range(node_count):
            node = struct.unpack("H", neighbours[8+(3*i):10+(3*i)])[0]
            node_cost = struct.unpack("B", neighbours[10+(3*i):11+(3*i)])[0]
            neighbours_dict[node] = (node_cost, i)
        return node_id, neighbours_dict

    """
    Efecto: Aplica Dijkstra sobre el grafo que se genera a partir
            de la tabla de adyacencias.
    Requiere: No aplica.
    Modifica: Agrega un nuevo paquete a la cola table_send_queue.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def dijkstra(self):
        while( True ):
            rows = self.dijkstra_queue.get(block=True)

            # se carga el grafo
            graph = Graph()
            self.graph_load(graph, rows)

            # se aplica dijkstra
            lowest_path = self.dijkstra_run(graph)
            
            # se carga la tabla de enrutamiento
            routing_table = self.routing_table_load(graph, lowest_path)

            # pasar la routing table a table_sender
            self.routing_table_send(routing_table)
    
    def packet_send(self):
        while True:
            packet = self.send_queue.get(block=True)
            self.green_agent.green_send_store(packet)
    
    def routing_queue_store(self, buffer):
        self.routing_queue.put(buffer)

    """
    Efecto: carga en graph las adyacencias almacenadas en adj_table y neighbours.
    Requiere: (graph) grafo a ser cargado.
              (rows) cantidad de filas a ser procesadas de adj_table.
    Modifica: (graph) grafo.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def graph_load(self, graph, rows):
        for n in self.neighbours:
            graph.add_edge(self.node_id, n, self.neighbours[n][0])
            # graph.add_edge(n, "root", self.neighbours[n][0])
        for i in range(rows):
            graph.add_edge(self.adj_table[i][0], self.adj_table[i][1],
                    self.adj_table[i][2])
    
    """i-1
    Efecto: corre Djkstra sobre el grafo graph.
    Requiere: (graph) grafo en el que se corre Dijkstra.
    Modifica: No aplica.
    Retorna: (node_path) diccionario con los caminos más cortos
             desde el nodo raíz a todos los otros nodos en graph
    Autor: Roy Rojas.
    """
    def dijkstra_run(self, graph):
        root_node = graph.get_vertex(self.node_id)
        node_path = {}
        node_path_weight = {}
        visited_nodes = []
        graph_nodes = PQueue()
        for node in graph.get_vertices():
            node_path[node] = []
            node_path_weight[node] = 10000
        node_path_weight[root_node] = 0
        graph_nodes.insert((0,root_node))

        while len(graph_nodes) > 0:
            actual_node = graph_nodes.pop()[1]
            if actual_node not in visited_nodes:
                actual_node_neighbours = actual_node.get_neighbours()
                visited_nodes.append(actual_node)

                for neigh in actual_node_neighbours:
                    graph_nodes.insert((actual_node.get_cost(neigh),neigh))
                    distance = node_path_weight[actual_node] + actual_node.get_cost(neigh)
                    if node_path_weight[neigh] > distance:
                        node_path_weight[neigh] = distance
                        node_path[neigh] = node_path[actual_node].copy()
                        node_path[neigh].append(actual_node)
        return node_path
    
    """
    Efecto: carga la tabla de enrutamiento basada en los caminos mas cortos.
    Requiere: (graph) grafo.
              (lowest_path) diccionario con caminos mas cortos de cada nodo.
    Modifica: No aplica.
    Retorna: tabla de enrutamiento como lista de listas.
    Autor: Roy Rojas.
    """
    def routing_table_load(self, graph, lowest_path):
        root_node = graph.get_vertex(self.node_id)
        routing_table = []
        for node in graph.get_vertices():
            if node != root_node:
                node_id = node.get_value()
                neigh = 0
                if len(lowest_path[node]) > 1:
                    neigh = lowest_path[node][1].get_value()

                elif len(lowest_path[node]) == 1 and lowest_path[node][0] == root_node:
                    neigh = node_id
                else:
                    neigh = list(self.neighbours.keys())[0]
                    
                routing_table.append([node_id, self.neighbours[neigh][1]])
        return routing_table
    
    """
    Efecto: envia routing_table a send_queue para ser dirigida al componente verde.
    Requiere: (routing_table) tabla de enrutamiento.
    Modifica: (send_queue) agrega un paquete a send_queue.
    Retorna: No aplica.
    Autor: Roy Rojas
    """
    def routing_table_send(self, routing_table):
        protocol = 101
        nodes_count = len(routing_table)
        pack_format = "!BB"
        packet = struct.pack(pack_format, protocol, nodes_count)
        packet_size = len(packet)

        for i in range(nodes_count):
            pack_format = "!%dsHB" % packet_size
            packet = struct.pack(pack_format, packet, routing_table[i][0],
                    routing_table[i][1])
            packet_size = len(packet)
        self.send_queue.put(packet)

    """
    Efecto: carga el paquete de adyacencias a vecinos propios para ser
            enviado cuando se necesite.
    Requiere: self.neighbours adecuadamente cargado.
    Modifica: No aplica.
    Retorna: (packet) paquete cargado con el formato de adyacencias.
    Autor: Roy Rojas
    """
    def adjacencies_packet_create(self):
        neighbours_list = list(self.neighbours.keys())
        neighbours_count = len(neighbours_list)
        costs = [w[0] for w in self.neighbours.values()]
        
        packet = struct.pack("!BHBBHB", 1, self.node_id, 15, 3, self.node_id, neighbours_count)
        packet_size = len(packet)

        for i in range(neighbours_count):
            pack_format = "!%dsHB" % packet_size
            packet = struct.pack(pack_format, packet, neighbours_list[i], costs[i])
            packet_size = len(packet)
        return packet
    
    """
    Efecto: envia las adyacencias a send_queue una vez algun proceso ejecute
            semaphore.release().
    Requiere: No aplica.
    Modifica: send_queue.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def adjacencies_send(self):
        while True:
            self.semaphore.acquire()
            self.send_queue.put(self.adjacencies_packet)
    
    """
    Efecto: suma al semaforo para que sean enviadas adyacencias.
    Requiere: No aplica.
    Modifica: semaphore.
    Retorna: No aplica.
    Autor: Pablo Cheng.
    """
    def adjacencies_send_unlock(self):
        self.semaphore.release()
    
    """
    Efecto: define las referencias a instancias de green_agent y spanning.
    Requiere: (agent) instancia de green_agent.
              (spanning) instancia de spanning_tree.
    Modifica: green_agent y spanning_tree.
    Retorna: No aplica.
    Autor: Pablo Cheng.
    """
    def set_instances(self, agent, spanning,sb):
        self.green_agent = agent
        self.spanning_tree = spanning
        self.sandbox = sb
    
    """
    Efecto: Devuelve y recolecta el mensaje de stat, para sandbox
    Requiere: Mensaje de request de sandbox para desbloquear 
        la cola, y devolver la stat
    Modifica:No aplica.
    Retorna: No aplica.
    Autor: Pablo Cheng.
    """
    def adj_send_stat(self):
        while(True):
            message = self.stat_queue.get(block=True)
            message = struct.unpack("!4B",message)
            new_message = str(message[0])+str(message[3])+str(message[1])+str(message[2])
            new_message = self.get_adj_stat()
            new_message = struct.pack("!4B"+str(len(new_message))+"s",104,3,message[1],message[2],new_message.encode('UTF-8'))
            self.sandbox.SB_dispatcher_store(new_message)

    """
    Efecto: Crea hilera con stats del grafo 
    Requiere: Tabla de adyacencias con datos
    Modifica: No aplica.
    Retorna: No aplica.
    Autor: Pablo Cheng.
    """
    def get_adj_stat(self ):
        payload = ''
        if (len(self.adj_table)):
            for i in range(len(self.adj_table)):
                node = self.adj_table[i][0]
                if (i == 0 or node != self.adj_table[i-1][0]):
                    if (i != 0):
                        payload += ';'
                    payload += str(node)

                    for j in range(len(self.adj_table)):
                        if (node == self.adj_table[j][0]):
                            payload += ',' + str(self.adj_table[j][1]) 
            return str(payload)+';-'
        return '0'
    
    """
    Efecto: Metodo para almacenar request de 
        la estadistica 3, desde sandbox
    Requiere: Buffer con el request de la 
        estadistica, cola stat_queue inicializada.
    Modifica: stat_queue
    Retorna: No aplica.
    Autor: Pablo Cheng.
    """
    def stat_queue_store(self, buffer):
        self.stat_queue.put(buffer)