#include "transport_layer.h"

TransportLayer::~TransportLayer()
{
	for (int i = 0; i < NUM_THREADS; i++)
		pthread_kill(threads[i], SIGKILL);
	shutdown(this->tcp_socket, 2);
	shutdown(this->blue_sockfd, 2);
	close(this->tcp_socket);
	close(this->blue_sockfd);
}

int TransportLayer::tcp_connect()
{
	/* se empieza a crear el socket para la conexion TCP */
	int tcp_sockfd, blue_sockfd, clien_len;
	struct sockaddr_in server_addr, client_addr;
	tcp_sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (tcp_sockfd < 0)
	{
		log->print_in_log(3, (char*)"< TL > error creating socketfd");
		return 1;
	}
	log->print_in_log(0, (char*)"< TL > socketfd TCP was created successfully");
	bzero(&server_addr, sizeof(server_addr));
	server_addr.sin_family = AF_INET;
	inet_pton(AF_INET, my_data->ip_add, &(server_addr.sin_addr));
	/* to listen on port 500# */
	server_addr.sin_port = htons(5000 + my_data->id);
	if (bind(tcp_sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
	{
		log->print_in_log(3, (char*)"< TL > Error binding blue socket");
		return 1;
	}
	listen(tcp_sockfd, 0);
	clien_len = sizeof(client_addr);
	blue_sockfd = accept(tcp_sockfd, (struct sockaddr *)&client_addr, (socklen_t *)&clien_len);
	this->blue_sockfd = blue_sockfd;
	this->tcp_socket = tcp_sockfd;
	return 0;
}

void *TransportLayer::blue_recv(void *data)
{
	TransportLayer *t = (TransportLayer *)data;
	std::cout << "READY TO CONNECT." << std::endl;
	while (t->tcp_connect())
	{
		sleep(0.1);
	}
	std::cout << "CONNECTED TO HOST." << std::endl;
	t->log->print_in_log(0, (char*)" < TL > listening blue");
	char msg_buffer[205];
	int connected = 1;
	while (connected)
	{
		/* se lee del socket */
		bzero(msg_buffer, 205);
		int bytes_recv = read(t->blue_sockfd, msg_buffer, 1);
		if (bytes_recv <= 0)
		{
			t->log->print_in_log(3, (char*)"< TL > lost connection with host TCP");
			raise(SIGINT);
			connected = 0;	
		}
		else
		{
			int size = (int8_t)msg_buffer[0];
			read(t->blue_sockfd, msg_buffer, size);
			shared_ptr<Packet> p = t->recv_construct(msg_buffer);
			if(p){	
				t->log->print_in_log(2,(char*)"< TL > received sucessfully of blue msg");
				/* Se encola en la cola que recibe mensajes de nodo azul */
				t->blue_rcv_queue.data_push(p);
			}
		}
	}
	return 0;
}


void *TransportLayer::blue_send(void *data)
{
	TransportLayer *t = (TransportLayer *)data;
	char *msg_buffer;
	int bytes_sent;
	ushort size;
	while (1)
	{
		std::shared_ptr<Packet> p = t->blue_snd_queue.data_pop();
		msg_buffer = p->deconstruct();
		size = p->getSize();
		bytes_sent = write(t->blue_sockfd, msg_buffer, size);
		if(bytes_sent > 0)
			t->log->print_in_log(1, (char*)"< TL > sending by blue send succesfully");
		else
			t->log->print_in_log(0, (char*)"< TL > error sending by blue");
		delete [] msg_buffer;
	}
	return 0;
}

shared_ptr<Packet> TransportLayer::recv_construct(char *buffer){
	shared_ptr<Packet> p;
	uint8_t protocol = (uint8_t)*buffer;
	switch(protocol){
		case FW_PACKET:
		{
			char msg_format[209];
			struct __attribute__((__packed__)){
				uint8_t protocol = 0;
				ushort origen;
			}pack;
			pack.origen = htons(my_data->id);
			memcpy(msg_format, (unsigned char*)&pack, 3);
			memcpy(&msg_format[3], &buffer[1], 206);
			p = packet_construct(msg_format);
			if(blue_msg_eval(p))
				return 0;
			break;
		}
		case BC_PACKET:
		{
			char msg_format[214];
			struct __attribute__((__packed__)){
				uint8_t protocol = 1; 
				ushort origin_nb;
				uint8_t ttl = 0; 
				uint8_t bc_protocol = 0;
				ushort origen;
			}pack;
			pack.origen = htons(my_data->id);
			pack.origin_nb = htons(my_data->id);
			memcpy(msg_format, (unsigned char*)&pack, 7);
			memcpy(&msg_format[7], &buffer[1], 206);
			p = packet_construct(msg_format);
			if(blue_msg_eval(p))
				return 0; 
			break;
		}
		default:
			p = packet_construct(buffer);
	}
	return p; 
}

int TransportLayer::blue_msg_eval(std::shared_ptr<Packet> p)
{	
	return 0;
}

void *TransportLayer::blue_assign(void *data)
{
	TransportLayer *t = (TransportLayer *)data;
	while (1)
	{
        std::shared_ptr<Packet> p = t->blue_rcv_queue.data_pop();
		/* Envia a la cola respectiva segun el protocolo */
		switch (p->getProtocol())
		{
		case FW_PACKET: 
			t->log->print_in_log(1, (char*)"< TL > < FW > Its despatched");
			t->network_layer->fw_store(p);
			break;
		case BC_PACKET:
			t->log->print_in_log(1, (char*)"< TL > < BC > Its despatched");
			t->network_layer->bc_store(p);
			break;
		case BSPIDER_PACKET:
			t->log->print_in_log(1, (char*)"< TL > < RA > Its despatched");
			t->rose_agent->queue_send_store(p);
		}
	}
}

void TransportLayer::blue_recv_store(std::shared_ptr<FwPacket> p)
{
	this->blue_rcv_queue.data_push(p);
}

void TransportLayer::blue_send_store(std::shared_ptr<Packet> p)
{
	this->blue_snd_queue.data_push(p);
}

int TransportLayer::threads_init(TransportLayer *t)
{
	log->print_in_log(0, (char*)"< TL > Threads are ready");
	if (pthread_create(&threads[0], 0, blue_recv, (void *)t) != 0)
		return 1;
	if (pthread_create(&threads[1], 0, blue_send, (void *)t) != 0)
		return 1;
	if (pthread_create(&threads[2], 0, blue_assign, (void *)t) != 0)
		return 1;
	return 0;
}

void TransportLayer::ptr_set(NetworkLayer *n, RoseAgent* ra, my_data_t *m, Log* l)
{
	this->network_layer = n;
	this->my_data = m;
	this->log = l;
	this->rose_agent = ra;
}

void TransportLayer::sock_shutdown(){
	shutdown(this->tcp_socket, SHUT_RDWR);
	close(this->tcp_socket);
}