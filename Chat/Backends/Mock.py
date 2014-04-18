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
                if reply != "":
                        self._nextLines.append(reply)
