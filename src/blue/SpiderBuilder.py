import time 
import queue
import threading
import struct 
import sys
import os
import queue
import stat
import shutil
from threading import Thread
from GreenAgent import GreenAgent
from interface import Interface
from log import Log

""" 
    Clase encargada de construir el ejcutable y la valija a enviar a ser ejectuada en los nodos.     
 """


class SpiderBuilder:
    def __init__(self, log):
        self.log = log
        self.builder_thread = Thread(target=self.spd_build, args=())
        self.request_queue = queue.Queue()
        self.next_spd_id = 1
        self.gA = 0
    
    # Efectua: inicializa las instancias de las demas clases. 
    # Autor: Diego Murillo Porras B85526
    def set_instances(self, gA):
        self.gA = gA

    # Efectua: inicializa los hilos que correran en las funciones. 
    # Autor: Diego Murillo Porras B85526
    def thread_init(self):
        self.builder_thread.start()
    
    # Efectua: funcion encargada de crear el ejecutable y la valija. 
    # Autor: Diego Murillo Porras B85526
    def spd_build(self):
        while(True):
            request = self.request_queue.get(block=True)
            dest_pkt = self.dest_build(request[0])
            exe_pkt = self.exe_build()
            luggage_pkt = self.luggage_build(request)
            self.gA.green_send_queue.put(dest_pkt)
            self.gA.green_send_queue.put(exe_pkt)
            self.gA.green_send_queue.put(luggage_pkt)
            self.next_spd_id += 1
        
    # Efectua: crea paquete de los destinos. 
    # Autor: Diego Murillo Porras B85526
    def dest_build(self, request):
        dest_string = ""
        for dest in request:
            dest_string += f"{dest};"
        dest_string += "-\n"
        dest_packet_format = "!B%ds" % len(dest_string)
        dest_pkt = struct.pack(dest_packet_format, 105, dest_string.encode())
        return dest_pkt

    # Efectua: crea paquete del ejecutable. 
    # Autor: Diego Murillo Porras B85526
    def exe_build(self):
        spider_name = f"spider{self.next_spd_id}"
        shutil.copy("spider.py", "spider_exe/"+spider_name)
        spider_add = "../blue/spider_exe/" + spider_name
        spider_pkt_format = "!B%ds" % len(spider_add)
        exe_pkt = struct.pack(spider_pkt_format, 105, spider_add.encode())
        return exe_pkt

    # Efectua: crea paquete de la valija. 
    # Autor: Diego Murillo Porras B85526
    def luggage_build(self, request):
        luggage_name = f"luggage{self.next_spd_id}.txt"
        luggage = open("luggage_sent/"+luggage_name, "w+")
        for i in range(1, 3):
            string = ""
            for r in request[i]:
                string += f"{r},"
            string += '-\n'
            luggage.write(string)
        luggage.close()
        luggage_add = "../blue/luggage_sent/" + luggage_name
        luggage_pkt_format = "!B%ds" % len(luggage_add)
        luggage_pkt = struct.pack(luggage_pkt_format, 105, luggage_add.encode())
        return luggage_pkt
    




    