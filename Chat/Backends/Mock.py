from Chat.Backends.Base import ChatBackendBase
from Control.MockMachine import MockMachine

class ChatBackendMock(ChatBackendBase):
	"""Mock chat backend implementations."""
        _machine = MockMachine()

        def _poll(self):
                pass

        def _read(self):
                pass

	def _send(self, sendStr):
                reply = self._machine.process(sendStr)

                if reply != None:
                        self._nextLines.append(reply)

		while self._machine.soh:
			self._nextLines.append('\001')
			self._machine.soh -= 1

		while self._machine.eot:
			self._nextLines.append('\004')
			self._machine.eot -= 1
