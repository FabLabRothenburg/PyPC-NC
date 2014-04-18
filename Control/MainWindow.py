from ui.MainWindow import Ui_MainWindow
from PySide import QtGui, QtCore

from Control.MachineStatus import ControlMachineStatus

class ControlMainWindow(QtGui.QMainWindow):
	def __init__(self, chatBackend):
		super(ControlMainWindow, self).__init__(None)

		self._status = ControlMachineStatus(chatBackend);
		self._status.statusUpdated.connect(self.statusUpdated)

		self._ui = Ui_MainWindow()
		self._ui.setupUi(self)

		self._ui.stop.clicked.connect(self._status.stop)
		self._ui.refMovement.clicked.connect(self._status.refMovement)

		self._ui.driveXUp.clicked.connect(self.driveXUp)
		self._ui.driveYUp.clicked.connect(self.driveYUp)
		self._ui.driveZUp.clicked.connect(self.driveZUp)
		self._ui.driveUUp.clicked.connect(self.driveUUp)
		self._ui.driveXDown.clicked.connect(self.driveXDown)
		self._ui.driveYDown.clicked.connect(self.driveYDown)
		self._ui.driveZDown.clicked.connect(self.driveZDown)
		self._ui.driveUDown.clicked.connect(self.driveUDown)

		self._logger = ControlChatLog(chatBackend.getChatLog(), self._ui.log)
		self._status.updateStatus()

	@QtCore.Slot()
	def statusUpdated(self):
		infos = []
		if self._status.status & 0x10: infos.append('moving')
		if self._status.status & 0x04: infos.append("ref'd")
		if self._status.status & 0x08: infos.append("ref'ing")

		status = hex(self._status.status)

		if infos:
			status += ' (' + ', '.join(infos) + ')'

		self._ui.statusX.setText(status)
		self._ui.statusPx.setText("%.3f" % (self._status.pX / 1000))
		self._ui.statusPy.setText("%.3f" % (self._status.pY / 1000))
		self._ui.statusPz.setText("%.3f" % (self._status.pZ / 1000))
		self._ui.statusPu.setText("%.3f" % (self._status.pU / 1000))

		self._ui.relX.setText("%.3f" % ((self._status.wpX - self._status.pX) / 1000))
		self._ui.relY.setText("%.3f" % ((self._status.wpY - self._status.pY) / 1000))
		self._ui.relZ.setText("%.3f" % ((self._status.wpZ - self._status.pZ) / 1000))

	@QtCore.Slot()
	def driveXUp(self):
		self.manualMove('X', True)

	@QtCore.Slot()
	def driveYUp(self):
		self.manualMove('Y', True)

	@QtCore.Slot()
	def driveZUp(self):
		self.manualMove('Z', True)

	@QtCore.Slot()
	def driveUUp(self):
		self.manualMove('U', True)

	@QtCore.Slot()
	def driveXDown(self):
		self.manualMove('X', False)

	@QtCore.Slot()
	def driveYDown(self):
		self.manualMove('Y', False)

	@QtCore.Slot()
	def driveZDown(self):
		self.manualMove('Z', False)

	@QtCore.Slot()
	def driveUDown(self):
		self.manualMove('U', False)

	def manualMove(self, axis, positive):
		fast = self._ui.driveFast.isChecked()

		if self._ui.drive1Step.isChecked():
			self._status.singleStep(axis, positive, fast)
		elif self._ui.drive01mm.isChecked():
			self._status.manualMove(axis, positive, 100, fast)
		elif self._ui.drive1mm.isChecked():
			self._status.manualMove(axis, positive, 1000, fast)
		elif self._ui.drive10mm.isChecked():
			self._status.manualMove(axis, positive, 10000, fast)
		elif self._ui.drive100mm.isChecked():
			self._status.manualMove(axis, positive, 100000, fast)

class ControlChatLog():
	def __init__(self, chatLog, listView):
		self._chatLog = chatLog;
		self._listView = listView;

		self._model = QtGui.QStandardItemModel(listView);
		listView.setModel(self._model);

		chatLog.newMessage.connect(self.messageHandler)


	@QtCore.Slot(str, str)
	def messageHandler(self, direction, message):
		scrollbar = self._listView.verticalScrollBar()
		scrollToBottom = scrollbar.value() == scrollbar.maximum()

		item = QtGui.QStandardItem(message)
		item.setEditable(False)

		if direction == "out":
			item.setIcon(QtGui.QIcon.fromTheme("go-previous"))
		else:
			item.setIcon(QtGui.QIcon.fromTheme("go-next"))

		self._model.appendRow(item)

		if scrollToBottom:
			self._listView.scrollToBottom()
