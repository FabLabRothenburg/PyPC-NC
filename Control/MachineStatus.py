from PySide import QtGui, QtCore

class ControlMachineStatus(QtCore.QObject):
	status = None
	pX = None
	pY = None
	pZ = None
	pU = None
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
			self.pX = self.fetchMachinePos("PX")
			self.pY = self.fetchMachinePos("PY")
			self.pZ = self.fetchMachinePos("PZ")
			self.pU = self.fetchMachinePos("PU")

		self.statusUpdated.emit()

	def fetchMachinePos(self, direction):
		self._chatBackend.send("@" + direction)
		res = self._chatBackend.getline()

		if res[0:3] != "@" + direction.upper():
			raise ValueError("Unexpected reply to @" + direction + " command: " + res)
		return float(res[3:])

        @QtCore.Slot()
        def stop(self):
                self._chatBackend.send('@B')

	@QtCore.Slot()
	def refMovement(self):
		commands = [
			'@M0',
			'#DX,0,90,94,90',
			'#DY,0,91,95,91',
			'#DZ,0,92,96,92',
			'#G90,15000',
			'#G91,15000',
			'#G92,10000',
			'#G94,2000',
			'#G95,2000',
			'#G96,2000',
			'#DU,0,93,97,93',
			'#G93,10000',
			'#G97,1000',
			'#OU,0',
			'#W',
			'@M1',
			'$A00',
			'@M1',
			'@D08',
			'$HZXY',
		]

		for command in commands:
			self._chatBackend.send(command, '')

