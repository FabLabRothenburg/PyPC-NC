from Chat.Backends.Base import ChatBackendBase
from collections import deque

class ChatBackendMock(ChatBackendBase):
	"""Mock chat backend implementations."""
	_nextLines = deque()

	def send(self, sendStr, expectStr = None):
		self._chatLog.append("out", sendStr)
		# @todo expectStr

		if sendStr == "@X":
			self._nextLines.append("@X04")
		elif sendStr == "@Px":
			self._nextLines.append("@PX0123.456")
		elif sendStr == "@Py":
			self._nextLines.append("@PY0123.456")
		elif sendStr == "@Pz":
			self._nextLines.append("@PZ0123.456")

	def getline(self):
		msg = self._nextLines.popleft()
		self._chatLog.append("in", msg);
		return msg
