from Chat.Backends.Base import ChatBackendBase
from collections import deque
from Control.MockMachine import MockMachine

class ChatBackendMock(ChatBackendBase):
	"""Mock chat backend implementations."""
	_nextLines = deque()
        _machine = MockMachine()

	def send(self, sendStr, expectStr = None):
		self._chatLog.append("out", sendStr)
		# @todo expectStr

                reply = self._machine.process(sendStr)
                if reply != "":
                        self._nextLines.append(reply)

	def getline(self):
		msg = self._nextLines.popleft()
		self._chatLog.append("in", msg);
		return msg
