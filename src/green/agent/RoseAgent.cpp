#include "RoseAgent.h"

RoseAgent::RoseAgent()
{
}

RoseAgent::~RoseAgent()
{
	pthread_kill(assign, SIGKILL);
	pthread_kill(send, SIGKILL);
	pthread_kill(recv, SIGKILL);
	close(this->fd_send);
	close(this->fd_recv);
}

int RoseAgent::rose_init(char *arg, char *send, char *recv, char *mode, my_data_t *my_data)
{
	char packet[512];
	bzero(packet, 512);

	int8_t protocol = 1;
	short origin_nb = 0;
	int8_t ttl = 0;
	int8_t bc_protocol = 3;
	short origin_node = my_data->id;
	int8_t nb_count = (int8_t)my_data->nb_count;

	memcpy(&packet[0], (unsigned char *)&protocol, 1);
	memcpy(&packet[1], (unsigned char *)&origin_nb, 2);
	memcpy(&packet[3], (unsigned char *)&ttl, 1);
	memcpy(&packet[4], (unsigned char *)&bc_protocol, 1);
	memcpy(&packet[5], (unsigned char *)&origin_node, 2);
	memcpy(&packet[7], (unsigned char *)&nb_count, 1);

	for (int i = 0, e = 8; i < my_data->nb_count; ++i, e += 3)
	{
		memcpy(&packet[e], &my_data->nb_data[i].id, 2);
		packet[e + 2] = 1; // peso
	}

	shared_ptr<Packet> neigh_packet = packet_construct(packet);
	queue_send_store(neigh_packet);

	pipe_send = send;
	pipe_recv = recv;
	pid_t pid = fork();
	if (!pid)
	{
		//El directorio sin path es el del main
		if (execlp("python3", "python3", "../rose/rose.py", arg, mode, NULL) < 0)
			return 1;
		log->print_in_log(2, (char*)"< RA > Initialize rose in python");
	}
	return pid;
}

int RoseAgent::threads_init(RoseAgent *my_class)
{
	my_class->fd_recv = open(my_class->pipe_recv, O_RDONLY);
	my_class->fd_send = open(my_class->pipe_send, O_WRONLY);
	if (pthread_create(&assign, 0, rose_assign, (void *)my_class))
		return 1;
	if (pthread_create(&send, 0, rose_send, (void *)my_class))
		return 1;
	if (pthread_create(&recv, 0, rose_recv, (void *)my_class))
		return 1;
	return 0;
}

void *RoseAgent::rose_assign(void *data)
{
	RoseAgent *my_class = (RoseAgent *)data;

	while (true)
	{

		shared_ptr<Packet> pack = my_class->rose_assign_queue.data_pop();
		int protocol = (int)pack->getProtocol();
		//Protocolos de forward y heartbeat
		if (protocol == HB_PACKET || protocol == AG_PACKET)
		{
			ushort destination = -1;
			switch (protocol)
			{
				case HB_PACKET:
				{
					std::shared_ptr<HbPacket> hb_packet =
						std::dynamic_pointer_cast<HbPacket>(pack);
					destination = hb_packet->getDestination();
				my_class->log->print_in_log(2, (char*)"< RA > < HB > Sends message protocol heartbeat");
					break;
				}
				case AG_PACKET:
				{
					std::shared_ptr<TWHPacket> twh_packet =
						std::dynamic_pointer_cast<TWHPacket>(pack);
					destination = twh_packet->getDestination();
				my_class->log->print_in_log(2, (char*)"< RA > < AG > Sends message protocol spanning tree");
					break;
				}
			}
			int nb_i = my_class->find_nb_i(destination);
			my_class->link_layer->green_send_store(pack, nb_i);
		}
		//Protocolos de broadcast y adyacencias
		else if (protocol == BC_PACKET)
		{
			my_class->network_layer->bc_store(pack);
			my_class->log->print_in_log(2, (char*)"< RA > < BC > Sends message protocol broadcast");
		}
		//Protocolo arbol de adyacencia
		else if (protocol == BCUPDATE_PACKET)
		{
			my_class->network_layer->bc_upd_store(pack);
			my_class->log->print_in_log(2, (char*)"< RA > < BC > Sends message protocol broadcast update");
		}
		else if (protocol == FTUPDATE_PACKET)
		{
			my_class->network_layer->fw_upd_store(pack);
			my_class->log->print_in_log(2, (char*)"< RA > < Fw > Sends message forward update");
		}
		else if(protocol == SW_PACKET)
		{
			my_class->network_layer->fw_store(pack);
		}
		else if( protocol == BSPIDER_PACKET )
		{
			std::cout << "Sending package to transport layer." << std::endl;
			my_class->transport_layer->blue_send_store(pack);
		}
		else if (protocol == STAT_PACKET)
		{
			my_class->stat_manager->spider_queue_store(pack);
			my_class->log->print_in_log(2, (char*)"< RA > < SM > Sends spider message to stat manager");


		}
	}
}

void *RoseAgent::rose_send(void *data)
{
	RoseAgent *my_class = (RoseAgent *)data;
	while (true)
	{
		shared_ptr<Packet> pack = my_class->rose_send_queue.data_pop();
		char *buffer = pack->deconstruct();
		unsigned short n_length = htons(pack->getSize());
		write(my_class->fd_send, (unsigned char *)&n_length, 2);
		write(my_class->fd_send, buffer, pack->getSize());
		delete [] buffer;
	}
}

void *RoseAgent::rose_recv(void *data)
{
	RoseAgent *my_class = (RoseAgent *)data;
	short length;
	while (true)
	{
		int bytes_red = read(my_class->fd_recv, (unsigned char *)&length, 2);
		if (bytes_red)
		{
			length = ntohs(length);
			if (length > 0)
			{
				char *buffer = new char[length]();
				read(my_class->fd_recv, buffer, length);
				
				shared_ptr<Packet> pack = packet_construct(buffer);
				my_class->rose_assign_queue.data_push(pack);
				delete buffer;
			}
		}
	}
}

int RoseAgent::queue_send_store(shared_ptr<Packet> package)
{
	this->rose_send_queue.data_push(package);
	return 0;
}

void RoseAgent::ptr_set(NetworkLayer *network, LinkLayer *ll, my_data_t *my_data, Log* log, StatsManager * stat, TransportLayer * tl )
{
	this->network_layer = network;
	this->my_data = my_data;
	this->link_layer = ll;
	this->log = log;
	this->stat_manager = stat;
	this->transport_layer = tl;
}


int RoseAgent::find_nb_i(ushort nb_id){
    for (int nb_i = 0; nb_i < my_data->nb_count; ++nb_i)
        if (my_data->nb_data[nb_i].id == nb_id)
            return nb_i;
    return -1;
}