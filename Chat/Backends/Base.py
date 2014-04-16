class ChatBackendBase:
	"""Common base class for chat backend implementations."""
	_chatLog = None
	_sane = True

	def __init__(self, chatLog):
		self._chatLog = chatLog

	def getChatLog(self):
		return self._chatLog

	def send(self, sendStr, expectStr = None):
		raise NotImplementedError("ChatBackendBase::send is abstract")

	def getline(self):
		raise NotImplementedError("ChatBackendBase::getline is abstract")

	def isSane(self):
		return _sane
