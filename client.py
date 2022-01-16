import socket

from threading import Thread

ip = '127.0.0.1'
p1 = 7001
p2 = 7002
p3 = 7003

cport = input('Port: ')

ClientSocket = socket.socket()
ClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ClientSocket.bind((ip, cport))
host = '127.0.0.1'
port = 7000

resp= []

lomportclock = ""
requestQueue = [] # priority queue
releaseMAP = []


print('Waiting for connection')
try:
	ClientSocket.connect((host, port))
except socket.error as e:
	print(str(e))

class Connections(Thread):
	def __init__(self,connection):
		Thread.__init__(self)
		self.connection = connection

	def run(self):
		while True:
			
			Response = self.connection.recv(1024)
			print(Response)

			# reply - update reply map, 
			# if eligible for trancation {
				# pop for queue and execute the request   }
			#release
			# if eligible for tranction {
				# pop for queue and execute the request   }
			# request for resource from other clients
				# send reply
			# 


new_connection = Connections(ClientSocket)
new_connection.start()


while True:
	Input = raw_input('Say Something: ')
	#mutex function
	#server transac
	ClientSocket.send(Input)
	#Response = self.connection.recv(1024)
	#print(Response)

ClientSocket.close()