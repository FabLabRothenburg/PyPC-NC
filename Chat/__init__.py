from PySide import QtCore, QtGui

class ChatLog(QtCore.QObject):
	"""Log of full chat activity"""
	_log = []

	newMessage = QtCore.Signal(str, str)

	def append(self, direction, message):
		if direction != "in" and direction != "out":
			raise ValueError("direction must be either in or out")
		entry = direction, message
		self._log.append(entry)

		if direction == "in":
			print "<<<", message
		else:
			print ">>>", message

		self.newMessage.emit(direction, message)
