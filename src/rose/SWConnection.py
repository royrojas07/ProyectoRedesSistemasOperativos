from threading import *
import queue
import struct # pack(), unpack()

SENDER = 0
RECEIVER = 1
SYN = 128 # 10000000
SYNACK = 192 # 11000000
ACK = 64 # 01000000
FIN = 32 # 00100000
FINACK = 96 # 01100000
    
class SWSender:
    def __init__( self, mplexer, node, target_node, green_agent, entity,
            sconn_num=0, conn_id=0 ):
        self.multiplexer = mplexer # referencia al multiplexor
        self.node = node
        self.target = target_node
        self.green_agent = green_agent # referencia a agente de comunicacion
        self.entity = entity
        self.sn = 0
        self.conn_id = conn_id # id que identifica la conexion del emisor
        self.sconn_num = sconn_num # identificador de conexion stop/wait en origen
        self.rconn_num = 0 # identificador de conexion stop/wait en destino
        self.i_packet_queue = queue.Queue() # cola para paquetes de entrada
        self.o_packet_queue = queue.Queue() # cola para paquetes de salida
        self.thread = Thread( target=self.sw_sender, args=() )
    
    def thread_init( self ):
        self.thread.start()

    """
    Efecto: Se inicia el 3-way handshake para establecer conexion.
            Si se completa con exito entonces se levanta hilo que
            maneja conexion efimera.
    Requiere: No aplica.
    Modifica: No aplica.
    Retorna: (connected) un entero, 0 si no se pudo establecer conexion.
             1 si se establecio conexion.
    Autor: Roy Rojas.
    """
    def init_connection( self ):
        connected = self.three_way_handshake()
        if connected:
            self.thread_init()
        return connected

    """
    Efecto: Metodo usado por multiplexor para depositar paquetes
            que deden ser enviados.
    Requiere: Conexion establecida exitosamente.
              (packet) paquete binario a ser enviado.
              (flags) byte que representa las banderas del paquete.
    Modifica: (o_packet_queue) se depositan paquetes en esta cola.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def send( self, packet, flags=0 ):
        self.o_packet_queue.put( (packet, flags) )
    
    def recv( self, packet ):
        self.i_packet_queue.put( packet )
    
    """
    Efecto: Se desenvuelve el funcionamiento del protocol Stop/Wait
            como agente enviador.
            Se reciben paquetes de capa superior.
            Se empaquetan y se envian al agente verde.
    Requiere: Conexion establecida.
    Modifica: (o_packet_queue) se toman los paquetes que son depositados
              en esa cola.
              (sn) se incrementa sn cuando se reciben acks.
    Retorna: 0 si se cierra conexion.
    Autor: Roy Rojas.
    """
    def sw_sender( self ):
        twh_ack_sent = False
        while( True ):
            max_timeouts = 10 # cantidad maxima de timeouts
            ack = False
            packet, flags = self.o_packet_queue.get( block=True )
            sw_packet = self.packet_construct( packet, flags )
            if not twh_ack_sent: # si no se ha enviado ack de three-way
                sw_packet = self.packet_construct( packet, ACK )
                twh_ack_sent = True
            # se envia el paquete
            self.green_agent.green_send_store( sw_packet )
            while not ack: # mientras no haya recibido ack
                try:
                    packet = self.i_packet_queue.get( timeout=0.7 )
                    data = packet_deconstruct( packet )
                    flags = data[4]
                    rn = data[3]
                    # revisa que RN == SN+1
                    if flags == 0 and rn == ((self.sn+1) % 256):
                        self.sn = rn # actualiza el SN
                        ack = True
                    elif flags == FINACK:
                        self.multiplexer.close_connection( (self.sconn_num,
                                self.rconn_num), SENDER, self.conn_id )
                        print("recibo finack, buen cierre de conexion")
                        return 0 # se cierra conexion
                except queue.Empty:
                    # si es posible, volver a enviar el paquete
                    if max_timeouts > 0:
                        self.green_agent.green_send_store( sw_packet )
                        max_timeouts -= 1
                    else:
                        self.multiplexer.close_connection( (self.sconn_num,
                                self.rconn_num), SENDER, self.conn_id )
                        print("sender pierde conexion")
                        return 0 # se cierra conexion
    
    """
    Efecto: Se construye paquete de 3-way/2-way handshake, ack o de datos.
    Requiere: (packet) arreglo de bytes con datos a ser enviados.
              (flags) byte con banderas que llevaria el paquete.
    Modifica: No aplica.
    Retorna: (sw_packet) paquete de stop/wait formado.
    Autor: Roy Rojas.
    """
    def packet_construct( self, packet, flags ):
        protocol = 5
        p_len = 0
        if packet != None: # si hay payload
            p_len = len( packet )
            # se arma un paquete de datos
            pack_format = "!B2H6BH%ds" % p_len
            sw_packet = struct.pack( pack_format, protocol, self.node,
                    self.target, self.sconn_num, self.rconn_num, self.sn,
                        0, flags, self.entity, p_len, packet )
        else:
            pack_format = "!B2H6BH"
            sw_packet = struct.pack( pack_format, protocol, self.node,
                    self.target, self.sconn_num, self.rconn_num, self.sn,
                        0, flags, self.entity, p_len )
        return sw_packet
    
    """
    Efecto: Se lleva a cabo 3-way handshake desde el lado del emisor.
    Requiere: No aplica.
    Modifica: (rconn_num) se guarda el numero de conexion del receptor.
              (i_packet_queue) se extraen los paquetes que son depositados
              en esa cola.
    Retorna: (1) si se pudo establecer conexion.
             (0) si no se pudo establecer conexion.
    Autor: Roy Rojas.
    """
    def three_way_handshake( self ):
        synack = False
        max_timeouts = 10 # cantidad maxima de timeouts
        
        syn_packet = self.packet_construct( None, SYN )
        self.green_agent.green_send_store( syn_packet ) # se envia syn
        while not synack: # mientras no se reciba synack
            try:
                packet = self.i_packet_queue.get( timeout=0.7 )
                data = packet_deconstruct( packet )
                data_flags = data[4]
                sconn = data[0]
                # si synack valido y conexion emisor correcta
                if data_flags == SYNACK and sconn == self.sconn_num:
                    # se guarda el numero de conexion de receptor
                    self.rconn_num = data[1]
                    synack = True
            except queue.Empty:
                if max_timeouts > 0: # si aun se puede reenviar
                    print("REENVIO SYN")
                    self.green_agent.green_send_store( syn_packet )
                    max_timeouts -= 1
                else: # no se pudo establecer conexion
                    return 0
        return 1 # se pudo establecer conexion

class SWReceiver:
    def __init__( self, mplexer, node, target_node, green_agent, entity,
            out_queue, rconn_num=0 ):
        self.multiplexer = mplexer # referencia al multiplexor
        self.node = node
        self.target = target_node
        self.green_agent = green_agent # referencia a agente de comunicacion
        self.entity = entity
        self.rn = 0
        self.sconn_num = 0 # identificador de conexion SW en origen
        self.rconn_num = rconn_num # identificador de conexion SW en destino
        self.i_packet_queue = queue.Queue() # cola para paquetes de entrada
        self.out_queue = out_queue # cola para entregar paquetes a entidad
        self.thread = Thread( target=self.sw_receiver, args=() )
    
    def thread_init( self ):
        self.thread.start()

    """
    Efecto: Se inicia el 3-way handshake para establecer conexion.
            Si se completa con exito entonces se levanta hilo que
            maneja conexion efimera.
    Requiere: No aplica.
    Modifica: No aplica.
    Retorna: (connected) un entero, 0 si no se pudo establecer conexion.
             1 si se establecio conexion.
    Autor: Roy Rojas.
    """
    def init_connection( self ):
        connected = self.three_way_handshake()
        if connected:
            self.thread_init()
        return connected
    
    """
    Efecto: Metodo usado por multiplexor para hacer llegar paquetes que
            van dirigidos a esta conexion.
    Requiere: (packet) paquete binario de llegada.
    Modifica: (i_packet_queue) se depositan los paquetes en esta cola.
    Retorna: No aplica.
    Autor: Roy Rojas.
    """
    def recv( self, packet ):
        self.i_packet_queue.put( packet )
    
    """
    Efecto: Se desenvuelve el funcionamiento del protocol Stop/Wait
            como agente receptor.
            Se reciben paquetes de capa inferior.
            Se desempaquetan y son enviados a la funcionalidad correspondiente.
    Requiere: Conexion establecida.
    Modifica: (i_packet_queue) se toman los paquetes que son depositados
              en esa cola.
              (rn) se incrementa rn cuando se reciben paquetes con sn esperado.
    Retorna: 0 si se cierra conexion.
    Autor: Roy Rojas.
    """
    def sw_receiver( self ):
        while( True ):
            try:
                packet = self.i_packet_queue.get( timeout=2 )
                data = packet_deconstruct( packet )
                payload = data[5]
                sn = data[2]
                flags = data[4]
                if sn == self.rn and flags == 0:
                    self.rn = (self.rn+1) % 256 # se actualiza RN
                    # pasa payload a entidad (capa superior)
                    self.out_queue.put( payload )
                elif flags == FIN: # se quiere cerrar la conexion
                    finack_packet = self.packet_construct( None, FINACK )
                    self.green_agent.green_send_store( finack_packet )
                    self.multiplexer.close_connection( (self.sconn_num,
                            self.rconn_num), RECEIVER )
                    print("se manda finack, buen cierre de conexion")
                    return 0 # se cierra conexion
                # construye y envia ACK
                ack = self.packet_construct( None, 0 )
                self.green_agent.green_send_store( ack )
            except queue.Empty: # se cierra conexion por inactividad
                self.multiplexer.close_connection( (self.sconn_num,
                        self.rconn_num), RECEIVER )
                print("receiver cierra conexion por inactividad")
                return 0
    
    """
    Efecto: Se construye paquete de 3-way/2-way handshake, ack o de datos.
    Requiere: (packet) arreglo de bytes con datos a ser enviados.
              (flags) byte con banderas que llevaria el paquete.
    Modifica: No aplica.
    Retorna: (sw_packet) paquete de stop/wait formado.
    Autor: Roy Rojas.
    """
    def packet_construct( self, packet, flags ):
        protocol = 5
        p_len = 0
        if packet != None: # si hay payload
            p_len = len( packet )
            # se arma el paquete de datos
            pack_format = "!B2H6BH%ds" % p_len
            sw_packet = struct.pack( pack_format, protocol, self.node,
                    self.target, self.sconn_num, self.rconn_num, 0,
                        self.rn, flags, self.entity, p_len, packet )
        else:
            # se arma el paquete ack o de 3-way handshake
            pack_format = "!B2H6BH"
            sw_packet = struct.pack( pack_format, protocol, self.node,
                    self.target, self.sconn_num, self.rconn_num, 0,
                        self.rn, flags, self.entity, p_len )
        return sw_packet

    """
    Efecto: Se lleva a cabo 3-way handshake desde el lado del receptor.
    Requiere: No aplica.
    Modifica: (sconn_num) se guarda el numero de conexion del emisor.
              (i_packet_queue) se toman los paquetes que son depositados
              en esa cola.
    Retorna: (1) si se pudo establecer conexion.
             (0) si no se pudo establecer conexion..
    Autor: Roy Rojas.
    """
    def three_way_handshake( self ):
        ack = False
        max_timeouts = 10 # cantidad maxima de timeouts
        
        # se extrae el paquete de SYN
        packet = self.i_packet_queue.get( block=True )
        data = packet_deconstruct( packet )
        sconn = data[0]
        flags = data[4]
        if flags == SYN:
            # se define el numero de conexion del sender
            self.sconn_num = sconn

        synack_packet = self.packet_construct( None, SYNACK )
        self.green_agent.green_send_store( synack_packet ) # se envia synack
        while not ack:
            try:
                packet = self.i_packet_queue.get( timeout=2 )
                data = packet_deconstruct( packet )
                data_flags = data[4]
                rconn = data[1]
                if data_flags == ACK and rconn == self.rconn_num:
                    ack = True
                    # se construye paquete con payload recibido
                    packet = self.packet_construct( data[5], 0 )
                    self.recv( packet )
            except queue.Empty:
                if max_timeouts > 0: # si aun se puede reenviar
                    print("REENVIO SYNACK")
                    self.green_agent.green_send_store( synack_packet )
                    max_timeouts -= 1
                else: # no se pudo establecer conexion
                    return 0
        return 1 # se pudo establecer conexion

"""
Efecto: Se deconstruye paquete.
Requiere: (packet) paquete a ser decontruido.
Modifica: No aplica.
Retorna: Tupla con valores importantes del paquete Stop/Wait.
            Numero de conexion de enviador, del receptor, SN, RN,
            banderas y payload.
Autor: Roy Rojas.
"""
def packet_deconstruct( packet ):
    origin_node = struct.unpack( "!H", packet[1:3] )[0]
    sconn = struct.unpack( "B", packet[5:6] )[0]
    rconn = struct.unpack( "B", packet[6:7] )[0]
    sn = struct.unpack( "B", packet[7:8] )[0]
    rn = struct.unpack( "B", packet[8:9] )[0]
    flags = struct.unpack( "B", packet[9:10] )[0]
    entity = struct.unpack( "B", packet[10:11] )[0]
    payload_len = struct.unpack( "!H", packet[11:13] )[0]
    payload = packet[13:13+payload_len]
    return sconn, rconn, sn, rn, flags, payload, origin_node, entity