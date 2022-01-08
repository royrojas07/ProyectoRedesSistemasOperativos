#include "structs.h"
packet_queue::packet_queue()
{
	sem_init(&semaphore, 0, 0);
}

packet_queue::~packet_queue()
{
	sem_destroy(&semaphore);
}

void packet_queue::data_push(shared_ptr<Packet> data)
{
	data_queue.push(data);
	sem_post(&semaphore);
}

shared_ptr<Packet> packet_queue::data_pop()
{
	sem_wait(&semaphore);
	shared_ptr<Packet> data = data_queue.front();
	data_queue.pop();
	return data;
}
int packet_queue::empty()
{
	return data_queue.empty();
}

int packet_queue::getSize()
{
	return data_queue.size();
}

link_queue::link_queue()
{
	sem_init(&semaphore, 0, 0);
}

link_queue::~link_queue()
{
	sem_destroy(&semaphore);
}

void link_queue::data_push(shared_ptr<Packet> data, int nb_i)
{
	data_queue.push(make_pair(data, nb_i));
	sem_post(&semaphore);
}

pair<shared_ptr<Packet>, int> link_queue::data_pop()
{
	sem_wait(&semaphore);
	pair<shared_ptr<Packet>, int> data = data_queue.front();
	data_queue.pop();
	return data;
}
int link_queue::empty()
{
	return data_queue.empty();
}


my_data_t::~my_data_t()
{
	delete [] nb_data;
}