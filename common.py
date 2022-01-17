class RequestMessage:
	def __init__(self, fromPid, clock, reqType):
		self.fromPid = fromPid
		self.clock = clock
		self.reqType = reqType

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