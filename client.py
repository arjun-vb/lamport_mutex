import sys
import socket
import pickle
import heapq
import hashlib
import time

from threading import Thread
from common import *


myClock = LamportClock(0,0)
pid = 0
requestPriorityQueue = [] 
replyCount = 0
c2c_connections = {}
transactionFlag = False
user_input = ""
buff_size = 1024

class Connections(Thread):
	def __init__(self,connection):
		Thread.__init__(self)
		self.connection = connection

	def run(self):
		global replyCount
		global requestPriorityQueue
		global transactionFlag
		global myClock

		while True:
			
			response = self.connection.recv(buff_size)

			data = pickle.loads(response)

			myClock.updateClock(data.clock)
			#print("Current clock of process " + str(pid) + " is " + str(myClock))

			if data.reqType == "MUTEX":
				requestPriorityQueue.append(LamportClock(data.reqClock.clock, data.reqClock.pid))
				heapq.heapify(requestPriorityQueue)
				print("REQUEST recieved from " + str(data.fromPid) + " at " + str(myClock))
				myClock.incrementClock()
				sleep()
				print("REPLY sent to " + str(data.fromPid) + " at " + str(myClock))
				#print("Current clock of process " + str(pid) + " is " + str(myClock))
				reply = RequestMessage(pid, myClock, "REPLY")
				self.connection.send(pickle.dumps(reply))
				
			
			if data.reqType == "REPLY":
				#if pid == 2:
				#	time.sleep(5)
				print("REPLY recieved from " + str(data.fromPid) + " at " + str(myClock))
				replyCount += 1
				if replyCount == 2 and requestPriorityQueue[0].pid == pid:
					#print("Execute Transaction")
					#if pid == 2:
					#	time.sleep(10)
					print("Local Queue:")
					for i in requestPriorityQueue:
						print(str(i))
					self.handle_transaction(data)
					heapq.heappop(requestPriorityQueue)
					heapq.heapify(requestPriorityQueue)
					replyCount = 0
					#release = RequestMessage(pid, myClock, "RELEASE")
					#myClock.incrementClock()
					#print("Current clock of process " + str(pid) + " is " + str(myClock))
					#print("Sending RELEASE to all clients")
					broadcast("RELEASE")
					transactionFlag = True

			if data.reqType == "RELEASE":
				#print("Inside release")
				print("Local Queue:")
				for i in requestPriorityQueue:
					print(str(i))
				print("RELEASE recieved from " + str(data.fromPid) + " at " + str(myClock))
				heapq.heappop(requestPriorityQueue)
				heapq.heapify(requestPriorityQueue)
				if len(requestPriorityQueue) > 0 and requestPriorityQueue[0].pid == pid and replyCount == 2:
					#print("Execute Transaction")
					self.handle_transaction(data)
					heapq.heappop(requestPriorityQueue)
					heapq.heapify(requestPriorityQueue)
					replyCount = 0
					#release = RequestMessage(pid, myClock, "RELEASE")
					#myClock.incrementClock()
					#print("Current clock of process " + str(pid) + " is " + str(myClock))
					#print("Sending RELEASE to all clients")
					broadcast("RELEASE")
					transactionFlag = True

	def handle_transaction(self, data):
		if user_input == "BAL":
			request = RequestMessage(pid, myClock,"BALANCE")
			myClock.incrementClock()
			sleep()
			print("Balance request sent to server" + " at " + str(myClock))
			#print("Current clock of process " + str(pid) + " is " + str(myClock))
			c2c_connections[0].sendall(pickle.dumps(request))
			#print("balance at 91")
			
			balance = c2c_connections[0].recv(buff_size)
			myClock.incrementClock()
			#print("Current clock of process " + str(pid) + " is " + str(myClock))
			sleep()
			print("=============================")
			print("Balance is " + str(balance))
			print("=============================")
			#transactionFlag = True
		else:
			reciever, amount = user_input.split()
			
			transaction = Transaction(int(pid), int(reciever), int(amount))

			myClock.incrementClock()
			#print("Current clock of process " + str(pid) + " is " + str(myClock))
			sleep()
			print("Balance request sent to server" + " at " + str(myClock))
			request = RequestMessage(pid,myClock,"BALANCE")
			c2c_connections[0].sendall(pickle.dumps(request))
			balance = c2c_connections[0].recv(buff_size)
			myClock.incrementClock()
			#print("Current clock of process " + str(pid) + " is " + str(myClock))
			sleep()
			print("======================================")
			print("Balance before transaction " + str(balance))

			if int(balance) >= int(amount):
				
				myClock.incrementClock()
				#print("Current clock of process " + str(pid) + " is " + str(myClock))
				request = RequestMessage(pid,myClock,"LAST_BLOCK")
				c2c_connections[0].send(pickle.dumps(request))
				last_blck_str = c2c_connections[0].recv(buff_size)
				
				myClock.incrementClock()
				#print("Current clock of process " + str(pid) + " is " + str(myClock))
				last_blck = pickle.loads(last_blck_str)
				block = Block(hashlib.sha256(str(last_blck)).digest(), 
					Transaction(transaction.sender,transaction.reciever,transaction.amount))
				request = RequestMessage(pid,data.clock,"ADD_BLOCK", None, block)

				myClock.incrementClock()
				#print("Current clock of process " + str(pid) + " is " + str(myClock))
				c2c_connections[0].send(pickle.dumps(request))

				message = c2c_connections[0].recv(buff_size)
				myClock.incrementClock()
				#print("Current clock of process " + str(pid) + " is " + str(myClock))
				print("Transaction was " + str(message))
				print("Balance after transaction " + str(int(balance) - int(amount)))
				print("======================================")
			else:
				print("Insufficient Balance")
				print("======================================")
			#transactionFlag = True
						

def sleep():
	time.sleep(3)

def sendRequest(client, reqType, reqClock):
	myClock.incrementClock()
	#print("Current clock of process " + str(pid) + " is " + str(myClock))
	sleep()
	if reqType == "MUTEX":
		print("REQUEST sent to " + str(client) + " at " + str(myClock))
	elif reqType == "RELEASE":
		print("RELEASE sent to " + str(client) + " at " + str(myClock))

	msg = RequestMessage(pid, myClock, reqType, reqClock)
	data_string = pickle.dumps(msg)
	c2c_connections[client].sendall(data_string)
	


def broadcast(reqType, reqClock = None):
	if pid == 1:
		sendRequest(2,reqType,reqClock)
		sendRequest(3,reqType,reqClock)	
	elif pid == 2:		
		sendRequest(1,reqType,reqClock)
		sendRequest(3,reqType,reqClock)
	elif pid == 3:		
		sendRequest(1,reqType,reqClock)
		sendRequest(2,reqType,reqClock)

def closeSockets():
	c2c_connections[0].close()
	if pid == 1:
		c2c_connections[2].close()
		c2c_connections[3].close()
	elif pid == 2:
		c2c_connections[1].close()
		c2c_connections[3].close()
	elif pid == 3:
		c2c_connections[1].close()
		c2c_connections[2].close()


def main():
	ip = '127.0.0.1'
	server_port = 7000
	client_port = 0
	global pid
	global user_input
	global myClock
	global replyCount
	global transactionFlag

	if sys.argv[1] == "p1":
		client_port = 7001
		pid = 1
	elif sys.argv[1] == "p2":
		client_port = 7002
		pid = 2
	elif sys.argv[1] == "p3":
		client_port = 7003
		pid = 3
	else:
		print("Enter valid process id")
		exit()

	ClientSocket = socket.socket()
	ClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	ClientSocket.bind((ip, client_port))

	myClock = LamportClock(0,pid)
	try:
		ClientSocket.connect((ip, server_port))
		print("Connected to server")
	except socket.error as e:
		print(str(e))

	c2c_connections[0] = ClientSocket

	if client_port == 7001: 
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
		new_client = Connections(conn)
		new_client.start()

	if client_port == 7002:
		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7020))
		
		try:
			client2client.connect((ip, 7010))
			print('Connected to: ' + ip + ':' + str(7010))
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

	if client_port == 7003:
		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7030))
		
		try:
			client2client.connect((ip, 7010))
			print('Connected to: ' + ip + ':' + str(7010))
		except socket.error as e:
			print(str(e))

		c2c_connections[1] = client2client
		new_connection = Connections(client2client)
		new_connection.start()

		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7031))
		
		try:
			client2client.connect((ip, 7021))
			print('Connected to: ' + ip + ':' + str(7021))
		except socket.error as e:
			print(str(e))

		c2c_connections[2] = client2client
		new_connection1 = Connections(client2client)
		new_connection1.start()

	print("=======================================================")
	print("Current Balance is $10")

	while True:
		transactionFlag = False
		print("=======================================================")
		print("| For Balance type 'BAL'                              |")
		print("| For transferring money - RECV_ID AMOUNT Eg.(2 5)    |")
		#print("| To quit type 'Q'                                    |") 
		print("=======================================================")
		user_input = raw_input()

		if user_input != "Q" and user_input != "BAL" and len(user_input.split()) != 2:
			print("Please enter valid input")
			continue

		if user_input == "Q":
			break
		
		myClock.incrementClock()
		#print("Current clock of process " + str(pid) + " is " + str(myClock))
		requestClock = LamportClock(myClock.clock, myClock.pid)
		requestPriorityQueue.append(requestClock)
		heapq.heapify(requestPriorityQueue)
		replyCount = 0
		
		broadcast("MUTEX", requestClock)

		while transactionFlag == False:
			a=1


	closeSockets()

if __name__ == "__main__":
    main()

