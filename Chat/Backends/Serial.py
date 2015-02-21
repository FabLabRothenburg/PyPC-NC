from Chat.Backends.Base import ChatBackendBase
import serial

class ChatBackendSerial(ChatBackendBase):
	"""Serial chat backend implementation."""
	_buffer = ""

	def __init__(self, logger, ttyname):
		ChatBackendBase.__init__(self, logger)
		self._serial = serial.Serial(ttyname, 115200)

	def _send(self, bytes):
		self._serial.write(bytes + '\r')

	def _poll(self):
		self._read(0)

	def _read(self, timeout = .2):
		# fetch anything that already is in buffer
		self._serial.timeout = 0
		self._buffer += self._serial.read(1024).replace('\r\n', '\n').replace('\r', '\n')

		self._serial.timeout = timeout
		while True:
			char = self._serial.read(1)
			if len(char) == 0: break

			if char == '\r': char = '\n'
			self._buffer += char

			if char == '\n': break

		while len(self._buffer):
			if self._buffer[0] == '\001':
				self._nextLines.append('\001')
				self._buffer = self._buffer[1:]
				self._handleSOH()
				continue

			if self._buffer[0] == '\004':
				self._nextLines.append('\004')
				self._buffer = self._buffer[1:]
				continue

			pos = self._buffer.find('\n')
			if(pos < 0): break

			self._nextLines.append(self._buffer[:pos])
			self._buffer = self._buffer[pos + 1:]

	def fileno(self):
		return self._serial.fileno()
