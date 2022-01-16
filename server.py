import socket
import os
#from thread import *
from threading import Thread

client_list = []

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 7000


try:
	ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	ServerSocket.bind((host, port))
except socket.error as e:
	print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)


class Client(Thread):
	def __init__(self,connection,name,port):
		Thread.__init__(self)
		self.connection = connection
		self.name = name
		self.port = port

	def run(self):
		self.handle_messages()
		self.connection.close()

	def handle_messages(self):
		while True:
			request = self.connection.recv(1024)
			self.connection.sendall(request)


while True:
	connection, client_address = ServerSocket.accept()
	print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
	new_client= Client(connection, client_address[0] , client_address[1])
	new_client.start()
	client_list.append(new_client)


ServerSocket.close()