from ui.MainWindow import Ui_MainWindow
from PySide import QtGui, QtCore

from Control.MachineStatus import ControlMachineStatus

class ControlMainWindow(QtGui.QMainWindow):
	storeButtonUsed = False

	def __init__(self, chatBackend):
		super(ControlMainWindow, self).__init__(None)

		self._status = ControlMachineStatus(chatBackend);
		self._status.statusUpdated.connect(self.statusUpdated)

		self._ui = Ui_MainWindow()
		self._ui.setupUi(self)

		self._ui.stop.clicked.connect(self._status.stop)
		self._ui.refMovement.clicked.connect(self._status.refMovement)
		self._ui.importGCode.clicked.connect(self.importGCode)

		self._ui.gotoOther.setMenu(self._ui.menuGoto)
		self._ui.storeOther.setMenu(self._ui.menuStore)
		self._ui.menuBar.hide()

		self._ui.storeXY.triggered.connect(self.storeXY)
		self._ui.storeXYZ.triggered.connect(self.storeXYZ)
		self._ui.storeX.triggered.connect(self.storeX)
		self._ui.storeY.triggered.connect(self.storeY)
		self._ui.storeZ.triggered.connect(self.storeZ)

		self._ui.gotoXY.triggered.connect(self.gotoXY)
		self._ui.gotoXYZ.triggered.connect(self.gotoXYZ)
		self._ui.gotoX.triggered.connect(self.gotoX)
		self._ui.gotoY.triggered.connect(self.gotoY)
		self._ui.gotoZ.triggered.connect(self.gotoZ)

		self._ui.driveXUp.clicked.connect(self.driveXUp)
		self._ui.driveYUp.clicked.connect(self.driveYUp)
		self._ui.driveZUp.clicked.connect(self.driveZUp)
		self._ui.driveUUp.clicked.connect(self.driveUUp)
		self._ui.driveXDown.clicked.connect(self.driveXDown)
		self._ui.driveYDown.clicked.connect(self.driveYDown)
		self._ui.driveZDown.clicked.connect(self.driveZDown)
		self._ui.driveUDown.clicked.connect(self.driveUDown)

		self._ui.feedRateOverride.valueChanged.connect(self.feedRateOverrideChanged)

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

		if self._status.totalSteps:
			self._ui.progress.setMaximum(self._status.totalSteps)
			self._ui.progress.setValue(self._status.N)
		else:
			self._ui.progress.setMaximum(1)
			self._ui.progress.setValue(0)

	@QtCore.Slot()
	def importGCode(self):
		if not self._status.status & 0x04:
		        reply = QtGui.QMessageBox.question(self, 'G-Code Import',
			            'Are you sure to import G-Code without reference movement?',
				    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.No:
				return

		if not self.storeButtonUsed:
		        reply = QtGui.QMessageBox.question(self, 'G-Code Import',
			            'Are you sure to import G-Code without setting workpiece location?',
				    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.No:
				return

		filename = QtGui.QFileDialog.getOpenFileName(self, 'Import G-Code', '.')
		if filename[0] == '': return

		self._status.importGCode(filename[0], self._ui.invertZ.isChecked())

	@QtCore.Slot(int)
	def feedRateOverrideChanged(self, value):
		self._status.setFeedRateOverride(value)

	@QtCore.Slot()
	def storeXY(self):
		self.storeButtonUsed = True
		self._status.storeXY()

	@QtCore.Slot()
	def storeXYZ(self):
		self.storeButtonUsed = True
		self._status.storeXYZ()

	@QtCore.Slot()
	def storeX(self):
		self.storeButtonUsed = True
		self._status.storeX()

	@QtCore.Slot()
	def storeY(self):
		self.storeButtonUsed = True
		self._status.storeY()

	@QtCore.Slot()
	def storeZ(self):
		self.storeButtonUsed = True
		self._status.storeZ()

	@QtCore.Slot()
	def gotoXY(self):
		self._status.gotoWorkpiece(self._ui.driveFast.isChecked(), True, True, False)

	@QtCore.Slot()
	def gotoXYZ(self):
		self._status.gotoWorkpiece(self._ui.driveFast.isChecked(), True, True, True)

	@QtCore.Slot()
	def gotoX(self):
		self._status.gotoWorkpiece(self._ui.driveFast.isChecked(), True, False, False)

	@QtCore.Slot()
	def gotoY(self):
		self._status.gotoWorkpiece(self._ui.driveFast.isChecked(), False, True, False)

	@QtCore.Slot()
	def gotoZ(self):
		self._status.gotoWorkpiece(self._ui.driveFast.isChecked(), False, False, True)

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
		elif self._ui.drive001mm.isChecked():
			self._status.manualMove(axis, positive, 10, fast)
		elif self._ui.drive01mm.isChecked():
			self._status.manualMove(axis, positive, 100, fast)
		elif self._ui.drive1mm.isChecked():
			self._status.manualMove(axis, positive, 1000, fast)
		elif self._ui.drive10mm.isChecked():
			self._status.manualMove(axis, positive, 10000, fast)
		elif self._ui.drive100mm.isChecked():
			self._status.manualMove(axis, positive, 100000, fast)
