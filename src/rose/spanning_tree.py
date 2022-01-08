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

TWHPROTOCOL = 2
SYN = 0 #primer envio pregunta
SYNACKY = 1 #respuesta con si puede unirse
SYNACKN = 2 #respuesta con no puede unirse
ACK = 3 #completar la transaccion

#Variable de heartbeat
HBPROTOCOL = 4 
C0 = 0 # vivo?  0
C1 = 1 # estoy vivo. 

BROADCASTUPDATE = 102

class SpanningTree:
    #Efectua: Metodo contructor de Spanning Three
    #param:id de si mismo, nb_table con los id's de los vecinos y el agente verde que usa el pipe
    #Autor: Diego Murillo Porras
    def __init__(self, id, bitacora):
        self.bool_table = {} # diccionario <id> : <bool>
        self.nb_table = 0 # nb id
        self.alive_queue = queue.Queue()
        self.question_queue = queue.Queue() # For downlinks and alive answer. 
        self.answer_queue = queue.Queue() # for TTH y HB
        self.dispacher_queue = queue.Queue()
        self.id = int(id)
        self.bitacora = bitacora
        if self.id == 1 : #Verificando el caso especial del nodo 1 que ya estaria en el arbol
            self.connected = True 
        else:
            self.connected = False # Me dice si es parte del AG o no 
        
        bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <ST> Spanning Tree was created\n" )

        self.threads = [Thread( target=self.answer_sender, args=()),
                 Thread( target=self.stablish_uplink, args=()), 
                    Thread( target=self.dispacher, args=())]

        

        #se inicializan en un metodo set
        self.g_agent = 0
        self.router = 0

    #efectua: Inicializa los threads de la clase
    def thread_init(self):
        for x in self.threads:
            x.start()
            #x.daemon = True

    #Efectua: Metodo ejecutado por un thread que se encargar de responder a las preguntas de HB y TWH
    #modifica: Tabla de AG a la hora de establecer alguien como Downlink
    #Autor: Carlos Urena Alfaro
    def answer_sender(self):# Responde a las preguntas de TTH y HB
        while True:
            question_packet = self.question_queue.get()
            protocol = struct.pack("@B", question_packet[0])[0]
            if protocol == TWHPROTOCOL:
                question_packet = struct.unpack("!2B4H", question_packet)
                act = question_packet[1]
                origin = question_packet[2]
                if act == SYN:
                    self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <ST> A question to join was sent\n" )
                    SN = question_packet[4]
                    RN = SN + 1
                    if self.connected:# es parte de arbol
                        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <ST> I will answer yes you can "+str(origin)+"\n" )
                        ag_paquet = struct.pack("!2B4H", TWHPROTOCOL, SYNACKY, self.id, origin, SN, RN)
                    else:
                        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <ST> I will answer no you cant "+str(origin)+ "\n" )
                        ag_paquet = struct.pack("!2B4H", TWHPROTOCOL, SYNACKN, self.id, origin, SN, RN)
                    self.g_agent.green_send_store(ag_paquet) #envio paquete
                elif act == ACK:
                    SN = question_packet[4]
                    if SN == RN:
                        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <ST> Ok, you join to my downlinks, TWH ended\n" )
                        print("New downlink")
                        self.bool_table[origin] = True #establezco el downlink en la tabla 
                        self.send_update_to_bc(origin) #le envio a verde la update de la tabla
                        self.router.adjacencies_send_unlock()
            elif protocol == HBPROTOCOL:
                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <ST> A question if Im alive came from\n" )
                question_packet = struct.unpack("!B2HB2H", question_packet)
                origin = question_packet[1]
                SN = question_packet[4]
                RN = SN
                hb_c1 = struct.pack("!B2HB2H", HBPROTOCOL, self.id, origin, C1, SN, RN)
                self.g_agent.green_send_store(hb_c1) #envio paquete


    #Efectua:Metodo ejecutado por un thread que se matendra vivo hasta que establezca el Uplink 
    #modifica: Atributo connected que indica si se es parte de AG o no
    #Autor: Carlos Urena Alfaro
    def stablish_uplink(self):# Establece el uplink
        while not self.connected: 
            for i in range(len(self.nb_table)):
                if(self.alive(self.nb_table[i])): 
                    if(self.three_way_handshake(self.nb_table[i])):
                        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <ST> I succesfully join to the AG with "+str(self.nb_table[i])+"\n" )
                        print("Exito al conectarse al AG con " + str(self.nb_table[i]))
                        self.connected = True
                        self.router.adjacencies_send_unlock()

                        break
                else:
                    time.sleep(0.3) #time out (Igual se hace con un promedio de los ping?)

    #Efectua:Encargado de analizar los paquetes enviados por el Green agent y ver a cual funcionalidad interna de spannning Tree enviarla
    #Autor: Diego Murillo Porras
    def dispacher(self):
        while(1):
            packet = self.dispacher_queue.get(block=True)
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0  <ST> A msg to be despatched comes\n" )
            protocol = struct.pack('@B', packet[0])[0]
            if protocol == TWHPROTOCOL:
                packet_aux = struct.unpack("!2B4H", packet)
                tth_type = packet_aux[1]
                if tth_type == SYNACKY or tth_type == SYNACKN:
                    self.answer_queue.put(packet)
                elif tth_type == SYN or tth_type == ACK:
                    self.question_queue.put(packet)
            elif protocol == HBPROTOCOL:
                hb_type = struct.pack("@B", packet[5])[0]
                if hb_type == C0:
                    self.question_queue.put(packet)
                elif hb_type == C1:
                    self.answer_queue.put(packet)

    #Efectua: Metodo utilizado por las demas funcionalidades destro de rosado para comunicarse con spanning tree   
    #param: Paquete el cual se quiere ingresar a la funcionalidad
    # Autor: Diego Murillo Porras   
    def dispacher_store(self, buffer): 
        self.dispacher_queue.put(buffer)

    #Efectua:Metodo que pregunta que si se puede unir al arbol y espera a que esa respuesta llegue para consolidar el trato
    #Modifica: Tabla de AG a la hora de establecer alguien como UpLink
    #Param: el id del nodo respectivo con el que se va a trabajar
    #Autor: Carlos Urena Alfaro
    def three_way_handshake(self,nb):
        SN = randint(0, 255)
        ag_paquet = struct.pack("!2B4H", TWHPROTOCOL, SYN, self.id, nb, SN, 0)
        print("Tratando de hacer Three way:" + str(nb))
        respuesta = False
        conectado = False 
        while not respuesta: #mientras no me haya respondido 
            self.g_agent.green_send_store(ag_paquet) #envio paquete
            try:
                answer_packet = self.answer_queue.get(timeout=5) #pop blocking hasta que pase el timeout
                answer_packet = struct.unpack("!2B4H",answer_packet)
                protocol = answer_packet[0]
                RN = answer_packet[5]
                if protocol == TWHPROTOCOL and RN == (SN + 1): #verifico si la respuesta es valida 
                    action = answer_packet[1]
                    if action == SYNACKY: #si me dijo que si me pude unir 
                        respuesta = True 
                        ag_paquet = struct.pack("!2B4h", TWHPROTOCOL, ACK, self.id, nb, SN + 1, RN)
                        self.g_agent.green_send_store(ag_paquet)
                        conectado = True 
                        self.bool_table[nb] = True #establezco el uplink en la tabla 
                        self.send_update_to_bc(nb) #le envio a verde la update de la tabla
                    else: #si me responde que no me pude unir 
                        respuesta = True
            except queue.Empty:
                time.sleep(0.5)
            time.sleep(2)
        return conectado

    #Efectua: Metodo que efectua el protocolo de HB para indicar si los nodos vecinos estan vivos para proceder con TWH
    #param: id del nodo que se le esta preguntando si esta vivo 
    #Autor: Diego Murillo Porras
    def alive(self, nb): 
        SN = randint(0,255)
        hb_c1 = struct.pack("!B2HB2H", HBPROTOCOL, self.id, nb, C0, SN, 0) 
        print("Preguntando si esta vivo el nodo " + str(nb))
        self.g_agent.green_send_store(hb_c1)
        is_alive = 0
        timeout = 20.0
        while is_alive == 0 and timeout >= 0:
            try:
                packet = self.answer_queue.get(block=False)
                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2  Came a msg that its alive from "+str(nb)+"\n" )
                protocol = struct.pack('@B', packet[0])[0]
                if protocol == HBPROTOCOL:
                    packet = struct.unpack("!B2HB2H", packet)
                    if packet[3] == C1 and SN == packet[5]:
                        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0  Verification if" +str(nb)+" is alive completed\n" )
                        print("Si esta vivo " + str(nb))
                        is_alive = C1
            except queue.Empty:
                pass
            time.sleep(0.01) 
            timeout -= 0.01  # Centecimas 
        if is_alive == C1:
            return True
        return False

    #Efectua: Envia un paquete de protocolo interno que avisa cual vecino se hizo parte del arbol
    #Param: El vecino especifico que ahora forma parte del arbol
    #Autor: Carlos Urena Alfaro
    def send_update_to_bc(self,nb):
        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <ST> Update to bc_table got out\n" )
        bc_update_paquet = struct.pack("!BH",BROADCASTUPDATE,nb)
        self.g_agent.green_send_store(bc_update_paquet)

    #Efectua: Metodo que envia todos los vecinos como parte de arbol generador siguiendo el metodo chambon
    #Autor: Carlos Urena Alfaro
    def send_silly_bc_update(self):
        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <ST> Intelligent mode desactived so the silly send is call\n" )
        for v in self.nb_table:
            bc_update_paquet = struct.pack("!BH",BROADCASTUPDATE,v)
            self.g_agent.green_send_store(bc_update_paquet)
        self.router.adjacencies_send_unlock()

    #Efectua: Asigna las instancias de los componentes necesarios dentro de este
    #Requiere: Que GreenAgent y Routing esten inicializados
    #Param: Las instancias de los componentes que se quieren dentro de las clase
    #Autor: Carlos Urena Alfaro
    def set_instancies(self,g_agent,router):
        self.g_agent = g_agent
        self.router = router

    #efectua: Metodo publico que es usado por router para darme una lista de los vecinos 
    #param: lista con los vecinos 
    #Autor: Carlos Urena Alfaro
    def nb_table_init(self, table):
        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <ST> bc table was init\n" )
        self.nb_table = table