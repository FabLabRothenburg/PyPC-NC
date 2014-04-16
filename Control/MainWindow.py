from ui.MainWindow import Ui_MainWindow
from PySide import QtGui

from Control.MachineStatus import ControlMachineStatus

class ControlMainWindow(QtGui.QMainWindow):
	def __init__(self, chatBackend):
		super(ControlMainWindow, self).__init__(None)

		self._status = ControlMachineStatus(chatBackend);
		self._status.updateStatus()

		self._ui = Ui_MainWindow()
		self._ui.setupUi(self)
