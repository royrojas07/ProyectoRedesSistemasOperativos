#!/usr/bin/env python3
import shutil #disk_usage()
import queue #queue()
import posix_ipc #MessageQueue()
import sys #argv[]
import subprocess
import time
import struct
"""
Codigo de clase MemLinux tomado de https://stackoverflow.com/questions/17718449/determine-free-ram-in-python/17718729
"""
#Clase encargada de hacer conversiones de unidades y averiguar los datos de la maquina fisica 
class MemLinux(object):
    #constructor de la clase
    #param: La unidad por default de la clase que en este caso son KB 
    def __init__(self, unit='kB'):

        with open('/proc/meminfo', 'r') as mem: #archivo que me proporciona la informacion de la memoria
            lines = mem.readlines()

        self._tot = int(lines[0].split()[1]) #linea que me da el total de memoria 
        self._free = int(lines[1].split()[1]) #linea que me da la memoria libre 

       
        total,used,free = shutil.disk_usage('/')   #metodo de la libreria que me da informacion del file system 
  
        self._memory_sys = total #guardo el total de la memoria que me dio la libreria shutil en una variable 
        self._free_sys = free #guardo el total de la memoria libre que me dio la libreria shutil en una variable 
       
        self.unit = unit #Asigna la unidad que se paso por parametro como la unidad en la que se trabajara en la clase
        self._convert = self._factor() #Asigna la conversion de unidades que se tiene que hacer

    #Efecto: Se encarga de asociar la conversion que se va a ser segun su unidad 
    def _factor(self):
        if self.unit == 'kB':
            return 1
        if self.unit == 'k':
            return 1024.0
        if self.unit == 'MB':
            return 1/1024.0
        if self.unit == 'GB':
            return 1/1024.0/1024.0
        if self.unit == '%m':
            return 1.0/self._tot
        if self.unit == '%q':
            return 1.0/self._memory_sys
        else:
            raise Exception("Unit not understood")
    

    @property
    def total(self):
        self.unit = 'MB' #Aqui especifico que quiero la memoria en MB
        self._convert = self._factor() #le digo a convert que la conversion tiene que ser en MB
        return self._convert * self._tot #Aqui devuelvo el resultado ya convertido 

    @property
    def user_free(self):
        self.unit = '%m' #indico que quiero el resultado en porcentaje de memoria libre en comparacion con su memoria total 
        self._convert = self._factor() #le digo a convert que la conversion tiene que ser en ese porcentaje
        return self._convert *(self._free) #Aqui devuelvo el resultado ya convertido 

    @property
    def mem_total(self):
        self.unit = 'GB' #Aqui especifico que quiero la memoria en GB
        self._convert = self._factor() #le digo a convert que la conversion tiene que ser en GB
        return self._convert *(self._memory_sys) #Aqui devuelvo el resultado ya convertido 
    
    @property
    def free_mem(self):
        self.unit = '%q' #indico que quiero el resultado en porcentaje de file system libre en comparacion con su total en el file system
        self._convert = self._factor() #le digo a convert que la conversion tiene que ser en ese porcentaje
        return self._convert *(self._free_sys) #Aqui devuelvo el resultado ya convertido 


class Spider:
    #Constructor de la clase
    #Param: el mailbox de rosado (envia solamente)
        # Su id que utiliza para crear su mailbox (recibe solamente)
        # El actual nodo donde se esta ejecutando
    #Autor: Carlos Urena
    def __init__(self,id_spider,act_node,luggage_name,sandbox_mailbox,spider_mailbox):
        self.request_fs_list = [] #cola donde se guardan las solicitudes de la maquina fisica segun lo leido en la maleta
        self.request_m_list = []  #cola donde se guardan las solicitudes del file system segun lo leido en la maleta

        self.actual_node = act_node
        self.id = id_spider
        #En estas 2 lineas se crean los mailboxes que se van a utilizar para la comunicacion
        self.request_mailbox = posix_ipc.MessageQueue(sandbox_mailbox) 
        time.sleep(0.2)
        self.answer_mailbox = posix_ipc.MessageQueue(spider_mailbox)

        #Instancio la clase que esta en la parte superior de este codigo fuente
        self.mem_informer = MemLinux()

        subprocess.call(['chmod', '0777', luggage_name]) #el ejecutable que acabo de armar le doy permisos
        #Direccion de la valija, open con permisos de read
        self.luggage = open(luggage_name,'r')
        self.luggage_name = luggage_name


    #Efecto: Se encarga de atender a las solicitudes de la maquina fisica y la escribe en la valija 
    #Param: El id de la solicitud especifica 
    #Autor: Carlos Urena
    def identify_request_machine(self,id):
        if id == 1:
            self.luggage.write("\nMemory Total: " + str(self.mem_informer.total)[:5] + 'MB')
        if id == 2:
            self.luggage.write("\nMemory Free: " + str(self.mem_informer.user_free)[:4] + '%')
        if id == 3:
            self.luggage.write("\nFile system total: " + str(self.mem_informer.mem_total)[:6] + 'GB')
        if id == 4:
            self.luggage.write("\nFile system Free: " + str(self.mem_informer.free_mem)[:4] + '%')

    #Efecto: Se encarga de atender a las solicitudes de los nodos y la escribe en la valija 
    #Param: El id de la solicitud especifica 
          # El paquete que tiene el dato que viene de parte de los nodos 
    #Autor: Carlos Urena 
    def identify_request_node(self,id,buffer):
        if id == 1:
            self.luggage.write("\nFW Table: ")
            row = buffer.split(';') #Este split se encarga de separar el string en filas(Mejor explicado en el documento imagen 1)
            for column in row:
                self.luggage.write("\n" + column)
        if id == 2:
            self.luggage.write("\nAG Neightbors: " + buffer)
        if id == 3:
            self.luggage.write("\nGraph Map: ")
            row = buffer.split(';')
            for column in row:
                self.luggage.write("\n" + column)
        if id == 4:
            self.luggage.write("\nSource to each source packets count: ")
            row = buffer.split(';')
            for column in row:
                self.luggage.write("\n" + column)
        if id == 5:
            self.luggage.write("\nTotal packages sent: ")
            row = buffer.split(';')
            for column in row:
                self.luggage.write("\n" + column)
        if id == 6:
            self.luggage.write("\nTotal packages received: " )
            row = buffer.split(';')
            for column in row:
                self.luggage.write("\n" + column)
        if id == 7:
            items = buffer.split(',')
            self.luggage.write("\nTotal package received from BC: " + items[0])
            self.luggage.write("\nTotal package received from FW: " + items[1])

    #Efecto: Lee Las primeras 2 lineas de la valija(luggage.txt) y guarda estas solicitudes en unas colas 
    #Autor: Carlos Urena
    def read_luggage(self):
        #Procedimiento de como se llenan estas colas mejor explicado en la imagen 2
        list_of_request = self.luggage.readlines() 
        self.request_fs_list = list_of_request[0].split(',')
        self.request_m_list = list_of_request[1].split(',')
        self.luggage.close()
        self.luggage = open(self.luggage_name,'a')

    #Efecto: Recorre las colas para atender las solicitudes que estan escritas alli
    #Autor: Carlos Urena
    def fill_luggage(self):
        #Logica explicada mejor en la imagen 3 del documento 
        self.luggage.write("\nNode id: " + self.actual_node+"----------------")
        while True:
            item = self.request_fs_list.pop(0)
            if item == '-\n':
                break
            else:
                self.identify_request_machine(int(item))
        
        while True:
            item = self.request_m_list.pop(0)
            if item == '-\n':
                break
            else:
                self.send_request(item)

       
       
        self.luggage.close()
        self.answer_mailbox.close()
        #Esta solitud indica que la spider ya acabo
        final_request = struct.pack("=2B",int(self.id),0)
        self.request_mailbox.send(final_request) #Request de terminar
        print("Termino la spider")
        exit()

    #Efecto: Se encarga de enviar la solicitud del mailbox y esperar la respuesta
    #Param: ID de la solitud especifica
    #Autor: Carlos Urena
    def send_request(self,id):
        request = struct.pack("=2B",int(self.id),int(id))
        self.request_mailbox.send(request) #Envio por el mailbox(spider emisor, rosado receptor)
        answer = self.answer_mailbox.receive() #Esperando respuesta mailbox(spider receptor, rosado emisor)
        self.identify_request_node(int(id),answer[0].decode())


def main(id_spider,act_node,luggage_name,sandbox_mailbox,spider_mailbox):
    spider = Spider(id_spider,act_node,luggage_name,sandbox_mailbox,spider_mailbox)
    spider.read_luggage()
    spider.fill_luggage()

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]) #Llamada al main con los parametros que vienen del exec




