import sys # argv[]
import os 
from spanning_tree import *
from GreenAgent import *
from Router import *
from Sandbox import Sandbox
from StopWait import *

ID = sys.argv[1]
MODE = sys.argv[2]

#Efecto: Manejador de signals que se encarga de cerrar el log cuando el verde le diga que se muera
def handler(signum, frame):
	print("signal catch")
	bitacora.close()
	exit()

bitacora = open("log/rose_logs/rose_log"+ sys.argv[1]+".txt","w+")

def main():
	agent = GreenAgent(ID)
	router = Router()
	AG = SpanningTree(ID, bitacora)
	SW = StopWait(ID, agent, bitacora)
	SB = Sandbox(ID,bitacora)
	
	agent.set_instancies(router,AG,SB,SW)
	AG.set_instancies(agent,router)
	router.set_instances(agent, AG, SB)
	SB.set_instancies(agent,router,SW)
	
	agent.threat_init()
	router.thread_init()
	SW.thread_init()
	SB.thread_init()

	if(MODE == 't'):
		AG.send_silly_bc_update()
	else:
		AG.thread_init()

	signal.signal(2, handler)

if __name__ == '__main__':
	main()

"""import sys # argv[]
import os 
from spanning_tree import *
from GreenAgent import *
from Router import *
from StopWait import *

import time
import queue

ID = sys.argv[1]
MODE = sys.argv[2]

#Efecto: Manejador de signals que se encarga de cerrar el log cuando el verde le diga que se muera
def handler(signum, frame):
	print("signal catch")
	bitacora.close()
	exit()

bitacora = open("log/rose_logs/rose_log"+ sys.argv[1]+".txt","w+")

def main():
	agent = GreenAgent(ID)
	router = Router()
	AG = SpanningTree(ID, bitacora)
	SW = StopWait( ID, agent )
	
	agent.set_instancies(router,AG,0,SW)
	AG.set_instancies(agent,router)
	router.set_instances(agent, AG)
	
	agent.threat_init()
	router.thread_init()
	SW.thread_init()

	if(MODE == 't'):
		AG.send_silly_bc_update()
	else:
		AG.thread_init()

	inq = queue.Queue()
	outq = queue.Queue()
	if SW.set_channel( inq, outq, 0 ):
		print("se establece canal")
		if ID == '1':
			time.sleep(2)
			req = struct.pack("!3H", 0, 3, 1)
			inq.put(req)
			resp = outq.get(block=True)
			dt = struct.unpack( "BB", resp )
			if dt[0] == 0 and dt[1] == 1:
				print("se establece conexion")
				print("empiezo a mandar paquetes")
				for i in range(15):
					num = "hola%d" % i
					p = struct.pack("!H%ds"%len(num), 1, num.encode())
					inq.put(p)
				p = struct.pack("!2H", 255, 1)
				time.sleep(3)
				inq.put(p)
		elif ID == '3':
			print("SB escucha por paquetes")
			while True:
				p = outq.get(block=True)
				d = struct.unpack("!BH", p[:3])
				if d[0] != 255:
					print( p.decode() )
				else:
					print("se cierra conexion en SB con", d[1])

	signal.signal(2, handler)

if __name__ == '__main__':
	main()"""