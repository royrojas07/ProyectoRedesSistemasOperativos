import spanning_tree 
import GreenAgent
import sys
if __name__ == "__main__":
    id = sys.argv[1]
    print(sys.argv[2])
    g = GreenAgent.GreenAgent(id)
    bc = spanning_tree.Broadcast(1, [1,2], g)
    

    