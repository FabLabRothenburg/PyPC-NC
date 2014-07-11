from PySide import QtGui, QtCore
from Converters import GCode, CNCCon, Filters

class MachineController(QtCore.QObject):
	_action = None

	def __init__(self, chatBackend):
		QtCore.QObject.__init__(self)
		self._chatBackend = chatBackend
		self._machineStatus = MachineStatusController(self)

	def machineStatus(self):
		return self._machineStatus

	def cts(self):
		while self._chatBackend.hasLines():
			msg = self._chatBackend.getline()
			if msg == "\001":
				print "SOH"
			elif msg == "\004":
				print "EOT"
			else:
				print "not processed reply: %s" % msg

	def send(self, sendStr, expectStr = None):
		self._chatBackend.send(sendStr, expectStr)

	def sendList(self, commands):
		for command in commands:
			self.cts()
			self.send(command, '')

	def sendAndRead(self, sendStr):
		self.cts()
		self.send(sendStr)
		return self._chatBackend.getline()

        @QtCore.Slot()
        def stop(self):
                self.send('@B')

	def action(self):
		return self._action

	def setAction(self, action):
		self._action = action


class MachineStatusController(QtCore.QObject):
	statusUpdated = QtCore.Signal()

	_status = None
	_axes = [ 'X', 'Y', 'Z', 'U' ]
	_pos = [ None, None, None, None ]
	_moving = [ False, False, False, False ]

	def __init__(self, machine):
		QtCore.QObject.__init__(self)
		self._machine = machine
                self._timer = QtCore.QTimer(self)
                self.connect(self._timer, QtCore.SIGNAL("timeout()"), self.updateStatus)
                self._timer.start(1000)

	def setAxisMoving(self, axis, value = True):
		self._moving[self._axes.index(axis)] = value

	def setXYZMoving(self, value = True):
		self._moving = [ value, value, value, self._moving[3] ]

	def setAllMoving(self, value = True):
		self._moving = [ value, value, value, value ]

        @QtCore.Slot()
	def updateStatus(self):
		res = self._machine.sendAndRead('@X')
		if res[0:2] != "@X": raise ValueError("Unexpected reply to @X command: " + res)
		self._status = int(res[2:], 16)

		for i in xrange(4):
			axis = self._axes[i]
			if self._pos[i] == None or self._moving[i]:
				res = self._machine.sendAndRead('@P' + axis)
				if res[0:3] != "@P" + axis:
					raise ValueError("Unexpected reply to @P" + axis + " command: " + res)
				self._pos[i] = float(res[3:])

		self.statusUpdated.emit()

		if not (self._status & 0x10):
			self.setAllMoving(False)

	def status(self): return self._status
	def x(self): return self._pos[0]
	def y(self): return self._pos[1]
	def z(self): return self._pos[2]
	def u(self): return self._pos[3]



class ReferenceMotionController(QtCore.QObject):
	def __init__(self, machine):
		QtCore.QObject.__init__(self)
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
		self._machine = machine
		self._machine.sendList(commands)
		self._machine.machineStatus().setXYZMoving()


class ManualMotionController(QtCore.QObject):
	def __init__(self, machine):
		QtCore.QObject.__init__(self)
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
		self._machine = machine
		self._machine.sendList(commands)

	def singleStep(self, axis, positive, fast):
		axisToSpeed = { 'X': 80, 'Y': 81, 'Z': 82, 'U': 83 }
		speed = axisToSpeed[axis];
		if not fast: speed += 4

		steps = 1 if positive else -1
		self._machine.cts()
		self._machine.send('$L%2d,%s%d' % (speed, axis.lower(), steps), '')
		self._machine.machineStatus().setAxisMoving(axis)

	def manualMove(self, axis, positive, distance, fast):
		axisToSpeed = { 'X': 80, 'Y': 81, 'Z': 82, 'U': 83 }
		speed = axisToSpeed[axis];
		if not fast: speed += 4

		steps = distance if positive else -distance
		self._machine.cts()
		self._machine.send('$E%2d,%s%d' % (speed, axis.lower(), steps), '')
		self._machine.machineStatus().setAxisMoving(axis)

	def gotoXYZ(self, x, y, z = None):
		steps = []

		if x != None:
			dist = x - self._machine.machineStatus().x()
			if dist:
				steps.append('x%d' % dist)
				self._machine.machineStatus().setAxisMoving('X')

		if y != None:
			dist = y - self._machine.machineStatus().y()
			if dist:
				steps.append('y%d' % dist)
				self._machine.machineStatus().setAxisMoving('Y')

		if z != None:
			dist = z - self._machine.machineStatus().z()
			if dist:
				steps.append('z%d' % dist)
				self._machine.machineStatus().setAxisMoving('Z')

		if not steps: return
		self._machine.cts()
		self._machine.send('$E80,' + ','.join(steps))



class ProgrammedMotionController(QtCore.QObject):
	_completedSteps = 0
	_sentSteps = 0
	_totalSteps = 0
	_feedRateOverride = 100

	def __init__(self, machine):
		QtCore.QObject.__init__(self)
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
			'@O%d' % self._feedRateOverride,
		]
		self._machine = machine
		self._machine.sendList(commands)

	def completedSteps(self): return self._completedSteps
	def totalSteps(self): return self._totalSteps

	def setFeedRateOverride(self, i):
		self._feedRateOverride = i
		self._machine.send("@O%d" % self._feedRateOverride)

        @QtCore.Slot()
	def updateStatus(self):
		res = self._machine.sendAndRead('@N')
		if res[0:2] != '@N':
			raise ValueError('Unexpected reply to @N command: ' + res)
		self._completedSteps = float(res[2:])

		if self._machine.machineStatus().status() & 0x10:
			self._run()
		else:
			self._end()

	def setCommands(self, commands):
		self._buffer = commands
		for command in self._buffer:
			if command == 'E': self._totalSteps += 1

		self._timer = QtCore.QTimer(self)
		self.connect(self._timer, QtCore.SIGNAL("timeout()"), self.updateStatus)
		self._timer.start(1000)

		self._machine.machineStatus().setXYZMoving()
		self._run()

	def _run(self):
		if self._completedSteps + 250 < self._sentSteps:
			return	# machine still has work to do; don't send yet

		while len(self._buffer) and self._sentSteps - self._completedSteps < 2000:
			command = self._buffer.pop(0)
			if command == 'E': self._sentSteps += 1

			print "sent %d of %d; current N: %d; next command: %s" % (self._sentSteps, self._totalSteps, self._completedSteps, command)
			self._machine.cts()
			self._machine.send(command)

	def _end(self):
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
			self._machine.cts()
			self._machine.send(command)

		self._timer.stop()
		self._machine.setAction(None)
