import socket, pickle
from common import *
import heapq
import hashlib

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


ClientSocket = socket.socket()
ClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ClientSocket.bind((ip, cport))
host = '127.0.0.1'
port = 7000
user_input = ""

try:
	print("Connecting to server...")
	ClientSocket.connect((host, port))
	print("Connected")
except socket.error as e:
	print(str(e))

class Connections(Thread):
	def __init__(self,connection):
		Thread.__init__(self)
		self.connection = connection

	def run(self):
		while True:
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
				print ("Data clock at REPLY is " + str(data.clock.clock))
				print ("\n Data PID at REPLY is " + str(data.clock.pid))
				print(str(data.clock))
				replyCount[str(data.clock)] += 1
				if replyCount[str(data.clock)] == 1 and requestPriorityQueue[0].pid == pid:
					print("Execute Transaction")
					self.handle_transaction(data)
					heapq.heappop(requestPriorityQueue)
					release = RequestMessage(pid, data.clock, "RELEASE")
					self.connection.send(pickle.dumps(release))

			if data.reqType == "RELEASE":
				print("Inside release")
				heapq.heappop(requestPriorityQueue)
				if len(requestPriorityQueue) > 0 and requestPriorityQueue[0].pid == pid and replyCount[str(requestPriorityQueue[0])] == 1:
					print("Execute Transaction")
					self.handle_transaction(data)
					heapq.heappop(requestPriorityQueue)
					release = RequestMessage(pid, data.clock, "RELEASE")
					self.connection.send(pickle.dumps(release))

	def handle_transaction(self, data):
		if user_input == "BAL":
			request = RequestMessage(pid,data.clock,"BALANCE")
			self.connection.send(pickle.dumps(request))
			balance = self.connection.recv(1024)
			print("Balance is " + str(balance))
		else:
			reciever, amount = user_input.split()
			print(reciever)
			print(amount)
			transaction = Transaction(int(pid), int(reciever), int(amount))

			request = RequestMessage(pid,data.clock,"BALANCE")
			self.connection.send(pickle.dumps(request))
			balance = self.connection.recv(1024)

			print("balance now is : " + str(balance))

			if int(balance) >= int(amount):
				print("enter transaction 2")
				request = RequestMessage(pid,data.clock,"LAST_BLOCK")
				self.connection.send(pickle.dumps(request))
				last_blck_str = self.connection.recv(1024)
				last_blck = pickle.loads(last_blck_str)
				block = Block(hashlib.sha256(str(last_blck)).digest(), 
					Transaction(transaction.sender,transaction.reciever,transaction.amount))
				request = RequestMessage(pid,data.clock,"ADD_BLOCK", block)
				self.connection.send(pickle.dumps(request))

				message = self.connection.recv(1024)
				print("Transaction was " + str(message))
						


new_connection = Connections(ClientSocket)
new_connection.start()

def getMutex(clock):
	msg = RequestMessage(pid, clock, "MUTEX")
	data_string = pickle.dumps(msg)
	ClientSocket.sendall(data_string)

while True:
	#print("Enter the operation you want to perform...\n")
	##print("Enter BAL for balance \n")
	#print("Enter RECIEVER AMOUNT for Transaction \n")
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