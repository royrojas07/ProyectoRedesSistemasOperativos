#ifndef ORANGE_AGENT_H // include guard
#define ORANGE_AGENT_H
#include "../packet/Packet/PHeaders.h"
#include "../struct/structs.h"
#include "../log/log.h"
#include <stdlib.h>
#include <stdint.h>
#include <queue>
#include <string>
#include <memory>
#include <unistd.h>
#include <sys/stat.h> // mkfifo
#include <fcntl.h>
#include <iostream>
#include <pthread.h>
#define MSG_SIZE 207
#define MYS_DATOS_REQUEST '1'
#define NEIGHBORS_REQUEST '2'
using namespace std;

class OrangeAgent
{
private:
	/*Hilos para realizar el paralelismo*/
	pthread_t send, recv;
	/* Instancia de la bitacora */
	Log * log;

			/**
	 * @Efecto: Recibe mensajes desde el naranja de python
	 * @Requiere: my_class: instancia de la misma clase, con el fin 
	 * de que los hilos puedan conocer los metodos de dicha clase
	 * @Modifica: Nada
	 * @Autor:Pablo
	 **/
	int data_recv(my_data_t *my_data, char number_request, int fd_recv, int fd_send);
			/**
	 * @Efecto:Interpreta los mensajes recibidos
	 * @Requiere: my_class: instancia de la misma clase, con el fin 
	 * de que los hilos puedan conocer los metodos de dicha clase
	 * @Modifica: Nada
	 * @Autor:Pablo
	 **/
	int data_load(char *msg_buf, my_data_t *my_data);
			/**
	 * @Efecto: Interpreta los mensajes del csv
	 * @Requiere: my_class: instancia de la misma clase, con el fin 
	 * de que los hilos puedan conocer los metodos de dicha clase
	 * @Modifica: Nada
	 * @Autor:Pablo
	 **/
	int get_csv_line_value(char *src, int index, char *dest);

public:
	OrangeAgent(){};
	~OrangeAgent();

	/**
	 * @Efecto: Metodo para pedir los datos al naranja
	 * @Requiere: my_class: instancia de la misma clase, con el fin 
	 * de que los hilos puedan conocer los metodos de dicha clase
	 * @Modifica: Nada
	 * @Autor:Pablo
	 **/
	int data_send(my_data_t *my_data, char *csv_file, char *fifo_recv, char *fifo_send);
	/**/
			/**
	 * @Efecto: Ejecuta el codigo del naranja en python
	 * @Requiere: Nada
	 * @Modifica: Nada
	 * @Autor:Pablo
	 **/
	int orange_init(char *arg);
	void ptr_set(Log* log);
};

#endif /* ORANGE_AGENT_H */