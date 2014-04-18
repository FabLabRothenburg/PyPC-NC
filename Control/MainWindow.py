from ui.MainWindow import Ui_MainWindow
from PySide import QtGui, QtCore

from Control.MachineStatus import ControlMachineStatus

class ControlMainWindow(QtGui.QMainWindow):
	statusMessages = {
		 4: 'ready',
		14: 'moving',
		15: 'ref movement',
	}

	def __init__(self, chatBackend):
		super(ControlMainWindow, self).__init__(None)

		self._status = ControlMachineStatus(chatBackend);
		self._status.statusUpdated.connect(self.statusUpdated)

		self._ui = Ui_MainWindow()
		self._ui.setupUi(self)

		self._logger = ControlChatLog(chatBackend.getChatLog(), self._ui.log)

		self._status.updateStatus()

	@QtCore.Slot()
	def statusUpdated(self):
		self._ui.statusX.setText("%02d (%s)" % (
			self._status.status,
			self.statusMessages[self._status.status]
		))

		self._ui.statusPx.setText(str(self._status.pX))
		self._ui.statusPy.setText(str(self._status.pY))
		self._ui.statusPz.setText(str(self._status.pZ))

		self._ui.relX.setText(str(self._status.pX - self._status.wpX))
		self._ui.relY.setText(str(self._status.pY - self._status.wpY))
		self._ui.relZ.setText(str(self._status.pZ - self._status.wpZ))


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
