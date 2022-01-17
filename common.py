class RequestMessage:
	def __init__(self, fromPid, clock, reqType, block = None):
		self.fromPid = fromPid
		self.clock = clock
		self.reqType = reqType
		self.block = block

class LomportClock:
	def __init__(self, clock, pid):
		self.clock = clock
		self.pid = pid

	def incrementClock(self):
		self.clock += 1

	def __lt__(self, other):
		if self.clock < other.clock:
			return True
		elif self.clock == other.clock:
			if self.pid < other.pid:
				return True
			else:
				return False
		else:
			return False

	def __str__(self):
		return str(self.clock) + "." + str(self.pid)

class Transaction:
	def __init__(self, sender, reciever, amount):
		self.sender = sender
		self.reciever = reciever
		self.amount = amount

	def __str__(self):
		return str(self.sender) + "|" + str(self.reciever) + "|" + str(self.amount)

class Block:
	def __init__(self, headerHash, transaction):
		self.headerHash = headerHash
		self.transaction = transaction

	def __str__(self):
		return str(self.headerHash) + "|" + str(self.transaction)
