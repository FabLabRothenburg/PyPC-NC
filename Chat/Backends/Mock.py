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

	def getline(self):
		msg = self._nextLines.popleft()
		self._chatLog.append("in", msg);
		return msg
