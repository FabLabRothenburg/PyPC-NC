from collections import deque

class ChatBackendBase:
	"""Common base class for chat backend implementations."""
	_chatLog = None
	_sane = True
	_waitSOH = False
	_queue = deque()
	_nextLines = deque()

	def __init__(self, chatLog):
		self._chatLog = chatLog

	def getChatLog(self):
		return self._chatLog

	def _send(self, bytes):
		raise NotImplementedError("ChatBackendBase::_send is abstract")

	def _poll(self):
		raise NotImplementedError("ChatBackendBase::_poll is abstract")

	def _read(self):
		raise NotImplementedError("ChatBackendBase::_read is abstract")

	def isSane(self):
		return _sane

	def sendQueue(self, sendStr):
		if self._waitSOH:
			self._queue.append(sendStr)
		else:
			self._waitSOH = True
			return self.send(sendStr, "");

	def send(self, sendStr, expectStr = None):
		self._chatLog.append("out", sendStr)
		# @todo expectStr

		self._poll()
		self._processLines()
		self._send(sendStr)

		if expectStr != None:
			result = self.getline()
			if result != expectStr:
				raise RuntimeError("Unexpected Controller reply, got %s instead of %s" % (result, expectStr))

	def getline(self):
		if not self._nextLines:
			self._read()

		msg = self._nextLines.popleft()
		self._chatLog.append("in", msg);
		return msg

	def _processLines(self):
		while self._nextLines:
			msg = self.getline()
			print "ignoring: %s" % msg

	def hasLines(self):
		self._poll()
		return bool(self._nextLines)

	def _handleSOH(self):
		print "handling SOH ..."

		if self._queue:
			print "received SOH, sending queued event ..."
			self.send(self._queue.popleft(), "")
		else:
			print "received SOH, clearing wait flag ..."
			self._waitSOH = False
