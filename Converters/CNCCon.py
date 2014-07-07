class CNCConWriter:
	axes = [ 'X', 'Y', 'Z' ]

	def __init__(self):
		self.buffer = [ 'C08', 'D141', 'A50', 'A51', 'D141', 'W100', 'E' ]
		self.C = 8
		self.D = 141
		self.W = 100
		self.spindleEnable = True
		self.spindleCCW = False
		self.initialW100Stickyness = True
		self.coolantEnable = False
		self.firstMove = True

	def appendPostamble(self):
		self.buffer.append('E')
		self.buffer.append('D0')

	def setFeedRate(self, fr):
		self.buffer.append('E')
		self.buffer.append('G21,%d' % fr)
		self.buffer.append('G20,%d' % fr)

	def setSpindleSpeed(self, speed):
		self.D = speed
		self.buffer.append('E')
		self.buffer.append('D%d' % self.D)
		self.buffer.append('W100')

	def appendEmptyStep(self):
		self.buffer.append('E')

	def setCoolantMist(self):
		self.buffer.append('E')
		if not self.coolantEnable:
			if not self.spindleEnable:
				self.buffer.append('A52')
			elif self.spindleCCW:
				self.buffer.append('AD3')
			else:
				self.buffer.append('A53')
		self.coolantEnable = True

	def setCoolantOff(self):
		self.buffer.append('E')
		if self.coolantEnable:
			if not self.spindleEnable:
				self.buffer.append('A50')
			elif self.spindleCCW:
				self.buffer.append('AD1')
			else:
				self.buffer.append('A51')
		self.coolantEnable = False

	def setSpindleSpeed(self, spindleCCW, spindleEnable, speed):
		# spindle speed setting of WinPC-NC writes W100 lines, however
		# the global W-state doesn't seem to be modified, at least
		# sub-sequent motions don't change W to the wanted value.
		#self.W = 100

		self.buffer.append('E')

		if self.spindleEnable and not spindleEnable:  # turn spindle off
			if self.spindleCCW:
				self.buffer.append('AD2' if self.coolantEnable else 'AD0')
			else:
				self.buffer.append('A52' if self.coolantEnable else 'A50')

		elif self.spindleCCW != spindleCCW or self.spindleEnable != spindleEnable:
			self.spindleCCW = spindleCCW
			if spindleCCW:
				self.buffer.append('AD3' if self.coolantEnable else 'AD1')
			else:
				self.buffer.append('A53' if self.coolantEnable else 'A51')

		if self.spindleEnable or not spindleEnable:
			# don't write E if spindle was off and now turned on (for what reason!??)
			self.buffer.append('E')

		self.spindleEnable = spindleEnable
		if not spindleEnable: return

		self.buffer.append('W100')

		if not speed: return
		D = min(255, round(speed * .0141))

		self.buffer.append('E')

		if self.D == D: return
		self.D = D

		self.buffer.append('D%d' % self.D)
		self.buffer.append('W100')

	def setSpeed(self, rapid):
		twice = False
		if not rapid:
			C = 8
			W = 10
			self.initialW100Stickyness = False
		else:
			if self.C == 8 and self.W == 100 and self.initialW100Stickyness:
				# don't change C8 W100, whyever ...
				return
			else:
				C = 10
				W = 10
				twice = True

		if C != self.C or W != self.W:
			if twice:
				self.buffer.append('C%02d' % C)
				self.buffer.append('W%d' % W)

			if not self.firstMove:
				self.buffer.append('E')

			self.buffer.append('C%02d' % C)
			self.buffer.append('W%d' % W)

			self.C = C
			self.W = W

	def straightMotion(self, rapid, longMoveAxe, machinePos):
		command = [ 'V%d' % (longMoveAxe + 1) ]
		if not rapid: command[0] = 'V21'

		for i in xrange(3):
			if machinePos[i] != None:
				command.append('%s%d' % (self.axes[i], machinePos[i]))

		self.buffer.append('E')
		self.setSpeed(rapid)
		self.buffer.append(','.join(command))
		self.firstMove = False

	def circleMotion(self, x, y, p):
		self.buffer.append('E')
		self.setSpeed(False)  # always "slow" motion
		self.buffer.append('K21,x%d,y%d,p%d' % (x, y, p))
		self.firstMove = False
