from ui.GraphicsView import Ui_GraphicsViewWindow
from PySide import QtGui, QtCore

class ControlGraphicsView(QtGui.QDialog):
	def __init__(self):
		super(ControlGraphicsView, self).__init__(None)

		self._ui = Ui_GraphicsViewWindow()
		self._ui.setupUi(self)

