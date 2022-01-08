#ifndef ROSE_AGENT_H // include guard
#define ROSE_AGENT_H
#include "../packet/Packet/PHeaders.h"
#include "../struct/structs.h"
#include "../network_layer/NetworkLayer.h"
#include "../link_layer/LinkLayer.h"
#include "../transport_layer/transport_layer.h"
#include "../stats/StatsManager.h"

#include "../log/log.h"
#include <stdlib.h>
#include <stdint.h>
#include <queue>
#include <string>
#include <memory>
#include <unistd.h>  
#include <fcntl.h>	
#include <iostream>
#include <sys/stat.h>	 // mkfifo
#include <pthread.h>
#include <cstdlib>
#include <stdio.h>
#include <string>
#include <signal.h>
using namespace std;

class LinkLayer;
class TransportLayer;
class NetworkLayer;
class StatsManager;
class RoseAgent
{
private:
	StatsManager* stat_manager;

	Log * log;
	NetworkLayer* network_layer;
	TransportLayer* transport_layer;
	LinkLayer* link_layer;
	/*Cola para guardar mensajes del rosado*/
	packet_queue rose_send_queue;
	/*Cola para enviar mensajes  al rosado */
	packet_queue rose_assign_queue;
	/*Hilos para realizar el paralelismo*/
	pthread_t assign, send, recv;
	my_data_t *my_data;
	/*Nombre de los file descriptors*/
	int fd_send, fd_recv;
	char* pipe_send;
	char* pipe_recv;
		/**
	 * @Efecto: Metodo que ejecuta el hilo, responsable de enviar el 
	 * mensaje(paquete) al rosa en python por medio de pipes 
	 * @Requiere: my_class: instancia de la misma clase, con el fin 
	 * de que los hilos puedan conocer los metodos de dicha clase
	 * @Modifica: Nada
	 * @Autor:Pablo
	 **/
	static void* rose_send(void* data);
		/**
	 * @Efecto: Metodo que ejecuta el hilo, responsable de clasificar el 
	 * mensaje(paquete) y ponerlo en la cola correspondiente del NetworkLayer 
	 * @Requiere: my_class: instancia de la misma clase, con el fin 
	 * de que los hilos puedan conocer los metodos de dicha clase
	 * @Modifica: Cola rose_assign_queue
	 * @Autor:Pablo
	 **/	
	static void* rose_assign(void* data);
		/**
	 * @Efecto: Metodo que ejecuta el hilo, responsable de recibir los 
	 * mensaje(paquete) y ponerlo en la cola pendiente a clasificar 
	 * @Requiere: my_class: instancia de la misma clase, con el fin 
	 * de que los hilos puedan conocer los metodos de dicha clase
	 * @Modifica: Cola rose_assign_queue
	 * @Autor:Pablo
	 **/		
	static void* rose_recv(void* data);
	/* Efecto: dado un id de vecino, su busca el indice de la posicion de ese vecino
               en la tabla de vecinos en my_data. 
     * Requiere: No aplica.
     * Modifica: No aplica.
     * Retorna: indice de la posicion del vecino dado en la tabla de vecinos. 
     */
    int find_nb_i(ushort);



public:
	RoseAgent();
	~RoseAgent();

	/**
	 * @Efecto: Inicializa el proceso hijo que se encarga 
	 * de ejecutar el codigo del rosado en python, tambien 
	 * guarda el nombre de los pipes para luego abrirlos
	 * @Requiere: arg: la terminacion del nombre de los
	 *  pipes expecificos de dicho nodo. 
	 * send y recv: nombre de los archivos de los pipes
	 * @Modifica: las variables de la clase donde se almacenan 
	 * los nombres de los pipes
	 * @Autor:Pablo
	 **/
	int rose_init(char* arg, char* send, char* recv, char * mode, my_data_t * my_data);
	/**
	 * @Efecto: Inicializa los hilos responsables de los metodos
	 * que reciben, envian y clasifican los mensajes que le llegen
	 * @Requiere: my_class: instancia de la misma clase, con el fin 
	 * de que los hilos puedan conocer los metodos de dicha clase
	 * @Modifica: Nada
	 * @Autor:Pablo
	 **/
	int threads_init(RoseAgent * my_class);
		/**
	 * @Efecto: Guarda una instancia de NetworkLayer 
	 * en un puntero de la clase
	 * @Requiere: puntero de la clase NetworkLayer 
	 * @Modifica: puntero de la la clase NetworkLayer en RoseAgent
	 * @Autor:Pablo
	 **/
	void ptr_set(NetworkLayer* network, LinkLayer *ll, my_data_t*my_data, Log* log, StatsManager*, TransportLayer *tl);
		/**
	 * @Efecto: Guarda un paquete en la cola que recibe 
	 * los mensajes para el modulo rosado
	 * @Requiere: smart pointer de la clase generica paquete
	 * @Modifica: cola rose_send_queue
	 * @Autor:Pablo
	 **/
	int queue_send_store(shared_ptr<Packet> package);

};
#endif /* ORANGE_AGENT_H */