#include <sys/types.h> // mkfifo
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/stat.h> // mkfifo
#include <fcntl.h>	  // O_WRONLY and O_RDONLY
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>	   // For exit function
#include <string.h>	   // for bzero
#include <unistd.h>	   // for write and read
#include <arpa/inet.h> // for inet_pton
#include <sys/wait.h>  // for wait(NULL)
#include <pthread.h>   //pthreads
#include <time.h>	   //time
#include <sys/time.h>  // for gettimeofday
#include "../link_layer/LinkLayer.h"
#include "../log/log.h"
//#include "../packet/Packet/PHeaders.h" //creo que no lo ocupa
//#include "../struct/structs.h" //my_data
#include "../agent/OrangeAgent.h"
#include "../agent/RoseAgent.h"
#include "../stats/StatsManager.h"

#include <semaphore.h>
#include <stdint.h>
#include <unistd.h>
#include <csignal>

#define ROSERCVPP	"rose_rcv_pp"
#define ROSESNDPP	"rose_snd_pp"
#define ORANGERCVPP	"orange_rcv_pp"
#define ORANGESNDPP	"orange_snd_pp"

int usage(int, char *argv[]);
int orange_call(my_data_t *, OrangeAgent *, char *);
int rose_call(RoseAgent *, char *, my_data_t *);
std::shared_ptr<Packet> neighbors_packet_load(my_data_t *);
void remove_pp(char *);
char AGmode[1];

void signal_handler(int signal)
{
	/* DO NOTHING */
}

/*Recibe el numero de archivo que va a buscar y el mode de AG */
int main(int argc, char *argv[])
{
	Log log(atoi(argv[1]));
	AGmode[0] = 't';
	if (usage(argc, argv))
	{
		log.print_in_log(3, (char*)"< G > error in arguments");
		return 1;
	}
	my_data_t my_data;

	OrangeAgent orange;
	orange.ptr_set(&log);
	if(orange_call(&my_data, &orange, argv[1]))
		log.print_in_log(3, (char*)"< G > error in orange call");

	RoseAgent rose;
	int rose_pid = rose_call(&rose, argv[1], &my_data);
	if(rose_pid == 1)
		log.print_in_log(3, (char*)"< G > error in rose call");
	
	TransportLayer transport_layer;
	NetworkLayer network_layer;
	LinkLayer link_layer(&my_data);
	StatsManager stats_manager;

	
	transport_layer.ptr_set(&network_layer, &rose, &my_data,&log);
	network_layer.ptr_set(&link_layer, &transport_layer, &rose, &log, &my_data, &stats_manager);
	link_layer.ptr_set(&network_layer,&rose,&log);
	rose.ptr_set(&network_layer, &link_layer, &my_data, &log, &stats_manager, &transport_layer);
	stats_manager.ptr_set(&rose, &network_layer, &link_layer, &my_data, &log);

	if(transport_layer.threads_init(&transport_layer))
		log.print_in_log(3, (char*)"< G > error in transport layer threads init");
	if(network_layer.threads_init(&network_layer))
		log.print_in_log(3, (char*)"< G > error in network layer threads init");
	if(link_layer.threads_init(&link_layer))
		log.print_in_log(3, (char*)"< G > error in link layer threads init");
	if(stats_manager.threads_init(&stats_manager))
		log.print_in_log(3, (char*)"< G > error in stat manager threads init");

	// while(1)
	// {
	// 	stats_manager.print_stats();
	// 	sleep(10);
	// }


	std::signal(SIGINT, signal_handler);
	/* Espere hasta que sea interrumpito por señal. */
	pause();
	kill(rose_pid,2);
	std::cout << "\nPROGRAM EXITS." << std::endl;
	transport_layer.sock_shutdown();
	remove_pp(argv[1]);
	return 0;
}

int usage(int argc, char *argv[])
{
	if (argc != 2)
	{
		if (argc == 3 && argv[2][0] == '-')
		{
			switch (argv[2][1])
			{
			case 'i':
				AGmode[0] = 'i';
				printf("AG mode intelligent activated\n");
				break;
			case 't':
				printf("AG mode intelligent desactivated\n");
				break;
			default:
				printf("Missing arguments: <file number> \n");
				return 1;
			}
		}
		else
		{
			printf("Missing arguments: <file number> \n");
			//log error
			return 1;
		}
	}
	return 0;
}

int orange_call(my_data_t *my_data, OrangeAgent *orange, char *argv)
{

	char fifo_snd[18] = "orange_snd_pp";
	char fifo_rcv[18] = "orange_rcv_pp";

	strcat(fifo_snd, argv);
	strcat(fifo_rcv, argv);

	/* Se utiliza por si el programa se cae y no logra cerrar el fifo, ya que esto produce un error */
	remove(fifo_snd);
	remove(fifo_rcv);

	mkfifo(fifo_rcv, 0666);
	mkfifo(fifo_snd, 0666);

	if (orange->orange_init(argv))
		return 1;

	if (orange->data_send(my_data, argv, fifo_rcv, fifo_snd))
		return 1;

	return 0;
}

int rose_call(RoseAgent *rose, char *argv, my_data_t *my_data)
{
	char sending_pipe_name[16] = "rose_snd_pp";
	char receiving_pipe_name[16] = "rose_rcv_pp";

	strcat(sending_pipe_name, argv);
	strcat(receiving_pipe_name, argv);

	remove(receiving_pipe_name);
	remove(sending_pipe_name);

	mkfifo(receiving_pipe_name, 0666);
	mkfifo(sending_pipe_name, 0666);
	int pid = rose->rose_init(argv, sending_pipe_name, receiving_pipe_name, AGmode, my_data);
	
	if (rose->threads_init(rose))
		return 1;

	return pid;
}

void remove_pp(char *id){
	char sending_pipe_name[16] = "rose_snd_pp";
	char receiving_pipe_name[16] = "rose_rcv_pp";
	strcat(sending_pipe_name, id);
	strcat(receiving_pipe_name, id);
	char fifo_snd[18] = "orange_snd_pp";
	char fifo_rcv[18] = "orange_rcv_pp";
	strcat(fifo_snd, id);
	strcat(fifo_rcv, id);
	remove(sending_pipe_name);
	remove(receiving_pipe_name);
	remove(fifo_rcv);
	remove(fifo_snd);
}