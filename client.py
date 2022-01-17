import socket, pickle
from common import *
import heapq

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
					release = RequestMessage(pid, data.clock, "RELEASE")
					self.connection.send(pickle.dumps(release))

			if data.reqType == "RELEASE":
				print("Inside release")
				heapq.heappop(requestPriorityQueue)
				if len(requestPriorityQueue) > 0 and replyCount[str(requestPriorityQueue[0])] == 1 and requestPriorityQueue[0].pid == pid:
					print("Execute Transaction")
					release = RequestMessage(pid, data.clock, "RELEASE")
					self.connection.send(pickle.dumps(release))


			#print(Response)

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

def getMutex(clock):
	msg = RequestMessage(pid, clock, "MUTEX")
	data_string = pickle.dumps(msg)
	ClientSocket.sendall(data_string)

while True:
	Input = raw_input('Say Something: ')
	
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