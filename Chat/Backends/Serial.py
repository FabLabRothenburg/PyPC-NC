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

	def _read(self, timeout = 0.2):
		# read one byte with timeout set, i.e. wait until we received data ...
		self._serial.timeout = timeout
		self._buffer += self._serial.read(1).replace('\r\n', '\n').replace('\r', '\n')

		# ... now fetch the rest, but don't wait for exactly 1k of data
		self._serial.timeout = 0
		self._buffer += self._serial.read(1024).replace('\r\n', '\n').replace('\r', '\n')

		while True:
			if self._buffer[0] == '\001':
				self._nextLines.append('\001')
				self._buffer = self._buffer[1:]
				continue

			if self._buffer[0] == '\004':
				self._nextLines.append('\004')
				self._buffer = self._buffer[1:]
				continue

			pos = self._buffer.find('\n')
			if(pos < 0): break

			self._nextLines.append(self._buffer[:pos])
			self._buffer = self._buffer[pos + 1:]
