"""
This class is implemented as a priority queue for tuple elements
Where the first object in the tuple is the heuristic
"""
class PQueue(object):
	def __init__( self ):
		self.pqueue = []
	
	def insert( self, element ):
		if len(self.pqueue) == 0 or element[0] >= self.pqueue[-1][0]:
			self.pqueue.append(element)
		else:
			position = -1
			for i in range( len(self.pqueue) ):
				if element[0] < self.pqueue[i][0]:
					position = i
					break
			self.pqueue.insert( position, element )
				
	def pop( self ):
		return self.pqueue.pop(0)
		
	def delete( self, element ):
		i = self.pqueue.index( element )
		del self.pqueue[i]
	
	def exists( self, element ):
		for n in self.pqueue:
			if n[1] == element[1]:
				return n
		return None
		
	def get( self, index ):
		return self.pqueue[index][1]
		
	def __len__( self ):
		return len( self.pqueue )
	
	def __str__( self ):
		return '[' + ', '.join( e[1].get_id() for e in self.pqueue ) + ']'