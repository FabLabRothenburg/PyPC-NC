class FilterChain:
	def __init__(self, filters, writer):
		self.__dict__['_filters'] = filters
		self.__dict__['_writer'] = writer

	def __getattr__(self, name):
		return getattr(self.__dict__['_writer'], name)

	def __setattr__(self, name, value):
		setattr(self.__dict__['_writer'], name, value)

	def straightMotion(self, rapid, longMoveAxe, pos):
		for filter in self.__dict__['_filters']:
			pos = filter.straightMotion(pos)
		self._writer.straightMotion(rapid, longMoveAxe, pos)

	def circleMotion(self, x, y, p):
		for filter in self.__dict__['_filters']:
			(x, y, p) = filter.circleMotion(x, y, p)
		self._writer.circleMotion(x, y, p)

class PolarFixer:
	_lastPos = [ None, None ]

	def __init__(self, r, phi):
		self._r = r
		self._phi = phi

	def straightMotion(self, pos):
		if pos[0] == None and pos[1] == None: return pos

		for i in xrange(2):
			if pos[i] == None:
				pos[i] = self._lastPos[i]
			else:
				self._lastPos[i] = pos[i]

			if pos[i] == None:
				raise ValueError('PolarFixer.straightMotion X/Y both need to be defined')

		(posR, posPhi) = toPolar(pos[0], pos[1])
		(posX, posY) = fromPolar(posR * self._r, posPhi + self._phi)
		return [ posX, posY, pos[2] ]

	def circleMotion(self, x, y, p):
		raise NotImplementedError('circleMotion not supported by PolarFixer (yet)')

class OffsetFilter:
	def __init__(self, offsets):
		self._offsets = offsets

	def straightMotion(self, pos):
		for i in xrange(len(self._offsets)):
			if pos[i] != None:
				pos[i] += self._offsets[i]
		return pos

	def circleMotion(self, x, y, p):
		# circles are addressed relatively, hence no need for offset correction
		#x += self._offsets[0]
		#y += self._offsets[1]
		return (x, y, p)


from util.polar import *
