
class ControlMachineStatus:
	status = None
	Px = None
	Py = None
	Pz = None

	def __init__(self, chatBackend):
		self._chatBackend = chatBackend

	def updateStatus(self):
		self._chatBackend.send("@X")
		res = self._chatBackend.getline()

		if res[0:2] != "@X":
			raise ValueError("Unexpected reply to @X command: " + res)

		self.status = res[2:]

		if self.status == "14" or self.Px == None:
			self.updateMachinePos("Px")
			self.updateMachinePos("Py")
			self.updateMachinePos("Pz")

	def updateMachinePos(self, direction):
		self._chatBackend.send("@" + direction)
		res = self._chatBackend.getline()

		if res[0:3] != "@" + direction.upper():
			raise ValueError("Unexpected reply to @" + direction + " command: " + res)

		setattr(self, direction, res[3:])
