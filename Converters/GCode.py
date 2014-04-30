import re
import math

class GCodeParser:
	sequenceNumbers = { }

	def readString(self, string):
		self.lines = string.split('\n')
		while self.lines and self.lines[0] == '':
			self.lines.pop(0)
		while self.lines and self.lines[-1] == '':
			self.lines.pop()

	def readFile(self, fname):
		with open(fname) as f:
			self.lines = f.readlines()

		# trim lines
		def f(x):
			return x.strip()
		self.lines = map(f, self.lines)

		# filter empty lines
		def f(x):
			return len(x) > 0
		self.lines = filter(f, self.lines)

	def removeTapeMarkers(self):
		if self.lines and self.lines[0][0] == '%':
			self.lines.pop(0)
		if self.lines and self.lines[-1][0] == '%':
			self.lines.pop()

	def removeInlineComments(self):
		for i in xrange(0, len(self.lines)):
			while True:
				old = self.lines[i]
				self.lines[i] = re.sub(r'\s*\([^()]+\)\s*', ' ', old)
				if old == self.lines[i]:
					break

        def removeComments(self):
                def f(x): return re.sub(r'\s*;.*', '', x)
                self.lines = map(f, self.lines)

	def removeBlockSkipLines(self):
		def f(x):
			x = x.strip()
			return len(x) and x[0] != '/'
		self.lines = filter(f, self.lines)

	def normalizeAddressWhitespace(self):
		def f(x):
			return re.sub(r'\b([A-Z])\s*([0-9.-]+)\b', '\\1\\2', x)
		self.lines = map(f, self.lines)

	def readSequenceNumbers(self):
		for i in xrange(0, len(self.lines)):
			m = re.match(r'\s*N(\d+)\s*', self.lines[i])
			if not m: continue

			self.lines[i] = self.lines[i][m.end():]
			self.sequenceNumbers[int(m.group(1))] = i

class GCodeInterpreter:
	axes = [ 'X', 'Y', 'Z' ]
	motionGroup = [ 'G0', 'G1', 'G2', 'G3', 'G80', 'G81', 'G83' ]
	axesCommands = [ 'G0', 'G1', 'G2', 'G3', 'G81', 'G83' ]

	def __init__(self):
		self.buffer = [ 'C08', 'D141', 'A50', 'A51', 'D141', 'W100', 'E' ]
		self.offsets = [ 10.000, 10.000, 10.000 ]
		self.position = [ 0, 0, 0 ]
		self.incrPosition = [ 10.000, 10.000, 10.000 ]
		self.stretch = 1.0
		self.end = False
		self.C = 8
		self.D = 141
		self.W = 100
		self.absDistanceMode = True
		self.absArcDistanceMode = False
		self.firstMove = True
		self.parameters = { }
		self.plane = 'XY'
		self.spindleEnable = True
		self.spindleCCW = False
		self.initialW100Stickyness = True
		self.coolantEnable = False
		self.invertZ = False

	def run(self, parser):
		currentBlock = -1

		while not self.end:
			currentBlock += 1
			blockStr = parser.lines[currentBlock]

			if self.readParameters(blockStr):
				continue

			blockStr = self.substituteParameters(blockStr)
			commands = self.splitBlock(blockStr)

			for command in commands:
				self.process(command)

		self.buffer.append('E')
		self.buffer.append('D0')

	def splitBlock(self, blockStr):
		instructions = []
		cur = []
		axes = []
		axesCommandIndex = None

		for i in blockStr.split(' '):
			if i == '': continue

			if i[0] in self.axes:
				axes.append(i)
			elif cur and cur[0] in [ 'M3', 'M4' ] and i[0] == 'S':
				cur.append(i)
			elif cur and cur[0] in [ 'M6' ] and i[0] == 'T':
				cur.append(i)
			elif i[0] in [ 'G', 'M', 'F', 'S', 'T' ]:
				if cur: instructions.append(cur)
				if i in self.axesCommands:
					axesCommandIndex = len(cur)
				cur = [i]
			else:
				cur.append(i)

		if cur: instructions.append(cur)

		if axes:
			if axesCommandIndex == None:
				instructions.append([ self.currentMotionCommand ] + axes)
				pass
			else:
				instructions[axesCommandIndex] = instructions[axesCommandIndex] + axes

		return instructions

	def readParameters(self, blockStr):
		m = re.match(r'\s*#(\d+)\s*=\s*(.*?)\s*$', blockStr)
		if not m: return False

		key = int(m.group(1))

		if key < 1 or (key > 33 and key < 100) or (key > 199 and key < 500) or key > 999:
			raise RuntimeError('Parameter #%d is not writeable' % key)

		self.parameters[key] = self.evalExpression(m.group(2))
		return True

	def evalExpression(self, expr):
		m = re.match(r'-?[0-9\.]+$', expr)
		if not m:
			raise RuntimeError('Unsupported expression: %s' % expr)
		return float(expr)

	def substituteParameters(self, blockStr):
		while True:
			m = re.search(r'#(\d+)\b', blockStr)
			if not m: break

			key = int(m.group(1))

			if int(self.parameters[key]) == float(self.parameters[key]):
				subst = '%d' % (self.parameters[key])
			else:
				subst = '%f' % (self.parameters[key])

			blockStr = blockStr[:m.start()] + subst + blockStr[m.end():]
		return blockStr

	def process(self, insn):
		try:
			if insn[0] in self.motionGroup:
				self.currentMotionCommand = insn[0]

			if insn[0][0] == 'F':
				self.processF(insn)
			elif insn[0][0] == 'S':
				self.processS(insn)
			elif insn[0][0] == 'T':
				self.processT(insn)
			else:
				getattr(self, 'process%s' % insn[0].replace('.', '_'))(insn)
		except AttributeError:
			raise RuntimeError('Unsupported G-Code instruction: %s' % insn[0])

	def processF(self, insn):  # set feed rate in units per minute
		fr = float(self._getAddress('F', insn)) * self.stretch * 1000 / 60
		self.buffer.append('E')
		self.buffer.append('G21,%d' % fr)
		self.buffer.append('G20,%d' % fr)

        def processS(self, insn):  # set spindle speed
                self.D = min(255, round(float(self._getAddress('S', insn)) * .0141))
		self.buffer.append('E')
		self.buffer.append('D%d' % self.D)
		self.buffer.append('W100')

        def processT(self, insn):  # select tool
                pass

        def processG04(self, insn):  # dwell
                pass

	def processG17(self, insn):  # plane = XY
		self.plane = 'XY'

	def processG18(self, insn):  # plane = XZ
		self.plane = 'XZ'

	def processG19(self, insn):  # plane = YZ
		self.plane = 'YZ'

	def processG20(self, insn):  # unit = inch
		self.stretch = 25.4

	def processG21(self, insn):  # unit = mm
		self.stretch = 1.00

        def processG40(self, insn):  # disable tool radius compensation
                pass

        def processG49(self, insn):  # disable tool length compensation
                pass

        def processG54(self, insn):  # select coordinate system 1
                pass

        def processG61(self, insn):  # exact path mode
                pass

	def processG64(self, insn):  # path blending
		# not supported, i.e. also not handled by WinPC-NC
		pass

        def processG80(self, insn):  # cancel modal motion
                pass

	def processG90(self, insn):  # absolute distance mode
		self.absDistanceMode = True

	def processG90_1(self, insn):  # absolute arc distance mode
		self.absArcDistanceMode = True

	def processG91(self, insn):  # incremental distance mode
		self.absDistanceMode = False

	def processG91_1(self, insn):  # incremental arc distance mode
		self.absArcDistanceMode = False

	def processG98(self, insn):  # retract to prior position
		self.retractToOldZ = True

	def processG99(self, insn):  # retract to R position
		self.retractToOldZ = False

	def processM2(self, insn):  # end program
		self.end = True

	def processM3(self, insn):  # start spindle clockwise
		self._setSpindleSpeed(insn, False, True)

	def processM4(self, insn):  # start spindle ccw
		self._setSpindleSpeed(insn, True, True)

	def processM5(self, insn):  # stop spindle
		self._setSpindleSpeed(insn, None, False)

	def processM6(self, insn):  # tool change (not supported)
		self.buffer.append('E')

	def processM7(self, insn):  # coolant on "mist"
		self.buffer.append('E')
		if not self.coolantEnable:
			if not self.spindleEnable:
				self.buffer.append('A52')
			elif self.spindleCCW:
				self.buffer.append('AD3')
			else:
				self.buffer.append('A53')
		self.coolantEnable = True

	def processM8(self, insn):  # coolant on "flood"; equal behaviour in WinPC-NC
		self.processM7(insn)

	def processM9(self, insn):  # coolant off
		self.buffer.append('E')
		if self.coolantEnable:
			if not self.spindleEnable:
				self.buffer.append('A50')
			elif self.spindleCCW:
				self.buffer.append('AD1')
			else:
				self.buffer.append('A51')
		self.coolantEnable = False

	def _setSpindleSpeed(self, insn, spindleCCW, spindleEnable):
		# spindle speed setting of WinPC-NC writes W100 lines, however
		# the global W-state doesn't seem to be modified, at least
		# sub-sequent motions don't change W to the wanted value.
		#self.W = 100

		speed = None

		if spindleEnable:
                        S = self._getAddress('S', insn)

                        if S != None:
                                speed = int(S)
                                if speed: D = min(255, round(speed * .0141))

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

		self.buffer.append('E')

		if self.D == D: return
		self.D = D

		self.buffer.append('D%d' % self.D)
		self.buffer.append('W100')

	def processM30(self, insn):  # end program
		self.end = True

	def _readAxes(self, insn):
		words = [ 'X', 'Y', 'Z' ]
		values = [ None, None, None ]

		for i in xrange(len(words)):
			for j in insn:
				if j[0] == words[i]:
					values[i] = float(j[1:]) * self.stretch
					break
		return values

	def _vectorAdd(self, a, b):
		def f(a, b):
			if a == None or b == None:
				return None
			else:
				return a + b
		return map(f, a, b)

	def _mergeIntoPosition(self, pos):
		for i in xrange(3):
			if(pos[i] != None):
				self.position[i] = pos[i]
				self.incrPosition[i] = pos[i]

	def _straightMotion(self, insn, rapid):
		move = self._readAxes(insn)

		if self.invertZ and move[2] != None:
			move[2] = -move[2]

		if self.absDistanceMode:
			target = self._vectorAdd(move, self.offsets)
		else:
			target = self._vectorAdd(move, self.incrPosition)

		self._straightMotionToTarget(target, rapid)

	def _straightMotionToTarget(self, target, rapid):
		command = [ None ]
		dist = 0

		for i in xrange(3):
			if self.firstMove and not self.absDistanceMode and target[i] == None:
				target[i] = self.incrPosition[i]

			if target[i] != None and abs(target[i] - self.position[i]) > dist:
				command[0] = 'V%d' % (i + 1)
				dist = abs(target[i] - self.position[i])

			if target[i] != None and target[i] != self.position[i]:
				command.append('%s%d' % (self.axes[i], round(target[i] * 1000)))

		if not rapid:
			command[0] = 'V21'

		if len(command) < 2:
			return

		self.buffer.append('E')
		self._setSpeed(rapid)
		self.buffer.append(','.join(command))
		self._mergeIntoPosition(target)
		self.firstMove = False

	def _setSpeed(self, rapid):
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




	def processG0(self, insn):  # rapid motion
		self._straightMotion(insn, True)

	def processG1(self, insn):  # coordinated motion
		self._straightMotion(insn, False)

	def _getAddress(self, word, insn):
		for i in insn:
			if i[0] == word:
				return i[1:]

	def processG2(self, insn):  # CW circle
		self._circleMotion(insn, self.angleCalcCW, False)

	def processG3(self, insn):  # CCW circle
		self._circleMotion(insn, self.angleCalcCCW, True)

	def _calcInnerAngle(self, xa, ya, xb, yb, xc, yc, fAngle):
		# a = dist B-C
		a = math.sqrt((xb - xc) ** 2 + (yb - yc) ** 2)
		# b = dist C-A
		b = math.sqrt((xc - xa) ** 2 + (yc - ya) ** 2)

		if round(a - b, 3) != 0:
			raise RuntimeError('strange circle a=%f, b=%f', a, b)

		alpha = fAngle((xa - xc) / a, (ya - yc) / a)
		beta = fAngle((xb - xc) / a, (yb - yc) / a)

		if beta < alpha: beta += math.pi * 2

		return beta - alpha

	def _circleMotion(self, insn, fAngle, ccw):
		move = self._readAxes(insn)
		radius = self._getAddress('R', insn)

		if self.absDistanceMode:
			target = self._vectorAdd(move, self.offsets)
		else:
			target = self._vectorAdd(move, self.incrPosition)

		target[0] = round(target[0], 3)
		target[1] = round(target[1], 3)

		xa = self.position[0]
		ya = self.position[1]
		xb = target[0]
		yb = target[1]

		if radius:
			#
			# calculate potential center coords for circle
			# http://www.fachinformatiker.de/algorithmik/70902-kreismittelpunkt-berechnen.html
			#
			r = float(radius) ** 2

			a = -((-2 * ya) - (-2 * yb)) / ((-2 * xa) - (-2 * xb))
			b = -((xa * xa + ya * ya - r) - (xb * xb + yb * yb - r)) / ((-2 * xa) - (-2 * xb));
			p = (-2 * (xa - b) * a - 2 * ya) / (a * a + 1);
			q = ((xa - b) * (xa - b) + ya * ya - r) / (a * a + 1);
			y1 = -p / 2 + math.sqrt((p * p) / 4 - q);
			y2 = -p / 2 - math.sqrt((p * p) / 4 - q);
			x1 = a * y1 + b;
			x2 = a * y2 + b;

			k = self._calcInnerAngle(xa, ya, xb, yb, x1, y1, fAngle) < self._calcInnerAngle(xa, ya, xb, yb, x2, y2, fAngle)
			if float(radius) < 0: k = not k

			if k:
				xc = x1
				yc = y1
			else:
				xc = x2
				yc = y2

		else:
			i = self._getAddress('I', insn)
			j = self._getAddress('J', insn)

			if self.absArcDistanceMode:
				xc = self.offsets[0] + float(i) * self.stretch
				yc = self.offsets[1] + float(j) * self.stretch
			else:
				if i:
					xc = self.position[0] + float(i) * self.stretch
				else:
					xc = self.position[0]

				if j:
					yc = self.position[1] + float(j) * self.stretch
				else:
					yc = self.position[1]

		# a = dist B-C
		a = math.sqrt((xb - xc) ** 2 + (yb - yc) ** 2)
		# b = dist C-A
		b = math.sqrt((xc - xa) ** 2 + (yc - ya) ** 2)

		if round(a - b, 3) != 0:
			raise RuntimeError('strange circle a=%f, b=%f', a, b)

		# c = dist A-B
		c = math.sqrt((xa - xb) ** 2 + (ya - yb) ** 2)

		# law of cosine
		gamma = math.acos((a ** 2 + b ** 2 - c ** 2) / (2 * a * b))

		# if the center of the circle is specified directly,
		# the angle gamma may be larger than 180 deg;
		alpha = fAngle((xa - xc) / a, (ya - yc) / a)
		beta = fAngle((xb - xc) / a, (yb - yc) / a)

		if beta < alpha: beta += math.pi * 2
		if beta - alpha > math.pi: gamma += math.pi

		x = round((xc - xa) * 1000)
		y = round((yc - ya) * 1000)
		p = gamma * 1000000
		if not ccw: p = -p

		# WinPC-NC seems to always ceil the value, for whatever reason ...
		p = math.ceil(p)

		self.buffer.append('E')
		self._setSpeed(False)  # always "slow" motion
		self.buffer.append('K21,x%d,y%d,p%d' % (x, y, p))
		self._mergeIntoPosition(target)
		self.firstMove = False

	def angleCalcCW(self, x, y):
		x = round(x, 6)
		alpha = math.acos(x)
		if y > 0: alpha = 2 * math.pi - alpha

		return alpha

	def angleCalcCCW(self, x, y):
		x = round(x, 6)
		alpha = math.acos(x)
		if y < 0: alpha = 2 * math.pi - alpha

		return alpha

	def _processCannedCycle(self, insn, peck):
		move = self._readAxes(insn)
		oldZ = self.position[2]
		clearZ = float(self._getAddress('R', insn)) * self.stretch
		L = self._getAddress('L', insn)

		if L == None:
			L = 1
		else:
			L = int(L)

			if L < 1:
				raise ValueError('L of G81 must be a natural number')

		if peck:
			Q = self._getAddress('Q', insn)
			if Q == None: raise ValueError('Q of G83 not set')

			Q = float(Q)
			if Q <= 0:
				raise ValueError('Q of G83 must not be zero or negative')

		if self.absDistanceMode:
			target = self._vectorAdd(move, self.offsets)
			clearZ += self.offsets[2]
			Z = target[2]
		else:
			target = self.incrPosition
			clearZ += self.incrPosition[2]
			Z = clearZ + move[2]

		if oldZ < clearZ:
			oldZ = clearZ
			self._straightMotionToTarget([ None, None, clearZ ], True)

		for i in xrange(L):
			if not self.absDistanceMode:
				target = self._vectorAdd(move, target)

			self._straightMotionToTarget([ target[0], target[1], None ], True)
			self._straightMotionToTarget([ None, None, clearZ ], True)

			while True:
				if peck:
					targetZ = self.position[2] - Q
					if Z > targetZ: targetZ = Z
				else:
					targetZ = Z

				self._straightMotionToTarget([ None, None, targetZ ], False)
				if targetZ == Z: break

				if peck:
					self._straightMotionToTarget([ None, None, clearZ ], True)

					peckOffset = Q / 3
					if peckOffset > 0.1: peckOffset = 0.1

					peckZ = targetZ + peckOffset
					if peckZ > clearZ: peckZ = clearZ

					self._straightMotionToTarget([ None, None, peckZ ], True)

			self._straightMotionToTarget([ None, None, oldZ ], True)

	def processG81(self, insn):
		self._processCannedCycle(insn, False)

	def processG83(self, insn):
		self._processCannedCycle(insn, True)
