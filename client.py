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


myClock = LamportClock(0,pid)

requestPriorityQueue = [] 
replyCount = 0
c2c_connections = {}
transactionFlag = False

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
		global replyCount
		global requestPriorityQueue
		global transactionFlag
		while True:
			
			response = self.connection.recv(1024)

			data = pickle.loads(response)

			myClock.updateClock(data.clock)
			##print("Current clock of process " + str(pid) + " is " + str(myClock))

			if data.reqType == "MUTEX":
				requestPriorityQueue.append(LamportClock(data.clock.clock, data.clock.pid))
				heapq.heapify(requestPriorityQueue)
				print("Request recieved from " + str(data.fromPid))
				myClock.incrementClock()
				print("Reply sent to " + str(data.fromPid))
				##print("Current clock of process " + str(pid) + " is " + str(myClock))
				reply = RequestMessage(pid, myClock, "REPLY")

				self.connection.send(pickle.dumps(reply))
			
			if data.reqType == "REPLY":
				#print ("Data clock at REPLY is " + str(data.clock.clock))
				#print ("\n Data PID at REPLY is " + str(data.clock.pid))
				#print(str(data.clock))
				#for i in requestPriorityQueue:
				#	print("queue: " + str(i))
				#if pid == 2:
				#	time.sleep(5)
				print("Reply recieved from " + str(data.fromPid))
				replyCount += 1
				if replyCount == 2 and requestPriorityQueue[0].pid == pid:
					#print("Execute Transaction")
					#if pid == 2:
					#	time.sleep(10)
					self.handle_transaction(data)
					heapq.heappop(requestPriorityQueue)
					heapq.heapify(requestPriorityQueue)
					replyCount = 0
					release = RequestMessage(pid, myClock, "RELEASE")
					myClock.incrementClock()
					##print("Current clock of process " + str(pid) + " is " + str(myClock))
					broadcast(pickle.dumps(release))
					transactionFlag = True

			if data.reqType == "RELEASE":
				#print("Inside release")
				print("Release recieved from " + str(data.fromPid))
				heapq.heappop(requestPriorityQueue)
				heapq.heapify(requestPriorityQueue)
				if len(requestPriorityQueue) > 0 and requestPriorityQueue[0].pid == pid and replyCount == 2:
					#print("Execute Transaction")
					self.handle_transaction(data)
					heapq.heappop(requestPriorityQueue)
					heapq.heapify(requestPriorityQueue)
					replyCount = 0
					release = RequestMessage(pid, myClock, "RELEASE")
					myClock.incrementClock()
					##print("Current clock of process " + str(pid) + " is " + str(myClock))
					broadcast(pickle.dumps(release))
					transactionFlag = True

	def handle_transaction(self, data):
		if user_input == "BAL":
			request = RequestMessage(pid, myClock,"BALANCE")
			myClock.incrementClock()
			print("Balance request sent to server")
			##print("Current clock of process " + str(pid) + " is " + str(myClock))
			c2c_connections[0].sendall(pickle.dumps(request))
			#print("balance at 91")
			
			balance = c2c_connections[0].recv(1024)
			myClock.incrementClock()
			##print("Current clock of process " + str(pid) + " is " + str(myClock))
			print("Balance is " + str(balance))
			transactionFlag = True
		else:
			reciever, amount = user_input.split()
			
			transaction = Transaction(int(pid), int(reciever), int(amount))

			myClock.incrementClock()
			##print("Current clock of process " + str(pid) + " is " + str(myClock))
			print("Balance request sent to server")
			request = RequestMessage(pid,myClock,"BALANCE")
			c2c_connections[0].sendall(pickle.dumps(request))
			balance = c2c_connections[0].recv(1024)
			myClock.incrementClock()
			##print("Current clock of process " + str(pid) + " is " + str(myClock))
			print("Balance before transaction " + str(balance))

			if int(balance) >= int(amount):
				
				myClock.incrementClock()
				##print("Current clock of process " + str(pid) + " is " + str(myClock))
				request = RequestMessage(pid,myClock,"LAST_BLOCK")
				c2c_connections[0].send(pickle.dumps(request))
				last_blck_str = c2c_connections[0].recv(1024)
				
				myClock.incrementClock()
				##print("Current clock of process " + str(pid) + " is " + str(myClock))
				last_blck = pickle.loads(last_blck_str)
				block = Block(hashlib.sha256(str(last_blck)).digest(), 
					Transaction(transaction.sender,transaction.reciever,transaction.amount))
				request = RequestMessage(pid,data.clock,"ADD_BLOCK", block)

				myClock.incrementClock()
				##print("Current clock of process " + str(pid) + " is " + str(myClock))
				c2c_connections[0].send(pickle.dumps(request))

				message = c2c_connections[0].recv(1024)
				myClock.incrementClock()
				#print("Current clock of process " + str(pid) + " is " + str(myClock))
				print("Transaction was " + str(message))
				print("Balance after transaction " + str(int(balance) - int(amount)))
			else:
				print("Insufficient Balance, cannot proceed with the transaction")
			transactionFlag = True
						
try:
	ClientSocket.connect((host, port))
	print("Connected to server")
except socket.error as e:
	print(str(e))

#new_connection = Connections(ClientSocket)
#new_connection.start()
c2c_connections[0] = ClientSocket

def getMutex(clock):
	msg = RequestMessage(pid, clock, "MUTEX")
	data_string = pickle.dumps(msg)
	#time.sleep(5)
	broadcast(data_string)
	print("Sending MUTEX request to other clients")
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
		print('Connected to: ' + host + ':' + str(7010))
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
		print('Connected to: ' + host + ':' + str(7010))
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
		print('Connected to: ' + host + ':' + str(7021))
	except socket.error as e:
		print(str(e))

	c2c_connections[2] = client2client
	new_connection1 = Connections(client2client)
	new_connection1.start()

print("Current Balance is $10")

while True:
	transactionFlag = False
	print("=======================================")
	print("*For Balance - BAL")
	print("*For transferring money - RECV_ID AMOUNT Eg.(2 5)")
	print("*For quit - Q")
	print("=======================================")
	user_input = raw_input()

	if user_input != "Q" and user_input != "BAL" and len(user_input.split()) != 2:
		print("Please enter valid input")
		continue

	if user_input == "Q":
		break
	
	myClock.incrementClock()
	#print("Current clock of process " + str(pid) + " is " + str(myClock))
	requestPriorityQueue.append(LamportClock(myClock.clock, myClock.pid))
	heapq.heapify(requestPriorityQueue)
	#print ("Data clock at creation is " + str(myClock.clock))
	#print ("\n Data PID at creation is " + str(myClock.pid))
	#print(str(myClock))
	replyCount = 0
	
	getMutex(myClock)

	while transactionFlag == False:
		a=1
		# transaction response



def closeSockets():
	ClientSocket.close()
	if pid == 1:
		c2c_connections[2].close()
		c2c_connections[3].close()
	elif pid == 2:
		c2c_connections[1].close()
		c2c_connections[3].close()
	elif pid == 3:
		c2c_connections[1].close()
		c2c_connections[2].close()

closeSockets()