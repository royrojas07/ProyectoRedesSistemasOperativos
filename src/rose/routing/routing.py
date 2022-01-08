import os 
import sys
import time
import queue
import threading
import struct
from threading import Thread

class Routing: 
    def __init__(self):
            self.adj_table = []
            self.routing_table = []
            self.neigh_positions = []
            self.routing_queue = queue.Queue()
            self.dijkstra_queue = queue.Queue()
            self.threads = [Thread( target=self.dijkstra_init, args=()),
                            Thread( target=self.adj_table_init, args=()),
                            Thread( target=self.table_sender_init, args=())]
    # table 
    #| N | Vecinos1 | peso | 
    #| N | Vecinos2 | peso | 
    #| N | Vecinos3 | peso | 
    #| N1| Vecinos1 | peso | 


    def threat_init(self):
        for x in self.threads:
            x.start()
            # x.daemon = True
    
    def adj_table_init(self):
        print("table init")

    def dijkstra_init(self):
        print("Dijkstra")
    
    def table_sender_init(self):
        print("sender")
    
    def routing_queue_store(self):