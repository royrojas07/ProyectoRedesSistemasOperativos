import os 
import sys
import time
import queue
import threading
import struct
import random
from random import randint
from datetime import datetime
import GreenAgent
import routing 
import signal
from random import random, randint
from threading import Thread
from multiprocessing import Process
import posix_ipc

STAT_PROTOCOL = 104

class Sandbox:
    def __init__(self,bitacora):
        self.stat_queue = queue.Queue() #For the spider request
   
        self.manager_mailbox = posix_ipc.MessageQueue("manager", posix_ipc.O_CREAT)
        self.mailbox_dict = {}
    
        self.bitacora = bitacora

        self.g_agent = 0
        self.router = 0

        self.threads = [Thread( target=self.construct_deconstruct, args=()),
                        Thread( target=self.mailbox_manager, args=())]

    def thread_init(self):
        for x in self.threads:
            x.start()
    
    def stat_store(self,buffer):
        self.stat_queue.put(buffer)

    def mailbox_manager(self):
        while True:
            if not self.mailbox_dict:
                request = self.manager_mailbox.receive()
                request_items = request[0].decode().split(',')
                if request_items[1] == '0':
                    del self.mailbox_dict[request_items[0]]
                    print("Termino la spider: " + request_items[0])
                    #TODO enviar una signal que esta spider tiene que ser deconstruida 
                request_paquet = struct.pack("@3B",STAT_PROTOCOL,request_items[0],request_items[1])
                self.g_agent.green_send_store(request_paquet)
    
                stat_packet = self.stat_queue.get() #pop blocking 
                #stat_packet = struct.unpack(,packet)
                #stat_packet = stat_packet[1:] esto le cortaria el protocolo interno 
                #spider_id = stat_packet[0]
                #stat_packet = stat_packet[1:] esto le cortaria el id de spider
                #self.mailbox_dict[spider_id].send(stat_packet)
            else:
                time.sleep(2) #paraqueno este revisando constantemente si se hay mailbox que utilizar


    def construct_deconstruct(self):
        pid = os.fork()
        if pid == 0:
            os.system("python Spider.py " + "manager " + "3 " + "1")
        else:
            answer_mailbox = posix_ipc.MessageQueue("1") 
            self.mailbox_dict["1"] = answer_mailbox

    def set_instancies(self,g_agent,router):
        self.g_agent = g_agent
        self.router = router
