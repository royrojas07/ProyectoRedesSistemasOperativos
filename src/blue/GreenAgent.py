import time
import queue
import threading 
import struct 
import sys
import os
from threading import Thread 
from socket import *
from socket import SHUT_RDWR
from Interpreter import Interpreter
from log import Log
import log
import signal

SEND_THREAD = 0
RECV_THREAD = 1
SPIDER_PROTOCOL = 105
DATA_PACKET = 0
BC_DEST = 65535

""" 
    Esta clase se escarga de la comunicacion con el verde, a traves de tcp recibe y envia paquetes. 
 """

class GreenAgent:
    # Parametros: 
    #     ip direccion ip del servidor. 
    #     port numero de puerto para la comunicacion.
    #     log objeto log.
    # Autor: Diego Murillo Porras B85526
    def __init__(self, ip, port, log):
        self.ip = ip
        self.port = port
        self.threads = [Thread(target=self.green_send, args=()),
            Thread(target=self.green_recv, args=())]
        self.green_send_queue = queue.Queue()
        self.green_recv_queue = queue.Queue()
        self.sock = socket( AF_INET, SOCK_STREAM )
        self.log = log
        self.interpreter = Interpreter(log)
    
    # Efectua: iniciliza los threads que correran en la comunicacion. 
    # Autor: Diego Murillo Porras B85526
    def thread_init(self):
        for thread in self.threads:
            thread.start()

    # Efectua: establece coneccion con el servidor (nodo verde)
    # Autor: Diego Murillo Porras B85526
    def server_connect(self):
        print("WAITING FOR SERVER CONECTION.")
        notConnected = True
        while(notConnected):
            try:
                self.sock.connect( (self.ip, self.port) )
                notConnected = False
            except ConnectionRefusedError:
                self.log.log_event(3, "no_tcp_connection" )
                time.sleep(2)
        print("CONTECTED TO SERVER.")

    # Efectua: envia paquetes a travez del socket tcp. 
    # Autor: Diego Murillo Porras B85526
    def green_send(self):
        while(True):
            pkt = self.green_send_queue.get(block = True)
            try: 
                size = struct.pack("B", len(pkt))
                self.sock.send( size )
                self.sock.send( pkt )
                self.log.log_event(1, "send_b->g" )
            except IOError as e:
                self.log.log_event(3, "SOCKET NOT CONNECTED." )

    # Efectua: recibe paquetes a traves del socket tcp. 
    # Autor: Diego Murillo Porras B85526
    def green_recv(self): 
        try:
            while True:
                pkt = self.sock.recv( 207 )
                if sys.getsizeof( pkt ) > 1:
                    protocol = struct.unpack( "!B", pkt[:1] )
                    if protocol[0] == SPIDER_PROTOCOL :
                        self.interpreter.print_spider_luggage(pkt)
                        self.log.log_event(1, "recv_g->b <Spider>")
                    elif protocol[0] == DATA_PACKET:
                        self.interpreter.print_data_packet(pkt)
                        self.log.log_event(1, "recv_g->b <Data>")
        except:
            print("\t\tLOST CONECTION WITH SERVER.")
        self.sock.shutdown(SHUT_RDWR)
        self.sock.close()
        os.kill(os.getpid(), signal.SIGINT)


        




