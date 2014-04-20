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
