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
	buffer = [ 'C08', 'D141', 'A50', 'A51', 'D141', 'W100', 'E' ]
	offsets = [ 10.000, 10.000, 2.500 ]
	position = [ 0, 0, 0 ]
	stretch = 1.0
	end = False
	C = 8
	W = 100
	absDistanceMode = True

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

	def processG0(self, insn):  # rapid motion
		move = self._readAxes(insn)

		if self.absDistanceMode:
			target = self._vectorAdd(move, self.offsets)
		else:
			target = self._vectorAdd(move, self.position)

		command = None

		if target[0] != None and target[1] != None:
			if abs(target[0] - self.position[0]) > abs(target[1] - self.position[1]):
				command = [ 'V1' ]
			else:
				command = [ 'V2' ]

		if target[0] != None:
			if not command: command = [ 'V1' ]
			command.append('X%d' % (target[0] * 1000))

		if target[1] != None:
			if not command: command = [ 'V2' ]
			command.append('Y%d' % (target[1] * 1000))

		self.buffer.append('E')
		self.buffer.append(','.join(command))

