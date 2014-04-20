import re

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
		twice = False

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
			C = 8
			W = 10

			if len(command) == 2 and command[1][0] == 'Z':
				command[1] = command[1].lower()
		else:
			if self.C == 8 and self.W == 100:
				# don't change C8 W100, whyever ...
				C = None
			else:
				C = 10
				W = 10
				twice = True

		if len(command) < 2:
			return

		self.buffer.append('E')

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

		self.buffer.append(','.join(command))
		self._mergeIntoPosition(target)
		self.firstMove = False

	def processG0(self, insn):  # rapid motion
		self._straightMotion(insn, True)

	def processG1(self, insn):  # coordinated motion
		self._straightMotion(insn, False)
