import time 
import struct
BC_DEST = 65535

""" 
    Esta clase se encarga de interuactuar con el usuario para pedir los datos o arnas a enviar. 
 """

class Interface:
    def __init__(self, log):
        self.log = log
        self.gA = 0
        self.msg_id = 1
        self.spd_builder = 0
    
    # Efectua: inicializa las instancias de las otras clases.
    # Param: 
    #   gA objeto de clase GreenAgent.
    #   spd_builder objeto de la clase Spiderbuilder 
    # Autor: Diego Murillo Porras B85526
    def set_instances(self, gA, spd_builder):
        self.gA = gA
        self.spd_builder = spd_builder
    
    # Efectua: inicializa el menu de la interfaz. 
    # Autor: Diego Murillo Porras B85526
    def run(self):
        run = True
        while(run):
            try:
                choice = int(input("\n1. Enviar mensaje\n2. Enviar Araña\n3. Terminar programa.\nIngrese numero acorde a las opciones: "))
                if choice == 1: # Mensaje
                    self.msg_pkt()
                elif choice == 2: # Envio de araña
                    self.spider_pkt()
                elif choice == 3:
                    run = False
                    print("PROGRAM EXITS.")
                else:
                    raise(ValueError)
            except ValueError:  
                print("INVALID CHOICE.")

    # Efectua: menu para enviar un paquete de datos. 
    # Autor: Diego Murillo Porras B85526
    def msg_pkt(self):
        msg = input( "\nIngrese el mensaje a enviar: ")
        msg_len = len( msg )
        if msg_len > 200:
            print("MESSAGE CAN NOT EXCEED 200 CHARACTERS.")
            return 
        try:
            choice = int(input("\n1. Mensaje Forward.\n2. Mensaje Broadcast\nIngrese numero acorde a las opciones: "))
            if choice == 1: # Mensaje de forwarding. 
                try:
                    destino = int(input( "\nIngrese el destino del mensaje: "))
                    self.data_pkt_send(0, destino, msg)
                except ValueError:
                    print("INVALID DESTINATION.")
            elif choice == 2: # Mensaje de broadcast.
                self.data_pkt_send(1, BC_DEST, msg)
                pass
            else:
                raise(ValueError)
        except ValueError:
            print("INVALID CHOICE.")
    
    # Efectua: menu para enviar paquete de datos. 
    # Autor: Diego Murillo Porras B85526
    def data_pkt_send(self, protocol, destino, msg):
        format_str = '!B3H%ds' % len(msg)
        packet = struct.pack(format_str, protocol, destino, self.msg_id, 0, msg.encode() )
        self.gA.green_send_queue.put(packet)
        print("\nMessage sent successful.")
    
    # Efectua: menu para enviar paqeute arana. 
    # Autor: Diego Murillo Porras B85526
    def spider_pkt(self):
        request = ([],[],[])
        try:
            choices = input("\nIngrese destinos separados por espacios: ").split()
            for x in choices :
                r = int(x)
                if r in request[0]:
                    raise(ValueError)
                request[0].append(r)
            print("\n1. Memoria total (MB).")
            print("2. Memoria libre(%).")
            print("3. Espacio total en el File System (GB).")
            print("4. Espacio libre en el File System (%).")
            choices = input("Ingrese pedidos de maquina fisica separados por espacios: ").split()
            for x in choices :
                r = int(x)
                if r < 1 or r > 4:
                    raise(ValueError)
                if r in request[1]:
                    raise(ValueError)
                request[1].append(r)
            print("\n1. Tablas de forwarding. (Verde) ")
            print("2. Lista por nodo de vecinos en AG. (Verde)")
            print("3. Mapa del grafo. (Rosado)")
            print("4. Cantidad de paquetes recibidos desde fuente, para cada fuente.")
            print("5. Cantidad de paquetes enviados a través de cada vecino.")
            print("6. Cantidad de paquetes recibidos desde cada vecino.")
            print("7. Cantidad de paquetes recibidos por broadcast y por enrutamiento.")
            choices = input ("Ingrese pedidos separados por espacios: ").split()
            for x in choices:
                r = int(x)
                if r < 1 or r > 7:
                    raise(ValueError)
                if r in request[2]:
                    raise(ValueError)
                request[2].append(r)
            self.spd_builder.request_queue.put(request)
            print("\nSpider sent successful.")
        except ValueError:
            print("INVALID REQUEST OR REPETED REQUEST.")
