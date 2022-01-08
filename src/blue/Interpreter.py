import os
import sys
import struct
from log import Log
import shutil

BC_DEST = 65535

""" 
    Esta clase de encarga de interpretar e inprimir
    en la terminal los datos y aranas recibidas. 
 """

class Interpreter:
    def __init__(self, log):
        self.recv_luggage_id = 1
        self.log = log
    
    # Efectua: imprime en terminal los datos de un paquete de datos recibido. 
    # Param: 
        # pkt paquete de datos a ser impreso. 
    # Autor: Diego Murillo Porras B85526
    def print_data_packet(self, pkt):
        msg_header = struct.unpack( "!3H", pkt[1:7] )
        if(msg_header[1] == BC_DEST):
            new_msg = f"Tipo( Broadcast ) : Origen ( {msg_header[0]} ) : Numero de mensaje ( {msg_header[2]} ) :"
            print("\nSe ha recibido un mensaje: ", new_msg, pkt[9:].decode())
            self.log.log_event( 2, "recv_b<-g < BC >" + pkt[9:].decode() )
        else:
            new_msg = f"Tipo( Forward ) : Origen( {msg_header[0]} ) : Numero de mensaje ( {msg_header[2]} ) :"
            print("\nSe ha recibido un mensaje: ", new_msg, pkt[9:].decode() )
            self.log.log_event( 2, "recv_b<-g < FW >" + pkt[9:].decode() )

    # Efectua: interpreta e imprime los datos de una valija recibida. 
    # Autor: Diego Murillo Porras B85526
    def print_spider_luggage(self, pkt):
        shutil.move("../green/"+pkt[1:].decode('utf-8'), f"luggage_received/luggage{self.recv_luggage_id}.txt")
        luggage = open(f"luggage_received/luggage{self.recv_luggage_id}.txt")
        print()     
        print("Received a spider: ")
        line = luggage.readline()
        while line:
            while line[:4] == "Node":
                print()
                print("\t" + line)
                line = luggage.readline()
                while line and line[:4] != "Node":
                    print("\t\t- " + line, end= "")
                    if(line[:2] == "FW"):
                        self.print_fw_table(luggage)
                    if(line[:6] == "Source"):
                        self.print_source_pkt(luggage)
                    if(line[15:23] == "received"):
                        self.print_received_pkt(luggage)
                    if(line[15:19   ] == "sent"):
                        self.print_sent_pkt(luggage) 
                    if(line[:4] == "Graf"):
                        self.print_graf_map(luggage)
                    line = luggage.readline()
            line = luggage.readline()
        print()
        print("\nProseguida con el menu: ", end="")
        self.recv_luggage_id += 1

    # Efectua: imprime datos de la tabla forwarding en la valija. 
    # Autor: Diego Murillo Porras B85526
    def print_fw_table(self, luggage):
        line = luggage.readline()
        if line[0] != "-":
            print( "\t\t\tDestiny\t| Root" )
        else:
            print("\t\t\tNON")
        while( line[0] != "-" ):
            print( "\t\t\t", end = "" )
            for x in line:
                if x == ",":
                    print("\t| ", end = "")
                else:
                    print(x, end="")
            line = luggage.readline()

    # Efectua: imprime datos de la  cantidad de paquetes recibidos de un nodo en la valija. 
    # Autor: Diego Murillo Porras B85526
    def print_received_pkt(self, luggage):
        line = luggage.readline()
        if line[0] != "-":
            print( "\t\t\tOrigin\t| Cant" )
        else:
            print("\t\t\tNON")
        while( line[0] != "-" ):
            print( "\t\t\t", end = "" )
            for x in line:
                if x == ",":
                    print("\t| ", end = "")
                else:
                    print(x, end="")
            line = luggage.readline()

    # Efectua: imprime datos de la cantidad de paquetes enviados de un nodo en la valija. 
    # Autor: Diego Murillo Porras B85526
    def print_sent_pkt(self, luggage):
        line = luggage.readline()
        if line[0] != "-":
            print( "\t\t\tDestiny\t| Cant" )
        else:
            print("\t\t\tNON")
        while( line[0] != "-" ):
            print( "\t\t\t", end = "" )
            for x in line:
                if x == ",":
                    print("\t| ", end = "")
                else:
                    print(x, end="")
            line = luggage.readline()

    # Efectua: imprime datos de la cantidad de paquetes de cada fuente de un dado nodo.  
    # Autor: Diego Murillo Porras B85526
    def print_source_pkt(self, luggage):
        line = luggage.readline()
        if line[0] != "-":
            print( "\t\t\tSource\t| Cant" )
        else:
            print("\t\t\tNON")
        while( line[0] != "-" ):
            print( "\t\t\t", end = "" )
            for x in line:
                if x == ",":
                    print("\t| ", end = "")
                else:
                    print(x, end="")
            line = luggage.readline()

    # Efectua: imprime datos de el grafo de un dado nodo. 
    # Autor: Diego Murillo Porras B85526
    def print_graf_map(self, luggage):    
        line = luggage.readline()
        if line[0] != "-":
                print( "\t\t\tNeighbor| Adjacencies" )
        else:   
            print("\t\t\tNON")
        while( line[0] != "-" ):
            print( "\t\t\t", end = "" )
            first = True
            for x in line:
                if x == "," and first:
                    print("\t| ", end = "")
                    first = False
                else:
                    print(x, end="")
            line = luggage.readline()

    # Efectua: interpresta una hilera en numeros. 
    # Autor: Diego Murillo Porras B85526
    def read_line_numbers(self, line):
        numbers = []
        str_number = ""
        for x in line:
            if x == ';':
                number = int(str_number)
                numbers.append(number)
                str_number = ""
            elif not x == '-':
                str_number += x
        return numbers

  