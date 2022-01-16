import socket
from threading import Thread

p1 = 7001
p2 = 7002
p3 = 7003

host = '127.0.0.1'
port = 7000


cport = input('Port: ')

ClientSocket = socket.socket()
ClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ClientSocket.bind((host, cport))
ClientSocket.listen(3)

client2client = []

class Connections(Thread):
	def __init__(self,connection,name,port,server):
		Thread.__init__(self)
		self.connection = connection
		self.name = name
		self.port = port
		self.server = server

	def run(self):
		#self.invoke_client()
		#self.setup_connections()
		self.handle_messages()
		self.connection.close()

	def handle_messages(self):
		if self.server == True:
			Input = raw_input('Say Something: ')
			#mutex
			#server transac
			self.connection.send(Input)
			Response = self.connection.recv(1024)
			print(Response)
		else:
			while True:
				Input = self.connection.recv(1024)
			
				self.connection.sendall(Input)
				#self.connection = temp



print('Waiting for connection')
try:
	ClientSocket.connect((host, port))
	new_connection = Connections(ClientSocket, host, port, True)
	new_connection.start()
	if cport == 7002:
		ClientSocket1 = socket.socket()
		ClientSocket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		ClientSocket1.bind((host, cport))
		ClientSocket1.connect((host, 7001))
		new_connection = Connections(ClientSocket1, host, port, False)
		new_connection.start()
		client2client.append(new_connection)

except socket.error as e:
	print(str(e))

#Response = ClientSocket.recv(1024)
#while True:
#    Input = raw_input('Say Something: ')
#    mutex
#    server transac
#    lientSocket.send(Input)
#    Response = ClientSocket.recv(1024)
#    print(Response)


while True:
	connection, client_address = ClientSocket.accept()
	print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
	#new_client= Client(connection, client_address[0] , client_address[1])
	#new_client.start()
	new_connection = Connections(connection, client_address[0] , client_address[1], False)
	new_connection.start()
	client2client.append(new_connection)

ClientSocket.close()