import os #open() close() 
import time #sleep() asi en los while True no tenemos la compu sobrecargada esperando
import csv #used to read csv files
from datetime import datetime
import sys

#esta es la direccion en donde se encuentra el fifo con el que hacemos el pipe nombrado  #
ORANGE_SND_PP = "orange_snd_pp" + sys.argv[1]
ORANGE_RCV_PP = "orange_rcv_pp" + sys.argv[1]

MY_DATA_REQUEST = '1'
NEIGHBOR_REQUEST = '2'

bitacora = open("log/orange_logs/orange_log"+ sys.argv[1]+".txt","w+")

#efecto: Se mantiene escuchando al verde hasta que este mande un msg
def listen_green(par_receiving_pipe):
	data = os.read(par_receiving_pipe ,16)
	data = data.decode("utf-8") #esto se hace por el read lo lee en formato de bytes y lo queremos en str
	bitacora.write('[' + str(datetime.now()) + '] ' + "Case 2 " + data + "  Orange  recv_g->o \n" )
	return data
		
#efecto: busca el archivo con los datos que desea el nodo verde
#@param: que numero de archivo csv es y que tipo de solicitud es
def file_searching(par_file, par_type_request,par_receiving_pipe,par_sending_pipe):
	if(par_type_request == MY_DATA_REQUEST):
		total_csv = "../../data/verde" + par_file + "/mis_datos" + par_file + ".csv"
		try:
			csv_file = open(total_csv)
			bitacora.write('[' + str(datetime.now()) + '] ' + "Case  0  Orange  " + total_csv + " open sucessfully\n" )
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				send_to_green(cast_list_to_string(row),par_type_request,par_sending_pipe)
			csv_file.close()
		except IOError:
			bitacora.write('[' + str(datetime.now()) + '] ' + "Case  3  Orange  err_open " + total_csv + "\n" )
	
	if(par_type_request == NEIGHBOR_REQUEST):
		nb_count = 0
		total_csv = "../../data/verde" + par_file + "/vecinos" + par_file + ".csv"
		try:
			csv_file = open(total_csv)
			bitacora.write('[' + str(datetime.now()) + '] ' + "Case  0  Orange  " + total_csv + " open sucessfully for neighbors count\n" )
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader: #este for es para contar las lineas en el archivo vecinos con el fin de saber cuantos hay
				if not(row == []): #para evacuar el error de los espacios en blanco en los csv 
					nb_count += 1
			send_to_green(str(nb_count),'0',par_sending_pipe) #aqui se le envia la cantidad de vecinos al verde para que prepare lo necesario
			csv_file.close()
		except IOError:
			bitacora.write('[' + str(datetime.now()) + '] ' + "Case  3  Orange  err_open " + total_csv + "\n" )
		
		try:
			#aqui tuve que volver a abrir el csv porque si no, no podia volver a recorrer el for 
			csv_file = open(total_csv)
			bitacora.write('[' + str(datetime.now()) + '] ' + "Case  0  Orange  " + total_csv + " open sucessfully for send neighbors\n" )
			csv_reader = csv.reader(csv_file, delimiter=',')
			listen_green(par_receiving_pipe)
			for row in csv_reader:
				if not(row == []): #para evacuar el error de los espacios en blanco en los csv 
					send_to_green(cast_list_to_string(row),par_type_request,par_sending_pipe) #qui le mando linea por linea los vecinos al verde
					listen_green(par_receiving_pipe)#hago un listen green esperando que el me devuelva respuesta con el fin de sincronizar procesos 
				else:
					bitacora.write('[' + str(datetime.now()) + '] ' + "Case  3  Orange  err_reading  blank space\n" )
			csv_file.close()
		except IOError:
			bitacora.write('[' + str(datetime.now()) + '] ' + "Case  3  Orange  err_open " + total_csv + "\n" )
		bitacora.write('[' + str(datetime.now()) + '] ' + "Case  0 Orange  Finished\n" )
		bitacora.close()
		os.close(par_receiving_pipe)
		os.close(par_sending_pipe)
		exit() #de forma brusca se mata al naranja despues de mandar los datos 
	
		
	#csv_file.close()


#modifica: La solicitud del nodo verde 
#efecto: Elimina del string enviado del nodo verde los caracteres '\n' y '\0' y tambien lo utilizo para cortar la parte del tipo de solicitud que es
#@param: el msj que va a ser cortado
#        inicio de donde va a prevalecer sin cortar
#        final de donde va a prevalecer sin cortar
def adjust_request(par_request, i, f):
	return par_request[i:f] #corta el string dejando solamente la parte desde la pos i a la f
											   #cortando exactamente los caracteres '\n' y '\0' enviados desde el programa c  


#efecto: envia al nodo verde los datos del archivo en csv
def send_to_green(msg,request_number,par_sending_pipe):
	bitacora.write('[' + str(datetime.now()) + '] ' + "Case  1 " + msg + "  Orange  send_g<-o\n" )
	if(request_number == '0'):
		os.write(par_sending_pipe, msg.encode() )
	if(request_number == '1'):
		os.write(par_sending_pipe, (request_number + ',' + msg).encode() )
	if(request_number == '2'):
		os.write(par_sending_pipe, (request_number + ',' + msg).encode() )
	
		
	
#efecto: castea la lista creada por el csv reader para hacerle una linea string
#modifica: la lista del csv reader 
#@param: la lista que se va a convertir en string
def cast_list_to_string(par_list):  
    
    msg = ""  
      
    for s in par_list:  
        msg += s + ','
      
    return msg
	
def main():
	bitacora.write('[' + str(datetime.now()) + '] ' + "Case  0 Orange  Created\n" )
	try:
		receiving_pipe = os.open( ORANGE_RCV_PP, os.O_RDONLY )
		bitacora.write('[' + str(datetime.now()) + '] ' + "Case  0  Orange  open sucessfuly " + ORANGE_RCV_PP + "\n" )
	except IOError:
		bitacora.write('[' + str(datetime.now()) + '] ' + "Case  3  Orange  err_open " + ORANGE_RCV_PP + "\n" )
	
	try:
		sending_pipe = os.open( ORANGE_SND_PP, os.O_WRONLY )
		bitacora.write('[' + str(datetime.now()) + '] ' + "Case  0  Orange  open sucessfuly " + ORANGE_SND_PP + "\n" )
	except IOError:
		bitacora.write('[' + str(datetime.now()) + '] ' + "Case  3  Orange  err_open " + ORANGE_SND_PP + "\n" )
		
	while True:
		request = listen_green(receiving_pipe)
		type_request = adjust_request(request, 0,1) #corta la solicitud obteniendo unicamente el numero que indica que tipo de solitud es 
		file_searching(adjust_request(request, 1,len(request) - 1), type_request,receiving_pipe,sending_pipe) #a este metodo se le pasa la solicitud del verde ya ajustada 
	
if __name__ == "__main__":
   main()
