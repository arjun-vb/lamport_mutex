import socket, pickle
import os
#from thread import *
from threading import Thread
from common import *

client_list = {}

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
			data = pickle.loads(request)
			print(data.reqType)
			print(data.fromPid)
			if data.reqType == "MUTEX":
				self.handle_mutex_request(data)
			elif data.reqType == "REPLY":
				self.handle_reply(data)
			elif data.reqType == "RELEASE":
				self.handle_release(data)
			
			#self.connection.sendall(request)
	def handle_mutex_request(self, data):
		if data.fromPid == 1:
			client_list[2].connection.sendall(pickle.dumps(data))
			#client_list[3].connection.sendall(pickle.dumps(data))
		if data.fromPid == 2:
			client_list[1].connection.sendall(pickle.dumps(data))
			#client_list[3].connection.sendall(pickle.dumps(data))
		if data.fromPid == 3:
			client_list[1].connection.sendall(pickle.dumps(data))
			#client_list[2].connection.sendall(pickle.dumps(data))

	def handle_reply(self, data):
		if data.clock.pid == 1:
			client_list[1].connection.sendall(pickle.dumps(data))
		if data.clock.pid  == 2:
			client_list[2].connection.sendall(pickle.dumps(data))
		if data.clock.pid  == 3:
			client_list[3].connection.sendall(pickle.dumps(data))

	def handle_release(self, data):
		if data.fromPid == 1:
			client_list[2].connection.sendall(pickle.dumps(data))
			#client_list[3].connection.sendall(pickle.dumps(data))
		if data.fromPid == 2:
			client_list[1].connection.sendall(pickle.dumps(data))
			#client_list[3].connection.sendall(pickle.dumps(data))
		if data.fromPid == 3:
			client_list[1].connection.sendall(pickle.dumps(data))
			#client_list[2].connection.sendall(pickle.dumps(data))

while True:
	connection, client_address = ServerSocket.accept()
	print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
	new_client= Client(connection, client_address[0] , client_address[1])
	new_client.start()
	client_list[client_address[1]%7000] = new_client


ServerSocket.close()