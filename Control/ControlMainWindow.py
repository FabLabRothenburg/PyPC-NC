from ui import MainWindow
from PySide import QtGui

class ControlMainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(ControlMainWindow, self).__init__(parent)
		self.ui =  MainWindow.Ui_MainWindow()
		self.ui.setupUi(self)
