import socket, pickle
from common import *
import heapq
import hashlib
import time

from threading import Thread

ip = '127.0.0.1'
p1 = 7001
p2 = 7002
p3 = 7003

cport = input('Port: ')
pid = cport
if cport == 7001:
	pid = 1
elif cport == 7002:
	pid = 2
elif cport == 7003:
	pid = 3
else:
	print("Enter valid process id")
	exit()


myClock = LomportClock(0,pid)

requestPriorityQueue = [] 
replyCount = {}
c2c_connections = {}


ClientSocket = socket.socket()
ClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ClientSocket.bind((ip, cport))
host = '127.0.0.1'
port = 7000
user_input = ""

class Connections(Thread):
	def __init__(self,connection):
		Thread.__init__(self)
		self.connection = connection

	def run(self):
		while True:
			print("Entering pickle response at 48")
			response = self.connection.recv(1024)

			data = pickle.loads(response)

			print(data.clock.clock)
			print(data.clock.pid)

			if data.reqType == "MUTEX":
				requestPriorityQueue.append(data.clock)
				heapq.heapify(requestPriorityQueue)
				reply = RequestMessage(pid, data.clock, "REPLY")
				self.connection.send(pickle.dumps(reply))
			
			if data.reqType == "REPLY":
				#print ("Data clock at REPLY is " + str(data.clock.clock))
				#print ("\n Data PID at REPLY is " + str(data.clock.pid))
				print(str(data.clock))
				replyCount[str(data.clock)] += 1
				if replyCount[str(data.clock)] == 2 and requestPriorityQueue[0].pid == pid:
					print("Execute Transaction")
					self.handle_transaction(data)
					heapq.heappop(requestPriorityQueue)
					heapq.heapify(requestPriorityQueue)
					release = RequestMessage(pid, data.clock, "RELEASE")
					broadcast(pickle.dumps(release))

			if data.reqType == "RELEASE":
				print("Inside release")
				heapq.heappop(requestPriorityQueue)
				heapq.heapify(requestPriorityQueue)
				if len(requestPriorityQueue) > 0 and requestPriorityQueue[0].pid == pid and replyCount[str(requestPriorityQueue[0])] == 2:
					print("Execute Transaction")
					self.handle_transaction(data)
					heapq.heappop(requestPriorityQueue)
					heapq.heapify(requestPriorityQueue)
					release = RequestMessage(pid, data.clock, "RELEASE")
					broadcast(pickle.dumps(release))

	def handle_transaction(self, data):
		if user_input == "BAL":
			request = RequestMessage(pid,data.clock,"BALANCE")
			c2c_connections[0].sendall(pickle.dumps(request))
			print("balance at 91")
			balance = c2c_connections[0].recv(1024)
			print("Balance is " + str(balance))
		else:
			reciever, amount = user_input.split()
			print(reciever)
			print(amount)
			transaction = Transaction(int(pid), int(reciever), int(amount))

			request = RequestMessage(pid,data.clock,"BALANCE")
			c2c_connections[0].sendall(pickle.dumps(request))
			balance = c2c_connections[0].recv(1024)

			print("balance now is : " + str(balance))

			if int(balance) >= int(amount):
				print("enter transaction 2")
				request = RequestMessage(pid,data.clock,"LAST_BLOCK")
				c2c_connections[0].send(pickle.dumps(request))
				last_blck_str = c2c_connections[0].recv(1024)
				last_blck = pickle.loads(last_blck_str)
				block = Block(hashlib.sha256(str(last_blck)).digest(), 
					Transaction(transaction.sender,transaction.reciever,transaction.amount))
				request = RequestMessage(pid,data.clock,"ADD_BLOCK", block)
				c2c_connections[0].send(pickle.dumps(request))

				message = c2c_connections[0].recv(1024)
				print("Transaction was " + str(message))
						
try:
	print("Connecting to server...")
	ClientSocket.connect((host, port))
	print("Connected")
except socket.error as e:
	print(str(e))

new_connection = Connections(ClientSocket)
new_connection.start()
c2c_connections[0] = ClientSocket

def getMutex(clock):
	msg = RequestMessage(pid, clock, "MUTEX")
	data_string = pickle.dumps(msg)
	broadcast(data_string)
	#ClientSocket.sendall(data_string)

def broadcast(data):
	if pid == 1:
		c2c_connections[2].sendall(data)
		c2c_connections[3].sendall(data)
	elif pid == 2:
		c2c_connections[1].sendall(data)
		c2c_connections[3].sendall(data)
	elif pid == 3:
		c2c_connections[1].sendall(data)
		c2c_connections[2].sendall(data)

if cport == 7001: 
	client2client = socket.socket()
	client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	client2client.bind((ip, 7010))
	client2client.listen(2)

	conn, client_address = client2client.accept()
	print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
	c2c_connections[2] = conn
	new_client = Connections(conn)
	new_client.start()

	conn, client_address = client2client.accept()
	print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
	c2c_connections[3] = conn
	new_client1 = Connections(conn)
	new_client1.start()

if cport == 7002:
	client2client = socket.socket()
	client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	client2client.bind((ip, 7020))
	
	try:
		client2client.connect((host, 7010))
	except socket.error as e:
		print(str(e))

	c2c_connections[1] = client2client
	new_connection = Connections(client2client)
	new_connection.start()

	client2client = socket.socket()
	client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	client2client.bind((ip, 7021))
	client2client.listen(2)

	conn, client_address = client2client.accept()
	print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
	c2c_connections[3] = conn
	new_client1 = Connections(conn)
	new_client1.start()

if cport == 7003:
	client2client = socket.socket()
	client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	client2client.bind((ip, 7030))
	
	try:
		client2client.connect((host, 7010))
	except socket.error as e:
		print(str(e))

	c2c_connections[1] = client2client
	new_connection = Connections(client2client)
	new_connection.start()

	client2client = socket.socket()
	client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	client2client.bind((ip, 7031))
	
	try:
		client2client.connect((host, 7021))
	except socket.error as e:
		print(str(e))

	c2c_connections[2] = client2client
	new_connection1 = Connections(client2client)
	new_connection1.start()

while True:
	user_input = raw_input()
	
	myClock.incrementClock()
	requestPriorityQueue.append(myClock)
	heapq.heapify(requestPriorityQueue)
	print ("Data clock at creation is " + str(myClock.clock))
	print ("\n Data PID at creation is " + str(myClock.pid))
	print(str(myClock))
	replyCount[str(myClock)] = 0
	
	getMutex(myClock)

	#server transac
	#ClientSocket.send(Input)
	#Response = self.connection.recv(1024)
	#print(Response)



ClientSocket.close()