import Sandbox 
import struct
import os

CHUNK_SIZE = 430

class StopAndWait:
    def __init__(self,id):
        self.sadnbox = 0
        self._in = 0
        self._out = 0
        self.entity = 0 

    def send_packages(self):
        lista = "1,2,3,4,-"
        packet = struct.pack("!2BHBH7s",6,0,4,29,7,lista.encode('UTF-8'))
        self._out.put(packet)
        exe_file = "../rose/spider"
        with open(exe_file, 'rb') as infile:
            while True:
                chunk = infile.read(CHUNK_SIZE)  #Lee la longitud de la constante CHUNK_SIZE para partir
                if not chunk: #indica cuando ya no hay mas bytes
                    print("Exe file chunked")
                    #os.remove(exe_file)
                    break
                packet = struct.pack("!2BHBH"+str(CHUNK_SIZE)+"s",6,1,4,29,CHUNK_SIZE,chunk)
                self._out.put(packet)
        luggage_file = "../rose/luggage1.txt"
        with open(luggage_file, 'rb') as infile:
            while True:
                chunk = infile.read(CHUNK_SIZE)  #Lee la longitud de la constante CHUNK_SIZE para partir
                if not chunk: #indica cuando ya no hay mas bytes
                    print("Luggage file chunked")
                    #os.remove(luggage_file)
                    break
                packet = struct.pack("!2BHBH"+str(CHUNK_SIZE)+"s",6,2,4,29,CHUNK_SIZE,chunk)
                self._out.put(packet)
        packet = struct.pack("!BH",255,4)
        self._out.put(packet)

        packet = self._in.get()
        packet = struct.pack("!2B",0,1)
        self._out.put(packet)
        while True:
            packet = self._in.get()
            #print("Llego paquete deconstruido")
            #print(packet)
           
            
    def little_test(self):
        packet = self._in.get()
        packet = struct.pack("!2B",0,1)
        self._out.put(packet)
        while True:
            packet = self._in.get()
            protocol = struct.pack("@B", packet[0])[0]
            if(protocol == 255):
                print("Se enviaron todos los paquetes")
            else:
                sand_packet_aux = struct.unpack("!H2BHBH",packet[:9])
                if(sand_packet_aux[2] == 2):
                    print("Llego paquete de luggage")
                    print(packet)
                else:
                    print("Llego paquete deconstruido")
           


    def set_channel(self,_in,_out,entity):
        print("Set channel S and W")
        self._in = _in
        self._out = _out 
        self.entity = entity

    def set_instances(self,sb):
        self.sadnbox = sb

