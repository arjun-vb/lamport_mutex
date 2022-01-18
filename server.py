import socket, pickle
import os
#from thread import *
from threading import Thread
from common import *
import hashlib

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


Blockchain = []

def initializeBlockchain():
	block = Block(0,Transaction(0, 1, 10))
	Blockchain.append(block)

	block = Block(hashlib.sha256(str(block)).digest(), Transaction(0,2,10))
	Blockchain.append(block)

	block = Block(hashlib.sha256(str(block)).digest(), Transaction(0,3,10))
	Blockchain.append(block)


initializeBlockchain()


class Server_Thread(Thread):
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
			#print(data.reqType)
			#print(data.fromPid)
			if data.reqType == "BALANCE":
				self.handle_balance(data)
			elif data.reqType == "LAST_BLOCK":
				self.get_lastblock(data)
			elif data.reqType == "ADD_BLOCK":
				self.add_block(data)
			
	def handle_balance(self, data):
		balance = 0
		for blk in Blockchain:
			if blk.transaction.sender == data.fromPid:
				balance -= int(blk.transaction.amount)
			if blk.transaction.reciever == data.fromPid:
				balance += int(blk.transaction.amount)
		client_list[data.fromPid].connection.sendall(str(balance))
		

	def get_lastblock(self, data):
		client_list[data.fromPid].connection.sendall(pickle.dumps(Blockchain[-1]))

	def add_block(self, data):
		Blockchain.append(data.block)
		client_list[data.fromPid].connection.sendall("SUCCESSFUL")


connection, client_address = ServerSocket.accept()
print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
new_client= Server_Thread(connection, client_address[0] , client_address[1])
new_client.start()
client_list[client_address[1]%7000] = new_client

connection, client_address = ServerSocket.accept()
print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
new_client= Server_Thread(connection, client_address[0] , client_address[1])
new_client.start()
client_list[client_address[1]%7000] = new_client

connection, client_address = ServerSocket.accept()
print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
new_client= Server_Thread(connection, client_address[0] , client_address[1])
new_client.start()
client_list[client_address[1]%7000] = new_client


def print_blockchain():
	print("=======================================")
	for blk in Blockchain:
		print("Sender: " + str(blk.transaction.sender) + " | Reciever: " + str(blk.transaction.reciever)
			+ " | Amount: " + str(blk.transaction.amount)) 
	print("=======================================")
while True:
	user_input = raw_input()
	if user_input == "PRINT":
		print_blockchain()



ServerSocket.close()