import os 
import sys
import time
import queue
import threading
import struct
from threading import Thread
import spanning_tree
import routing 
import Sandbox

SENDINGTHREAD   =   0
ASSIGNERTHREAD  =   1
RECEIVINGTHREAD =   2
ROUTER          =   5
SPANTHREE       =   2
HB              =   4
STAT            =  104
POINTER_FILE    =  105

class GreenAgent: 
    def __init__(self, id):
            self.receiving_pipe_name = "rose_snd_pp"+id
            self.sending_pipe_name = "rose_rcv_pp"+id
            self.green_send_queue = queue.Queue()
            self.green_assign_queue = queue.Queue()
            self.threads = [Thread( target=self.green_send, args=()),
                 Thread( target=self.green_assign, args=()), 
                    Thread( target=self.green_recv, args=())]
            self.router = 0
            self.span_three = 0
            self.sandbox = 0
            self.sw = 0
    
    #efectua: Inicializa los threads que se van a encargar de las funcionalidades 
    #Autor Diego Murillo Porras
    def threat_init(self):
        for x in self.threads:
            x.start()

    #Efectua: Metodo que se encarga de mandarle msj por pipe al componente verde
    # Requiere que el fifo haya sido establecido 
    # Autor Diego Murillo Porras 
    def green_send(self):
        sending_pipe = os.open( self.sending_pipe_name, os.O_WRONLY)
        while(1):
            buffer = self.green_send_queue.get(block=True)
            msg_len = struct.pack('!H', len(buffer))
            os.write(sending_pipe, msg_len)
            os.write(sending_pipe, buffer)

    #Efectua: Metodo utilizado para que las otras funcionalidades tengan acceso a esta cola y sus paquetes puedan salir de rosado
    #Param: Paquete que se va a enviar para verde
    #Autor Diego Murillo Porras
    def green_send_store(self, buffer):
        self.green_send_queue.put(buffer)

    
    #Efectua: Recibe los msj que vienen de verde por medio de su pipe
    #Requiere: Que este pipe este establecido 
    #Autor: Diego Murillo Porras
    def green_recv(self):
        receiving_pipe = os.open( self.receiving_pipe_name, os.O_RDONLY)
        try:
            while(1):
                buffer = os.read(receiving_pipe, 2)
                msg_len = struct.unpack("!H", buffer)[0]
                if msg_len > 0:
                    # Primeros dos bytes indican el tamaño del mensaje.
                    buffer = os.read(receiving_pipe, msg_len)
                    self.green_assign_queue.put(buffer)
        except:
            pass
                

    #Efectua: Metodo que se encarga de entregar a las distintas funicionalides en la capa de control
    #Autor: Diego Murillo Porras
    def green_assign(self):
        while(1):
            buffer = self.green_assign_queue.get(block=True)
            protocol = struct.pack("!B", buffer[0])[0]
            if protocol == 1:
                self.router.routing_queue_store(buffer)
            elif protocol  == SPANTHREE or protocol == HB: 
                self.span_three.dispacher_store(buffer)
                #stores in broadcast queue
            elif protocol == STAT or protocol == POINTER_FILE:
                self.sandbox.SB_dispatcher_store(buffer)
            elif protocol == 5:
                self.sw.recv(buffer)

        return 0

    #Efectua: Asigna las intancias necesarias dentro de este componente
    #Requiere: A router y spanning tree inicializados 
    #Param: instancias de router y spanning tree
    #Autor: Diego Murillo Porras
    def set_instancies(self, r, spt,sd, sw):
        self.router = r
        self.span_three = spt
        self.sandbox = sd
        self.sw = sw