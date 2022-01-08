#ifndef STRUCT_H // include guard
#define STRUCT_H
#include <queue>
#include <memory>
#include <stdlib.h>
#include <semaphore.h>
#include "../packet/Packet/PHeaders.h"
#include <utility>
using namespace std;

/* 
 * Colas utilizadas para el manejo de paquetes. Son blocking. 
 */
struct packet_queue
{
private:
public:
	sem_t semaphore;
	queue<shared_ptr<Packet>> data_queue;
	packet_queue();
	~packet_queue();
	void data_push(shared_ptr<Packet> packet);
	shared_ptr<Packet> data_pop();
	int empty();
	int getSize();
};

/* 
 * Cola utilizada para la funcion de envio de mensajes por udp. 
 */
struct link_queue
{
public:
	sem_t semaphore;
	queue<pair<shared_ptr<Packet>, int>> data_queue;
	link_queue();
	~link_queue();
	void data_push(shared_ptr<Packet>, int);
	pair<shared_ptr<Packet>, int> data_pop();
	int empty();
};

/* 
 * Strcut de datos de los nodos vecinos. 
 */
typedef struct
{
	ushort id;
	char ip_add[16];
	short pt_num;
} nb_data_t;

/* 
 * Struct de datos propios del nodo verde. 
 */
struct my_data_t
{
public:
	ushort id;
	char ip_add[16];
	short pt_num;
	int nb_count;
	nb_data_t *nb_data;

	my_data_t(){};
	~my_data_t();
};

#endif /* ORANGE_AGENT_H */