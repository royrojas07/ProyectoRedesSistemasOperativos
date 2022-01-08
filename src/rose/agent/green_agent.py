import os 
import sys
import time
import queue
import threading
import struct
from threading import Thread

SENDINGTHREAD   =   0
ASSIGNERTHREAD  =   1
RECEIVINGTHREAD =   2
FWPACKET        =   5
BCPACKET        =   2

class GreenAgent: 
    def __init__(self, id):
            self.receiving_pipe_name = "rose_snd_pp"+id
            self.sending_pipe_name = "rose_rcv_pp"+id
            self.green_send_queue = queue.Queue()
            self.green_assign_queue = queue.Queue()
            self.threads = [Thread( target=self.green_send, args=()),
                 Thread( target=self.green_assign, args=()), 
                    Thread( target=self.green_recv, args=())]
    
    def __del__(self):
        for x in self.threads:
            x.join()

    def threat_init(self):
        for x in self.threads:
            x.start()
        
    def green_send(self):
        sending_pipe = os.open( self.sending_pipe_name, os.O_WRONLY)
                
        while(1):
            buffer = self.green_send_queue.get(block=True)
            msg_len = struct.pack('!h', len(buffer))
            os.write(sending_pipe, msg_len.encode())
            os.write(sending_pipe, buffer.encode())
        
    def green_send_store(self, buffer):
        self.green_send_queue.put(buffer)

    
    def green_recv(self):
        receiving_pipe = os.open( self.receiving_pipe_name, os.O_RDONLY)
        while(1):
            buffer = os.read(receiving_pipe, 2)
            if len(buffer) > 1:
                # Primeros dos bytes indican el tamaño del mensaje.
                msg_len = struct.unpack('!h',buffer)[0]
                buffer = os.read(receiving_pipe, msg_len)
                self.green_assign_queue.put(buffer)
            time.sleep(0.1)


    def green_assign(self):
        while(1):
            buffer = self.green_assign_queue.get(block=True)
            protocol = 1
            if protocol == FWPACKET:
                #stores in fordwarding queue
                pass
            elif protocol  == BCPACKET:
                pass
                #stores in broadcast queue
        return 0
