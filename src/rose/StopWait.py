from datetime import datetime
from threading import *
import queue
import SWConnection # SWSender, SWReceiver
import struct # unpack()
import time # sleep()

SENDER = 0
RECEIVER = 1
AVAILABLE = 0
UNAVAILABLE = 1
PROCESSING = 2
SYN = 128 # 10000000
SYNACK = 192 # 11000000
ACK = 64 # 01000000
FIN = 32 # 00100000

class StopWait:
    def __init__( self, node_id, green_agent, bitacora ):
        self.node_id = int(node_id) # ID del nodo
        self.green_agent = green_agent # referencia a agente de comunicacion
        self.bitacora = bitacora
        self.sw_queue = queue.Queue() # cola para paquetes de entrada
        self.connection_keys = {} # numeros de conexion y disponibilidad
        self.connection_by_key = {} # asocia numero con instancia conexion
        self.init_connection_keys() # incializa dicc. connection_by_key
        self.key_tuples_used = [] # se almacenan las tuplas usadas como llave
        self.connection_by_id = {} # asocia ID con conexion
        self.entities = {} # asocia codigo entidad con sus colas IN y OUT
        self.threads = [Thread( target=self.sw_queue_listen, args=() )]
    
    def thread_init( self ):
        for t in self.threads:
            t.start()
    
    def __del__( self ):
        for t in self.threads:
            t.join()

    def init_connection_keys( self ):
        for i in range(256):
            self.connection_keys[i] = AVAILABLE

    def recv( self, packet ):
        self.sw_queue.put( packet )

    """
    Efecto: Se encarga de iniciar el proceso de levantamiento de una
            conexion, sea como emisor o receptor.
    Requiere: (entity) entidad que solicita inicio de conexion.
              (role) indica el rol (emisor o receptor) de este lado de
              la conexion.
              (node) numero de nodo objetivo (el otro nodo de la conexion).
              (syn)(opcional) paquete SYN de 3Way-H, solo se usa este
              parametro cuando se levanta conexion como receptor.
              (id)(opcional) id (que asigno la entidad) de la conexion.
    Modifica: (connection_keys) se asigna una llave de conexion.
              (connection_by_key) se asocia una instancia SWConnection
              con la llave asignada.
    Retorna: (sw_connection) instancia de la conexion si se logra establecer
             conexion.
             (None) si no se logra establecer conexion.
    Autor: Roy Rojas.
    """
    def init_connection( self, entity, role, node, syn=0, conn_id=0 ):
        my_conn_key = self.get_conn_key( role )
        # si la entidad ya esta registrada
        if entity in self.entities and my_conn_key != -1:
            if role == SENDER:
                sw_connection = SWConnection.SWSender( self, self.node_id,
                        node, self.green_agent, entity, my_conn_key, conn_id )
            elif role == RECEIVER:
                out_queue = self.entities[entity][1]
                sw_connection = SWConnection.SWReceiver( self, self.node_id,
                        node, self.green_agent, entity, out_queue, my_conn_key )
                # se le pasa paquete SYN
                sw_connection.recv( syn )
            self.connection_by_key[my_conn_key] = sw_connection
            if sw_connection.init_connection():
                print("SE ESTABLECIO CONEXION")
                self.bitacora.write( '['+str(datetime.now())+'] '+"Case 0 <SW>"+
                        "Ephemeral connection established\n" )
                self.connection_keys[my_conn_key] = UNAVAILABLE
                # se actualiza la llave de conexion
                self.update_conn_key( my_conn_key )
                return sw_connection
            else:
                print("NO SE PUDO ESTABLECER CONEXION")
                # se declara como disponible y se remueve conexion
                self.connection_keys[my_conn_key] = AVAILABLE
                del self.connection_by_key[my_conn_key]
                self.bitacora.write( '['+str(datetime.now())+'] '+"Case 3 <SW>"+
                        " Ephemeral connection not established due to not"+
                        " completion of 3WayHandshake\n" )
        return None
    
    """
    Efecto: Escucha a la cola de entrada del multiplexor.
            Despacha los paquetes segun corresponda, ya sea para iniciar
            una nueva conexion o a una conexion ya existente.
    Requiere: Conexion establecida.
    Modifica: (sw_queue) extrae los paquetes de esa cola.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def sw_queue_listen( self ):
        while( True ):
            packet = self.sw_queue.get( block=True )
            data = SWConnection.packet_deconstruct( packet )
            flags = data[4]
            if flags == SYN: # se desea establecer nueva conexion
                entity = data[7]
                origin_node = data[6]
                # se levanta hilo para atender conexion entrante
                Thread( target=self.init_connection, args=(entity, RECEIVER,
                        origin_node, packet) ).start()
            else:
                if flags == SYNACK:
                    conn_key = data[0]
                elif flags == ACK:
                    conn_key = data[1]
                else:
                    conn_key = (data[0], data[1])
                try:
                    self.connection_by_key[conn_key].recv( packet )
                except:
                    if flags == ACK:
                        conn_key = (data[0], data[1])
                        self.connection_by_key[conn_key].recv( packet )
                    pass # se bota el paquete
                    print("SE BOTA PAQUETE")
    
    """
    Efecto: Escucha a la cola IN de una entidad especifica.
    Requiere: Entidad correctamente registrada.
              (entity) id de entidad.
              (queue) cola IN.
    Modifica: (queue) extra paquetes de esa cola IN.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def in_queue_listen( self, entity, queue ):
        while( True ):
            packet = queue.get( block=True )
            packet_id = struct.unpack( "!H", packet[:2] )[0]
            if packet_id in self.connection_by_id:
                # se pasa paquete a conexion correspondiente
                self.connection_by_id[packet_id].send( packet[2:] )
            elif packet_id == 0: # se desea establecer conexion
                target, connection_id = struct.unpack( "!HH", packet[2:6] )
                # se levanta hilo para establecer conexion solicitada
                Thread( target=self.establish_connection, args=(entity,
                        target, connection_id) ).start()
            elif packet_id == 255: # se desea cerrar conexion
                print("Se envia FIN")
                packet_id = struct.unpack( "!H", packet[2:4] )[0]
                self.connection_by_id[packet_id].send( None, FIN )
    
    """
    Efecto: Se intenta registrar una entidad que requiera comunicacion
            confiable.
    Requiere: (inq) cola IN de entrada de paquetes a multiplexor.
              (outq) cola OUT para depositar paquetes hacia la entidad.
              (entity_code) numero con el que se identificara esa entidad.
    Modifica: (entities) diccionario que asocia IDs de entidades con sus
              colas IN y OUT.
              (threads) lista de hilos en ejecucion.
    Retorna: (1) si se pudo registrar la entidad.
             (0) si no se pudo registrar la entidad.
    Autor: Roy Rojas.
    """
    def set_channel( self, inq, outq, entity_code ):
        if len( self.connection_by_key ) < 256: # si hay espacio
            if entity_code not in self.entities:
                self.entities[entity_code] = (inq, outq)
                new_thread = Thread( target=self.in_queue_listen,
                        args=(entity_code, inq) )
                self.threads.append( new_thread )
                new_thread.start()
                self.bitacora.write( '['+str(datetime.now())+'] '+"Case 0 <SW>"+
                        " Entity registered succesfully\n" )
                return 1 # se establece el canal
        self.bitacora.write( '['+str(datetime.now())+'] '+"Case 3 <SW>"+
                " Cannot register entity\n" )
        return 0 # se deniega el canal
    
    """
    Efecto: Se procesa el levantamiento de una conexion emisora.
    Requiere: (entity) numero de entidad.
              (target) numero de nodo objetivo.
              (conn_id) id que asigna la entidad a esta conexion.
    Modifica: (connection_by_id) se asociaria la conexion levantada
              con el ID que le asigno la entidad.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def establish_connection( self, entity, target, conn_id ):
        if conn_id not in self.connection_by_id:
            sw_connection = self.init_connection( entity, SENDER, target,
                    conn_id=conn_id )
            if sw_connection != None:
                self.connection_by_id[conn_id] = sw_connection
                # se reporta conexion establecida
                response = struct.pack( "BB", 0, 1 )
                self.entities[entity][1].put( response )
            else:
                response = struct.pack( "BB", 0, 0 )
                self.entities[entity][1].put( response )
        else:
            print("ID conexion existente")
            # se reporta conexion no establecida
            response = struct.pack( "BB", 0, 0 )
            self.entities[entity][1].put( response )
            self.bitacora.write( '['+str(datetime.now())+'] '+"Case 3 <SW>"+
                    " Existent connection ID, cannot establish connection\n" )

    """
    Efecto: Se consigue una llave/numero de conexion disponible.
    Requiere: (role) el rol (emisor o receptor) d la conexion.
    Modifica: (connection_keys) se reserva una llave.
    Retorna: (i) numero de conexion tomado.
             (-1) si no se obtuvo numero de conexion disponible.
    Autor: Roy Rojas.
    """
    def get_conn_key( self, role ):
        for i in range(256):
            if self.connection_keys[i] == AVAILABLE:
                if all( [i != t[role] for t in self.key_tuples_used] ):
                    self.connection_keys[i] = PROCESSING
                    return i
        return -1 # no se encontro llave disponible
    
    """
    Efecto: Se actualiza llave de conexion.
    Requiere: (conn_key) llave de conexion actual.
    Modifica: (connection_by_key) se remueve la llave antigua y se
              actualiza para que ahora la conexion se referencie por
              los numeros de conexion que obtuvieron ambos lados, o sea,
              la llave se compone del numero de emisor y receptor (como tupla).
              (key_tuples_used) se agrega una nueva tupla que esta siendo
              usada como llave de conexion actualmente.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def update_conn_key( self, conn_key ):
        # se guarda la instancia de la conexion
        sw_instance = self.connection_by_key[conn_key]
        del self.connection_by_key[conn_key]
        # se genera el nuevo identificador de conexion
        new_conn_key = (sw_instance.sconn_num, sw_instance.rconn_num)
        self.connection_by_key[new_conn_key] = sw_instance
        self.key_tuples_used.append( new_conn_key )
    
    """
    Efecto: Se cierra una conexion efimera.
    Requiere: Conexion actualmente abierta.
              (conn_key) llave de la conexion a cerrar.
              (role) el rol que se ejecuta a este lado de la conexion.
              (id)(opcional) ID de la conexion que asigno la entidad
              a esta conexion.
    Modifica: (connection_by_key) se elimina la entrada de la conexion.
              (key_tuples_used) se elimina la tupla que se estaba usando
              para esa conexion.
              (connection_keys) se libera el numero de conexion que estaba
              siendo usado de este lado de la conexion.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def close_connection( self, conn_key, role, conn_id=0 ):
        time.sleep(1) # esta espera es para botar paquetes retrasados
        del self.connection_by_key[conn_key]
        self.key_tuples_used.remove( conn_key )
        if role == SENDER:
            del self.connection_by_id[conn_id]
            self.connection_keys[conn_key[0]] = AVAILABLE
            self.bitacora.write( '['+str(datetime.now())+'] '+"Case 0 <SW>"+
                    " Connection as sender closed correctly\n" )
        elif role == RECEIVER:
            self.connection_keys[conn_key[1]] = AVAILABLE
            self.bitacora.write( '['+str(datetime.now())+'] '+"Case 0 <SW>"+
                    " Connection as receiver closed correctly\n" )