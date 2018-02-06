class server(object):
	"""docstring for server"""
	def __init__(self, bw, log, id):
		super(server, self).__init__()
		self.__bw=bw
		self.__log=open(log,'w')
		self.__id=id 
	def getbw(self):
		return self.__bw
	def getlog(self):
		return self.__log
	def getid(self):
		return self.__id

def init():
	BandWidth=200
	SERVER=[]
	servercount=10
	for i in range(servercount):
		fname='server'+str(i)+'.log'
		SERVER.append(server(BandWidth,fname,i))
	return SERVER

