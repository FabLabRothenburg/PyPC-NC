from ui.MainWindow import Ui_MainWindow
from PySide import QtGui

class ControlMainWindow(QtGui.QMainWindow):
	def __init__(self, chatBackend):
		super(ControlMainWindow, self).__init__(None)
		self._chatBackend = chatBackend
		self._ui = Ui_MainWindow()
		self._ui.setupUi(self)
		self.updateStatus()

	def updateStatus(self):
		self._chatBackend.send("@X")
		print(self._chatBackend.getline())
