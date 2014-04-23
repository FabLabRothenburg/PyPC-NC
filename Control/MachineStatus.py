from PySide import QtGui, QtCore
from Converters import GCode

class ControlMachineStatus(QtCore.QObject):
	status = None
	pX = None
	pY = None
	pZ = None
	pU = None
	wpX = 1000
	wpY = 1000
	wpZ = 0
	movingX = False
	movingY = False
	movingZ = False
	movingU = False
	_preparedManualMove = False
	_programmedMotionActive = False

	statusUpdated = QtCore.Signal()

	def __init__(self, chatBackend):
		QtCore.QObject.__init__(self)
		self._chatBackend = chatBackend

                self._timer = QtCore.QTimer(self)
                self.connect(self._timer, QtCore.SIGNAL("timeout()"), self.updateStatus)
                self._timer.start(1000)

        @QtCore.Slot()
	def updateStatus(self):
		self.cts()
		self._chatBackend.send("@X")
		res = self._chatBackend.getline()

		if res[0:2] != "@X":
			raise ValueError("Unexpected reply to @X command: " + res)
		self.status = int(res[2:], 16)

		if self.pX == None or self.movingX:
			self.pX = self.fetchMachinePos("PX")
		if self.pY == None or self.movingY:
			self.pY = self.fetchMachinePos("PY")
		if self.pZ == None or self.movingZ:
			self.pZ = self.fetchMachinePos("PZ")
		if self.pU == None or self.movingU:
			self.pU = self.fetchMachinePos("PU")

		self.statusUpdated.emit()

		if (self.status & 0x10) == 0:
			self.movingX = False
			self.movingY = False
			self.movingZ = False
			self.movingU = False

			if self._programmedMotionActive:
				self.endProgrammedMotion()

	def fetchMachinePos(self, direction):
		self.cts()
		self._chatBackend.send("@" + direction)
		res = self._chatBackend.getline()

		if res[0:3] != "@" + direction.upper():
			raise ValueError("Unexpected reply to @" + direction + " command: " + res)
		return float(res[3:])

	def cts(self):
		while self._chatBackend.hasLines():
			msg = self._chatBackend.getline()
			if msg == "\001":
				print "SOH"
			elif msg == "\004":
				print "EOT"
			else:
				print "not processed reply: %s" % msg

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
			self.cts()
			self._chatBackend.send(command, '')
		self.movingX = True
		self.movingY = True
		self.movingZ = True

	@QtCore.Slot()
	def storeXY(self):
		self.wpX = self.pX
		self.wpY = self.pY

	@QtCore.Slot()
	def storeXYZ(self):
		self.wpX = self.pX
		self.wpY = self.pY
		self.wpZ = self.pZ

	@QtCore.Slot()
	def storeX(self):
		self.wpX = self.pX

	@QtCore.Slot()
	def storeY(self):
		self.wpY = self.pY

	@QtCore.Slot()
	def storeZ(self):
		self.wpZ = self.pZ

	def gotoWorkpiece(self, fast, x, y, z):
		if not self._preparedManualMove:
			self.prepareManualMove()

		steps = []
		if x and self.wpX != self.pX:
			steps.append('x%d' % (self.wpX - self.pX))
			self.movingX = True
		if y and self.wpY != self.pY:
			steps.append('y%d' % (self.wpY - self.pY))
			self.movingY = True
		if z and self.wpZ != self.pZ:
			steps.append('z%d' % (self.wpZ - self.pZ))
			self.movingZ = True

		if not steps:
			return

		self.cts()
		self._chatBackend.send('$E80,' + ','.join(steps))

	def prepareManualMove(self):
		commands = [
			'@M0',
			'#G80,15000',
			'#G81,15000',
			'#G82,10000',
			'#G83,10000',
			'#G84,2000',
			'#G85,2000',
			'#G86,2000',
			'#G87,1000',
			'@M1',
		]
		for command in commands:
			self.cts()
			self._chatBackend.send(command, '')
		self._preparedManualMove = True

	def singleStep(self, axis, positive, fast):
		if not self._preparedManualMove:
			self.prepareManualMove()

		axisToSpeed = { 'X': 80, 'Y': 81, 'Z': 82, 'U': 83 }
		speed = axisToSpeed[axis];
		if not fast: speed += 4

		steps = 1 if positive else -1
		self.cts()
		self._chatBackend.send('$L%2d,%s%d' % (speed, axis.lower(), steps), '')

		setattr(self, 'p' + axis, None)

	def manualMove(self, axis, positive, distance, fast):
		if not self._preparedManualMove:
			self.prepareManualMove()

		axisToSpeed = { 'X': 80, 'Y': 81, 'Z': 82, 'U': 83 }
		speed = axisToSpeed[axis];
		if not fast: speed += 4

		steps = distance if positive else -distance
		self.cts()
		self._chatBackend.send('$E%2d,%s%d' % (speed, axis.lower(), steps), '')

		setattr(self, 'moving' + axis, True)

	def startProgrammedMotion(self):
		commands = [
			'@M0',
			'#G11,5000',
			'#E21,5000,30',
			'#E41,10000,30',
			'#G31,10000',
			'#G1,15000',
			'#G4,3000',
			'#G2,15000',
			'#G5,3000',
			'#G3,10000',
			'#G6,2000',
			'#G7,10000',
			'#G8,2000',
			'#C2,9',
			'#C14,17',
			'#C43,1',
			'@N0',
			'@M2',
		]

		for command in commands:
			self.cts()
			self._chatBackend.send(command, '')

		self._preparedManualMove = False
		self._programmedMotionActive = True
		self.movingX = True
		self.movingY = True
		self.movingZ = True

	def endProgrammedMotion(self):
		commands = [
			'@@',
			'@M2',
			'D0',
			'A60',
			'Q100,0',
			'Q101,0',
			'Q102,0',
			'Q103,0',
			'Q104,0',
			'Q105,0',
			'Q106,0',
			'Q107,0',
			'W100',
			'A40',
		]

		for command in commands:
			self.cts()
			self._chatBackend.send(command)

		self._programmedMotionActive = False


	def importGCode(self, fname):
		parser = GCode.GCodeParser()
		parser.readFile(fname)
		parser.removeTapeMarkers()
		parser.removeInlineComments()
		parser.removeBlockSkipLines()
		parser.normalizeAddressWhitespace()
		parser.readSequenceNumbers()

		inter = GCode.GCodeInterpreter()
		inter.offsets = [ self.wpX / 1000.0, self.wpY / 1000.0, self.wpZ / 1000.0 ]
		inter.position = [ self.pX / 1000.0, self.pY / 1000.0, self.pZ / 1000.0 ]
		inter.incrPosition = [ self.wpX / 1000.0, self.wpY / 1000.0, self.wpZ / 1000.0 ]
		inter.run(parser)

		self.startProgrammedMotion()

		for command in inter.buffer:
			self.cts()
			self._chatBackend.send(command)
