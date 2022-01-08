import sys # argv[]
import os 
import signal
from spanning_tree import SpanningTree
from GreenAgent import GreenAgent
from Router import Router
from Sandbox import Sandbox
from SandWTest import StopAndWait

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
	SB = Sandbox(ID,bitacora)
	SW = StopAndWait(ID)
	
	agent.set_instancies(router,AG,SB)
	AG.set_instancies(agent,router)
	router.set_instances(agent, AG)
	SB.set_instancies(agent,router,SW)
	SW.set_instances(SB)
	
	agent.threat_init()
	router.thread_init()
	SB.thread_init()

	
	#SW.send_packages()
	SW.little_test()

	if(MODE == 't'):
		AG.send_silly_bc_update()
	else:
		AG.thread_init()

	signal.signal(2, handler)

if __name__ == '__main__':
	main()
