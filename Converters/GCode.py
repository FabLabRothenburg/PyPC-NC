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

	def removeBlockSkipLines(self):
		def f(x):
			return x.strip()[0] != '/'
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

	def __init__(self):
		self.buffer = [ 'C08', 'D141', 'A50', 'A51', 'D141', 'W100', 'E' ]
		self.offsets = [ 10.000, 10.000, 10.000 ]
		self.position = [ 0, 0, 0 ]
		self.incrPosition = [ 10.000, 10.000, 10.000 ]
		self.stretch = 1.0
		self.end = False
		self.C = 8
		self.W = 100
		self.absDistanceMode = True
		self.firstMove = True

	def splitBlock(self, blockStr):
		instructions = []
		cur = []

		for i in blockStr.split(' '):
			if i == '': continue

			if cur and cur[0] in [ 'M3', 'M4' ] and i[0] == 'S':
				cur.append(i)
			elif i[0] in [ 'G', 'M', 'F', 'S', 'T' ]:
				if cur: instructions.append(cur)
				cur = [i]
			else:
				cur.append(i)

		if cur: instructions.append(cur)
		return instructions

	def process(self, insn):
		try:
			getattr(self, 'process%s' % insn[0])(insn)
		except AttributeError:
			raise RuntimeError('Unsupported G-Code instruction: %s' % insn[0])

	def processG20(self, insn):  # unit = inch
		self.stretch = 2.54

	def processG21(self, insn):  # unit = mm
		self.stretch = 1.00

	def processG90(self, insn):  # absolute distance mode
		self.absDistanceMode = True

	def processG91(self, insn):  # incremental distance mode
		self.absDistanceMode = False

	def processM30(self, insn):  # end program
		self.end = True

	def processM2(self, insn):  # end program
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

		if self.absDistanceMode:
			target = self._vectorAdd(move, self.offsets)
		else:
			target = self._vectorAdd(move, self.incrPosition)

		command = [ None ]
		dist = 0

		for i in xrange(3):
			if self.firstMove and not self.absDistanceMode and target[i] == None:
				target[i] = self.incrPosition[i]

			if target[i] != None and abs(target[i] - self.position[i]) > dist:
				command[0] = 'V%d' % (i + 1)
				dist = abs(target[i] - self.position[i])

			if target[i] != None and target[i] != self.position[i]:
				command.append('%s%d' % (self.axes[i], target[i] * 1000))

		if not rapid:
			command[0] = 'V21'
			if len(command) == 2 and command[1][0] == 'Z':
				command[1] = command[1].lower()

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
		else:
			if self.C == 8 and self.W == 100:
				# don't change C8 W100, whyever ...
				C = None
			else:
				C = 10
				W = 10
				twice = True

		if C and (C != self.C or W != self.W):
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

			# @fixme which one to pick!?
			xc = x1
			yc = y1

		else:
			i = self._getAddress('I', insn)
			j = self._getAddress('J', insn)

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

		if not radius:
			# if the center of the circle is specified directly,
			# the angle gamma may be larger than 180 deg;
			alpha = fAngle((xa - xc) / a, (ya - yc) / a)
			beta = fAngle((xb - xc) / a, (yb - yc) / a)

			if beta < alpha: beta += math.pi * 2
			if beta - alpha >= math.pi: gamma += math.pi

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
		alpha = math.acos(x)
		if y > 0: alpha = 2 * math.pi - alpha

		return alpha

	def angleCalcCCW(self, x, y):
		alpha = math.acos(x)
		if y < 0: alpha = 2 * math.pi - alpha

		return alpha
