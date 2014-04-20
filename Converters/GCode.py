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
	offset = [ 10000, 10000, 2500 ]
	position = [ 0, 0, 0 ]
	stretch = 1.0
	end = False

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

	def processM30(self, insn):  # end program
		self.end = True

	def processM2(self, insn):  # end program
		self.end = True
