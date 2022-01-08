import os 
import sys
import time
import queue
import threading
import struct
import subprocess
from datetime import datetime
import GreenAgent
import routing 
import signal
from threading import Thread
from multiprocessing import Process
import posix_ipc
import StopWait

STAT_PROTOCOL = 104 #Procolo para las estadisticas
POINTERS_PROTOCOL = 105 #Procolo utilizado para los punteros del luggage, exe y los destinos
CHUNK_SIZE = 430 #En cuantos bytes se van a separar los paquetes 

sem = threading.Semaphore(0)

class Sandbox:
    #Costructor de la clase 
    #Param: id del node en el cual se esta 
         # Futura bitacora encargada del log del rosado
    #Autor: Carlos Urena 
    def __init__(self,id,bitacora):
        self.stat_queue = queue.Queue() #For the spider request
        self.pointers_queue = queue.Queue() #es para los archivos de luggage y spider que llegan de azul 
        self.dispatcher_queue = queue.Queue() 
        self.deconstruct_queue = queue.Queue()
        self.connect_queue = queue.Queue()
        self.manager_mailbox = posix_ipc.MessageQueue("/manager"+id, posix_ipc.O_CREAT)
        self.mailbox_dict = {} #diccionario para asociar los mailbox respectivos a la spider

        #Este diccionario contiene llaves a punteros archivo de tanto arañas como de sus valijas 
        self.files_dict = {}

        #Diccionario que se maneja cuando solo me llega lugagge identificando que se debe usar una logica diferente
        self.only_luggage_dict = {}

        self.id = id
        self.bitacora = bitacora

        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <SB> Sandbox was created\n" )

        #Se inicializan en set_instances 
        self.g_agent = 0
        self.router = 0
        self.sw = 0

        #Colas para stop and Wait
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue() 

        #Hilos de la funcionalidad
        self.threads = [Thread( target=self.construct, args=()),
                        Thread( target=self.mailbox_manager, args=()),
                        Thread( target=self.dispatcher, args=()),
                        Thread( target=self.own_spider_runner, args=()),
                        Thread( target=self.deconstruct, args=())]

    #Efecto: Encargado de iniciar los Threads 
    #Autor: Carlos Urena 
    def thread_init(self):
        for x in self.threads:
            x.start()

    #Efecto: Encargado de administrar a cual hilo va determinado paquete que viene del verde
    def dispatcher(self):
        while True:
            packet = self.dispatcher_queue.get()
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <SB> A packet came from green to Sandbox\n" )
            protocol = struct.pack('@B', packet[0])[0]
            if(protocol == POINTERS_PROTOCOL):
                self.pointers_queue.put(packet)
            elif(protocol == STAT_PROTOCOL):
                self.stat_queue.put(packet)


    #Efecto: Metodo publico que usa el dispatcher de rosado para mandar la solicitud a esta funcionalidad
    #Autor: Carlos Urena 
    def SB_dispatcher_store(self,buffer):
        self.dispatcher_queue.put(buffer)
    
    #Efecto: Encargado de escuchar solitudes de las spider y devolverles su solicitud 
    #Autor: Carlos Urena 
    def mailbox_manager(self):
        global sem
        while True:
            sem.acquire() #evita busy wait
            request = self.manager_mailbox.receive() #Escucha las solicitudes de sus spider
            #request_items = request[0].decode().split(',') #Decode() para pasar de binario a texto y split para separar lo enviado 
            request_items = struct.unpack("=2B",request[0])
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> A request from spider " +str(request_items[0])+ " was received\n" )
            if request_items[1] == 0: #solicitud 0, termino          
                #lineas encargadas de cerrar los mailbox 
                self.mailbox_dict[str(request_items[0])].close()
                self.mailbox_dict[str(request_items[0])].unlink()

                #Encargado de eliminar el elemento del diccionario
                del self.mailbox_dict[str(request_items[0])]
                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <SB> The spider "+str(request_items[0])+" wants to finish\n" )
                #os.wait() #Espero a que la spider termine para que no quede como zombie
                time.sleep(0.5)
                self.deconstruct_queue.put(str(request_items[0])) #Signal de que tiene que ser deconstruida
            else:
                sem.release()
                #Empaqueto la solicitud de la spider en binario 
                request_paquet = struct.pack("!4B",STAT_PROTOCOL, request_items[0], 0, request_items[1])

                if(int(request_items[1]) == 3): #si es la solicutud 3 se le pregunta a router por la tabla de adyacencias
                    self.router.stat_queue_store(request_paquet)
                else:
                    self.g_agent.green_send_store(request_paquet) #Envia a GreenAgent el paquete para que se encarga de llevarlo a verde
                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> The spider "+str(request_items[0])+" sent a request\n" )
                stat_packet = self.stat_queue.get() #pop blocking 
                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> The spider "+str(request_items[0])+"'s request was received\n" )
                stat_packet = stat_packet[1:] #esto le cortaria el protocolo interno 
                spider_id = str(stat_packet[1]) #Obtengo el id de la spider que es la llave del diccionario
                stat_packet = stat_packet[3:] #esto le cortaria el id de spider y el id de la solicitud
                self.mailbox_dict[spider_id].send(stat_packet) #Envio al mailbox que me dice el diccionario 

    #Efecto: Encargado de hacer exec a la spider y crear su respectivo mailbox
    #Autor: Carlos Urena
    def construct(self): 
        self.S_W_Communication() #primero se debe establacer la cola in y out para comunicarse con 
        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <SB> The queue in and out were sent to SW\n" )
        while True: #Ciclo para seguir escuchando solicitudes
            packet = self.out_queue.get() #get blocking que evita el busy wait
            protocol = struct.pack("@B", packet[0])[0] #reviso el primer byte de protocolo para ver si es un cierre de conexion o si es un paquete de datos
            if(protocol == 0):
                self.connect_queue.put(packet)#si es paquete de respuesta de conexion se lo envio a connect por medio de esta cola 
            else:
                sand_packet_aux = struct.unpack("!2BHBH",packet[:7]) #primero hago unpack de unicamente esta parte del paquete para determinar el tamaño de lo que vamos a leer de payload
                key = str(sand_packet_aux[2]) #llave de diccionario compuesta por Origen
                payload_length = sand_packet_aux[4] #aqui saco el tamaño del payload
                sand_packet = struct.unpack("!2BHBH"+str(payload_length)+"s",packet[:(7+payload_length)]) #desempaco ahora si con el payload
                data_type = sand_packet[1] #determino que tipo de paquete es, si exe o luggage o destinos
                if data_type == 3:
                    self.final_packet_work(key)
                elif(key in self.only_luggage_dict):
                    #useful_bytes = sand_packet[5].split(b'\x00')[0]
                    self.only_luggage_dict[key].write(sand_packet[5])  
                elif key in self.files_dict: #pregunto si existe esa key en el diccionario
                    self.medium_packet_work(sand_packet,key,data_type)
                else: #si no existe la key en los diccionarios
                    self.first_packet_work(sand_packet,key,data_type)
    
    #Efecto: Encargado de crear las entradas del diccionario que administraran el resto de paquetes que llegar de esa araña respectiva o bien si llega 
    # solo luggage detectarlo y proceder con diferente logica
    #param: paquete con los datos en binario 
            #LLave que se creo a partir del origen_idSpider que sirve como llave en el diccionario principal
            #El tipo de dato que es, si es valija o ejecutable o destinos 
    #Author: Carlos Ureña Alfaro
    def first_packet_work(self,sand_packet,key,data_type):
        if(data_type == 2):
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> A packet with only luggage came\n" )
            f = open("luggage"+str(key)+".txt",'wb+') #asi que creamos el archivo de luggage
            self.only_luggage_dict[key] = f
            #useful_bytes = sand_packet[5].split(b'\x00')[0]
            self.only_luggage_dict[key].write(sand_packet[5])
        else:
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> A packet with destinies came\n" )
            self.files_dict[key] = [] #creo la key y le digo que guarda una lista
            destiny_list = sand_packet[5].decode().split(',') #la primer entrada de esta lista sera una lsita de destinos 
            self.files_dict[key].append(destiny_list) #se la agrego
            #time.sleep(0.4)#esperarme un poco para crearlo porque aveces se crea y el nodo pasado lo vuelve a borrar entonces no se lee el archivo
            f = open(str(key),'wb+') #creo el archivo del ejecutable de la spider
            self.files_dict[key].append(f) #lo agrego al diccionario 
            f2 = open("luggage"+str(key)+".txt",'wb+') #asi que creamos el archivo de luggage
            self.files_dict[key].append(f2)#lo agregamos al diccionario 

    #Efecto: Son los eventos instermedios que solo pasan a disco los paquetes que llegan
    # param:El paquete con los datos que llega de S&W
        #La llave del diccionario que identifica a que lugar se guarda la informacion que llega
        #El tipo de dato que llego, si es exe o luggage
    #Author: Carlos Ureña Alfaro
    def medium_packet_work(self,sand_packet,key,data_type):
        if(data_type == 1):#llego un paquete de spider
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> A exe packet came\n" )
            #useful_bytes = sand_packet[5].split(b'\x00')[0]
            self.files_dict[key][1].write(sand_packet[5])
        elif(data_type == 2): #significa que estamos armando el luggage
                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> A luggage packet came\n" )
                #useful_bytes = sand_packet[5].split(b'\x00')[0]
                self.files_dict[key][2].write(sand_packet[5])

    #Efecto: Encargado de mandar a ejecutar la spider y crear la entrada que utiliza el mailbox manager para escucharla
    #param: La llave que corresponde a la entrada del diccionario de lo que se quiere mandar a ejecutar
    #Author: Carlos Ureña Alfaro
    def final_packet_work(self,key):
        global sem
        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> The final packet came\n" )
        if(key in self.files_dict):
            self.files_dict[key][1].close()
            pid = os.fork()
            if pid == 0:
                subprocess.call(['chmod', '0777', self.files_dict[key][1].name]) #el ejecutable que acabo de armar le doy permisos 
                #formato para el exec: ejecutable id_spider #nodo maleta sandbox_mailbox spider_mailbox
                #time.sleep(0.7)
                os.system("./"+ self.files_dict[key][1].name + " " + key + " " + self.id + " " + self.files_dict[key][2].name + " /manager"+self.id+ " /" +str(key))
            else:
                self.files_dict[key][2].close() #cierro el lugagge porque a este punto ya lo hubiera terminado de armar
                self.mailbox_dict[key] = posix_ipc.MessageQueue("/"+str(key),posix_ipc.O_CREAT)
                sem.release()
        elif(key in self.only_luggage_dict):
            self.only_luggage_dict[key].close()
            packet = struct.pack("!B"+str(len(self.only_luggage_dict[key].name))+"s",105,self.only_luggage_dict[key].name.encode('UTF-8'))
            self.g_agent.green_send_store(packet)
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> The luggage was sent to blue\n" ) 
            self.only_luggage_dict[key].close()
            del self.only_luggage_dict[key]
    

    
    #Efecto: Deconstruye lo especificado en los parametros
    #Param: Un llave que indica cual es el archivo en el diccionario que vamos a partir
    #Autor: Carlos Ureña 
    def deconstruct(self):
        count = 0 
        while True:
            key = self.deconstruct_queue.get() #Es blocking por default
            print("Deconstruyendo...")
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> Deconstruct was called\n" )
            real_spider_id = key
            destinies = self.files_dict[key][0]
            if(destinies[0] == '-\n' or destinies[0] == '-'): #condicion de que tengo que enviarsela al origin si es True
                self.send_to_origen(key,real_spider_id)
            else:
                retry_connect = True
                while(retry_connect):
                    if(self.set_connect(destinies[0])):
                        destinies.pop(0)
                        retry_connect = False
                        str_destinies = ','.join(destinies) #hago que la lista de destinos se vuelva una hilera de destinos separada por comas
                        packet = struct.pack("!H2BHBH"+str(len(str_destinies))+"s",int(self.id),6,0,int(real_spider_id),count,len(str_destinies),str_destinies.encode('UTF-8'))
                        self.in_queue.put(packet)
                        exe_file = self.files_dict[key][1].name
                        with open(exe_file, 'rb') as infile:
                            while True:
                                chunk = infile.read(CHUNK_SIZE)  #Lee la longitud de la constante CHUNK_SIZE para partir
                                if not chunk: #indica cuando ya no hay mas bytes
                                    self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <SB> Exe file "+exe_file+" was chunked\n" )
                                    os.remove(exe_file)
                                    break
                                useful_bytes = chunk.split(b'\x00')[0]
                                packet = struct.pack("!H2BHBH"+str(len(useful_bytes))+"s",int(self.id),6,1,int(real_spider_id),count,len(useful_bytes),useful_bytes)
                                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> Exe file "+exe_file+" was sent\n" )
                                self.in_queue.put(packet)
                        luggage_file = self.files_dict[key][2].name
                        with open(luggage_file, 'rb') as infile:
                            while True:
                                chunk = infile.read(CHUNK_SIZE)  #Lee la longitud de la constante CHUNK_SIZE para partir
                                if not chunk: #indica cuando ya no hay mas bytes
                                    self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <SB> Luggage file "+luggage_file+" was chunked\n" )
                                    os.remove(luggage_file)
                                    break
                                useful_bytes = chunk.split(b'\x00')[0]
                                packet = struct.pack("!H2BHBH"+str(len(useful_bytes))+"s",int(self.id),6,2,int(real_spider_id),count,len(useful_bytes),useful_bytes)
                                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> luggage file "+luggage_file+" was sent\n" )
                                self.in_queue.put(packet)
                        del self.files_dict[key]
                        packet = struct.pack("!H2BHBH",int(self.id),6,3,int(real_spider_id),count,0)
                        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> Final packet was sent\n" )
                        self.in_queue.put(packet)
                        disconnect_packet = struct.pack("!2H",255,int(self.id))
                        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> Desconnect packet to S&W was sent\n" )
                        self.in_queue.put(disconnect_packet)
                        count += 1
                    else:
                        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 3 <SB> SW can't connect with the requested node\n" )

    #Efecto:Caso en el que se tiene que enviar unicamente el luggage al origen
    #param:Key del diccionario para acceder a los datos y una lista que contiene al origen y al id de la spider
    #Author: Carlos Ureña Alfaro
    def send_to_origen(self,key,real_spider_id):
        print("Se va a mandar al origen la valija...")
        if(self.set_connect(real_spider_id[0])):
            luggage_file = self.files_dict[key][2].name
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <SB> The luggage "+luggage_file+" is sent to the origen "+real_spider_id[0]+"\n" )
            with open(luggage_file, 'rb') as infile:
                while True:
                    chunk = infile.read(CHUNK_SIZE)  #Lee la longitud de la constante CHUNK_SIZE para partir
                    if not chunk: #indica cuando ya no hay mas bytes
                        os.remove(luggage_file) #remuevo del file system al luggage
                        os.remove(self.files_dict[key][1].name) #remuevo del file system al exe
                        break
                    packet = struct.pack("!H2BHBH"+str(CHUNK_SIZE)+"s",int(self.id),6,2,int(real_spider_id),0,CHUNK_SIZE,chunk)
                    self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> Luggage file "+luggage_file+" was sent\n" )
                    self.in_queue.put(packet)
            del self.files_dict[key]
            packet = struct.pack("!H2BHBH",int(self.id),6,3,int(real_spider_id),0,0)
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> Final packet was sent\n" )
            self.in_queue.put(packet)
            disconnect_packet = struct.pack("!2H",255,int(self.id))
            self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 1 <SB> Desconnect packet to S&W was sent\n" )
            self.in_queue.put(disconnect_packet)

    #Efecto: Envia una solicitud de conexion a SW y espera respuesta de si se logro  
    #Param: Siguiente destino con el que se quiere realizar comunicacion
    #Author: Carlos Ureña Alfaro
    def set_connect(self,destiny):
        self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <SB> The next destiny is "+destiny+"\n" )
        packet = struct.pack("!3H",0,int(destiny),int(self.id))
        self.in_queue.put(packet)
        answer = self.connect_queue.get()
        answer = struct.unpack("2B",answer)
        if(answer[1] == 0): #Aqui determino que hacer segun lo que me devolvio S&W
            return False
        else:
            return True

    #Efecto: Encargado de mandar a ejecutar las arañas propias
    #Author: Carlos Ureña Alfaro
    def own_spider_runner(self):
        global sem
        receiver_count = 0 #maneja el flujo de que se esta recibiendo, si los destinos, spider o valija
       # key_count = 0 #contador que permite ir creado spiders propias con llave unica
        while True:
            pointer_packet = self.pointers_queue.get()
            pointer_packet = pointer_packet[1:].decode() #esto le cortaria el protocolo interno 
            if(receiver_count == 0): #primero que se recibe
                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> A packet from blue came with destinies\n" )
                key = self.id
                self.files_dict[key] = [] #le asocio una lista al diccionario 
                destinies = pointer_packet.split(';') #lista de destinos 
                self.files_dict[key].append(destinies) #agrego a la lista
                receiver_count += 1 #proximo paquete sera ejecutable
            elif(receiver_count == 1): #paquete es ejecutable
                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> A packet from blue came with the executable\n" )
                subprocess.call(['chmod', '0777', pointer_packet]) #el ejecutable que acabo de armar le doy permisos 
                f = open(pointer_packet,'rb') #ejecutable con permiso de escribir
                f.close()
                self.files_dict[key].append(f) #lo agrego a la lista
                receiver_count += 1 #proximo a esperar valija
            else: #llego valija
                self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 <SB> A packet from blue came with the luggage\n" )
                receiver_count = 0 #cuenta desde 0 de nuevo para futura spider
                f = open(pointer_packet,'rb') #ejecutable con permiso de escribir
                f.close()
                self.files_dict[key].append(f) #guardo el nombre del luggage para destruirlo mas tarde
                pid = os.fork()
                if pid == 0:
                    #formato para el exec: ejecutable id_spider #nodo maleta sandbox_mailbox spider_mailbox
                    os.system("./"+ self.files_dict[key][1].name + " " + key + " " + self.id + " " + pointer_packet + " /manager"+self.id+" /" +str(key))
                else:
                    self.bitacora.write('[' + str(datetime.now()) + '] ' + "Case 0 <SB> The spider "+str(key)+" was executed\n" )
                    self.mailbox_dict[key] = posix_ipc.MessageQueue("/"+str(key),posix_ipc.O_CREAT)
                    sem.release()


    #Efecto: Asigna las instacias necesarias de la clase 
    #Autor: Carlos Urena 
    def set_instancies(self,g_agent,router,sw): 
        self.g_agent = g_agent
        self.router = router
        self.sw = sw

    #Efecto: Le comparte a SW las colas in y out que se usaran para la comunicacion
    #Author: Carlos Ureña Alfaro
    def S_W_Communication(self):
        self.sw.set_channel(self.in_queue,self.out_queue,0)

