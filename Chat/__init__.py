class ChatLog:
	"""Log of full chat activity"""
	_log = []

	def append(self, direction, message):
		if direction != "in" and direction != "out":
			raise ValueError("direction must be either in or out")
		entry = direction, message
		self._log.append(entry)

		if direction == "in":
			print "<<<", message
		else:
			print ">>>", message
