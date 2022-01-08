#include "OrangeAgent.h"
OrangeAgent::~OrangeAgent()
{
}

int OrangeAgent::orange_init(char *arg)
{
	pid_t pid = fork();
	if (!pid)
	{
		if (execlp("python3", "python3", "../orange/orange.py", arg, NULL) < 0)
			return 1;
	}

	return 0;
}

int OrangeAgent::data_send(my_data_t *my_data, char *csv_file, char *fifo_recv, char *fifo_send)
{
	int fd_recv, fd_send;

	// /* mas uno para hacer un futuro cat del tipo de solicitud de datos que se va a hacer */
	char request_to_orange[strlen(csv_file) + 2];
	bzero(request_to_orange, strlen(csv_file) + 2);

	fd_recv = open(fifo_recv, O_WRONLY);
	fd_send = open(fifo_send, O_RDONLY);
	request_to_orange[0] = MYS_DATOS_REQUEST;
	strcat(request_to_orange, csv_file);

	write(fd_recv, request_to_orange, strlen(request_to_orange) + 1);
	if (data_recv(my_data, MYS_DATOS_REQUEST, fd_recv, fd_send))
	{
		log->print_in_log(3, (char*)"< OA > Error listening orange id");

		return 1;
	}
	/* Utilizo bzero para limpiar el buffer de msj */
	bzero(request_to_orange, strlen(csv_file) + 1);
	request_to_orange[0] = NEIGHBORS_REQUEST;
	strcat(request_to_orange, csv_file);
	write(fd_recv, request_to_orange, strlen(request_to_orange) + 1);
	if (data_recv(my_data, NEIGHBORS_REQUEST, fd_recv, fd_send))
	{
		log->print_in_log(3, (char*)"< OA > Error listening orange neighbour");
		return 1;
	}
	/*Aqui se cerrarian los respectivos fifos de parte del verde hacia el naranja, ya que no se utilizaran mas */
	close(fd_recv);
	close(fd_send);
	return 0;
}

int OrangeAgent::data_recv(my_data_t *my_data, char number_request, int fd_recv, int fd_send)
{
	char arr[32];
	/* se utiliza para que siempre haya un \0 al final de lo que recibe */
	bzero(arr, 32);

	if (number_request == MYS_DATOS_REQUEST)
	{
		// Read from FIFO
		read(fd_send, arr, sizeof(arr));

		if (number_request == arr[0])
		{
			if (data_load(arr, my_data))
				cout << "Error L81" << endl;
			log->print_in_log(3, (char*)"< OA > Error in my data load");
		}

		/* Print the read message */
		log->print_in_log(2, (char*)"< OA > Receive from orange my data");
	}

	if (number_request == NEIGHBORS_REQUEST)
	{
		int nghb_count = 0;
		/* Read from FIFO */
		read(fd_send, arr, sizeof(arr));
		nghb_count = atoi(arr);
		nb_data_t *nb_data_ptr = (nb_data_t *)malloc(nghb_count * sizeof(nb_data_t));
		my_data->nb_data = nb_data_ptr;
		my_data->nb_count = nghb_count;

		write(fd_recv, "h", 1);

		for (int i = 0; i < nghb_count; ++i)
		{
			// en este for se hacen cambios entre lectura y escritura del fifo con el fin de sincronizar procesos
			bzero(arr, 32);
			read(fd_send, arr, sizeof(arr));
			log->print_in_log(2, (char*)"< OA > Receive from orange neighbour data");
			if (number_request == arr[0])
			{
				if (data_load(arr, (my_data_t *)&nb_data_ptr[i]))
					this->log->print_in_log(3, (char*)"< OA >Error in neighbour data load");
			}

			/* bandera de que ya consumio la informacion */
			write(fd_recv, "r", 1);
		}
	}
	return 0;
}

int OrangeAgent::data_load(char *msg_buf, my_data_t *my_data)
{
	char node_num[8] = {0};
	char ip[16] = {0};
	char port[6] = {0};
	/* para saltar el identificador de mensaje y la coma inicial */
	int index = 2;

	index = get_csv_line_value(msg_buf, index, node_num);
	if (index == -1)
		return 1;

	index = get_csv_line_value(msg_buf, index, ip);
	if (index == -1)
		return 1;

	index = get_csv_line_value(msg_buf, index, port);
	if (index == -1)
		return 1;

	my_data->id = (short)atoi(node_num);
	strncpy(my_data->ip_add, ip, strlen(ip) + 1);
	my_data->pt_num = (short)atoi(port);
	return 0;
}

int OrangeAgent::get_csv_line_value(char *src, int index, char *dest)
{
	if (src && dest)
	{
		char c = src[index];
		int i = 0;
		while (c != ',' && c != '\0')
		{
			if (c != ' ')
			{
				dest[i] = src[index];
				++i;
			}
			c = src[++index];
		}
		/* para quedar apuntando después de la coma */
		++index;
	}
	else
	{
		index = -1;
	}
	return index;
};

void OrangeAgent::ptr_set(Log* log)
{
	this->log = log;
}
