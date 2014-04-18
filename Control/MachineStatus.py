from PySide import QtGui, QtCore

class ControlMachineStatus(QtCore.QObject):
	status = None
	pX = None
	pY = None
	pZ = None
	wpX = 1000
	wpY = 1000
	wpZ = 0

	statusUpdated = QtCore.Signal()

	def __init__(self, chatBackend):
		QtCore.QObject.__init__(self)
		self._chatBackend = chatBackend

                self._timer = QtCore.QTimer(self)
                self.connect(self._timer, QtCore.SIGNAL("timeout()"), self.updateStatus)
                self._timer.start(1000)

        @QtCore.Slot()
	def updateStatus(self):
		self._chatBackend.send("@X")
		res = self._chatBackend.getline()

		if res[0:2] != "@X":
			raise ValueError("Unexpected reply to @X command: " + res)
		self.status = int(res[2:])

		if self.status == "14" or self.pX == None:
			self.pX = self.fetchMachinePos("Px")
			self.pY = self.fetchMachinePos("Py")
			self.pZ = self.fetchMachinePos("Pz")

		self.statusUpdated.emit()

	def fetchMachinePos(self, direction):
		self._chatBackend.send("@" + direction)
		res = self._chatBackend.getline()

		if res[0:3] != "@" + direction.upper():
			raise ValueError("Unexpected reply to @" + direction + " command: " + res)
		return float(res[3:])

