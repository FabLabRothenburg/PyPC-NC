from PySide import QtGui, QtCore
import os, struct, time

class ControlMainWindow(QtGui.QMainWindow):
	_storeButtonUsed = False
	_gv = None
	_parser = None
	_inter = None
	_workpiecePos = [ 5, 5, 5 ]
	_originOffset = [ 0, 0 ]
	_polarCorrection = [ 1, 0 ]
	_debounce = None

	def __init__(self, chatBackend):
		super(ControlMainWindow, self).__init__(None)

		self._machine = MachineController(chatBackend);
		self._machine.machineStatus().statusUpdated.connect(self.statusUpdated)

		self._ui = Ui_MainWindow()
		self._ui.setupUi(self)

		self._ui.stop.clicked.connect(self._machine.stop)
		self._ui.refMovement.clicked.connect(self.refMovement)
		self._ui.importGCode.clicked.connect(self.importGCode)
		self._ui.run.clicked.connect(self.run)
		self._ui.resume.clicked.connect(self.resume)
		self._ui.showGraphicsView.clicked.connect(self.showGraphicsView)

		self._ui.gotoOther.setMenu(self._ui.menuGoto)
		self._ui.storeOther.setMenu(self._ui.menuStore)
		self._ui.menuBar.hide()

		self._ui.storeXY.triggered.connect(self.storeXY)
		self._ui.storeXYZ.triggered.connect(self.storeXYZ)
		self._ui.storeX.triggered.connect(self.storeX)
		self._ui.storeY.triggered.connect(self.storeY)
		self._ui.storeZ.triggered.connect(self.storeZ)

		self._ui.gotoXY.triggered.connect(self.gotoWorkpieceXY)
		self._ui.gotoXYZ.triggered.connect(self.gotoWorkpieceXYZ)
		self._ui.gotoX.triggered.connect(self.gotoWorkpieceX)
		self._ui.gotoY.triggered.connect(self.gotoWorkpieceY)
		self._ui.gotoZ.triggered.connect(self.gotoWorkpieceZ)

		self._ui.driveXUp.clicked.connect(self.driveXUp)
		self._ui.driveYUp.clicked.connect(self.driveYUp)
		self._ui.driveZUp.clicked.connect(self.driveZUp)
		self._ui.driveUUp.clicked.connect(self.driveUUp)
		self._ui.driveXDown.clicked.connect(self.driveXDown)
		self._ui.driveYDown.clicked.connect(self.driveYDown)
		self._ui.driveZDown.clicked.connect(self.driveZDown)
		self._ui.driveUDown.clicked.connect(self.driveUDown)

		self._ui.feedRateOverride.valueChanged.connect(self.feedRateOverrideChanged)

		self._machine.machineStatus().updateStatus()

	@QtCore.Slot()
	def refMovement(self):
		# @fixme assert machine is not moving
		self._machine.setAction(ReferenceMotionController(self._machine))

	@QtCore.Slot()
	def showGraphicsView(self):
		if self._parser == None:
			QtGui.QMessageBox.information(
				self, 'PyPC-NC Graphics View',
				'You need to import G-Code before visualizing it.')
			return

		if self._gv == None:
			self._gv = ControlGraphicsView(self, self._machine)
			self._gv.render(self._parser)
			self._gv.show()
                        self._gv.closed.connect(self.graphicsViewClosed)

        @QtCore.Slot()
        def graphicsViewClosed(self):
                self._gv = None


	@QtCore.Slot()
	def statusUpdated(self):
		infos = []
		if self._machine.machineStatus().status() & 0x10: infos.append('moving')
		if self._machine.machineStatus().status() & 0x04: infos.append("ref'd")
		if self._machine.machineStatus().status() & 0x08: infos.append("ref'ing")

		status = hex(self._machine.machineStatus().status())

		if infos:
			status += ' (' + ', '.join(infos) + ')'

		self._ui.statusX.setText(status)
		self._ui.statusPx.setText("%.3f" % (self._machine.machineStatus().x() / 1000))
		self._ui.statusPy.setText("%.3f" % (self._machine.machineStatus().y() / 1000))
		self._ui.statusPz.setText("%.3f" % (self._machine.machineStatus().z() / 1000))
		self._ui.statusPu.setText("%.3f" % (self._machine.machineStatus().u() / 1000))

		self._ui.relX.setText("%.3f" % ((self._workpiecePos[0] - self._machine.machineStatus().x()) / 1000))
		self._ui.relY.setText("%.3f" % ((self._workpiecePos[1] - self._machine.machineStatus().y()) / 1000))
		self._ui.relZ.setText("%.3f" % ((self._workpiecePos[2] - self._machine.machineStatus().z()) / 1000))

		if isinstance(self._machine.action(), ProgrammedMotionController):
			self._ui.progress.setMaximum(self._machine.action().totalSteps())
			self._ui.progress.setValue(self._machine.action().completedSteps())
		elif self._inter and self._inter.pause:
			if self._ui.progress.maximum():
				QtGui.QMessageBox.information(
					self, 'Tool Change',
					'Insert tool %d now.' % self._inter.nextTool)

			self._ui.progress.setMaximum(0)
		else:
			self._ui.progress.setMaximum(1)
			self._ui.progress.setValue(0)

	@QtCore.Slot()
	def importGCode(self):
		filename = QtGui.QFileDialog.getOpenFileName(self, 'Import G-Code', '.')
		if filename[0] == '': return
		self.importGCodeFromFile(filename[0])

	def importGCodeFromFile(self, filename):
		parser = GCode.GCodeParser()
		parser.readFile(filename)
		parser.removeTapeMarkers()
		parser.removeComments()
		parser.removeInlineComments()
		parser.removeBlockSkipLines()
		parser.normalizeAddressWhitespace()
		parser.normalizeLeadingZeros()
		parser.readSequenceNumbers()

		self._parser = parser

	@QtCore.Slot()
	def run(self):
		if not self._machine.machineStatus().status() & 0x04:
			reply = QtGui.QMessageBox.question(self, 'G-Code Import',
				    'Are you sure to import G-Code without reference movement?',
				    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.No:
				return

		if not self._storeButtonUsed:
			reply = QtGui.QMessageBox.question(self, 'G-Code Import',
				    'Are you sure to import G-Code without setting workpiece location?',
				    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

			if reply == QtGui.QMessageBox.No:
				return

		filters = [
			Filters.OffsetFilter([ -self._originOffset[0], -self._originOffset[1] ]),
			Filters.PolarFixer(self._polarCorrection[0], self._polarCorrection[1]),
			Filters.OffsetFilter(self._workpiecePos)
		]

		fc = Filters.FilterChain(filters, CNCCon.CNCConWriter())
		self._inter = GCode.GCodeInterpreter(fc)
		self._inter.position = [
			self._machine.machineStatus().x() - self._workpiecePos[0] + self._originOffset[0],
			self._machine.machineStatus().y() - self._workpiecePos[1] + self._originOffset[1],
			self._machine.machineStatus().z() - self._workpiecePos[2]
		]
		self._inter.invertZ = self._ui.invertZ.isChecked()
		self._inter.run(self._parser)

		self._machine.setAction(ProgrammedMotionController(self._machine))
		self._machine.action().setFeedRateOverride(self._ui.feedRateOverride.value())
		self._machine.action().setCommands(self._inter.target.buffer)

	@QtCore.Slot()
	def resume(self):
		if not self._inter:
			QtGui.QMessageBox.information(
				self, 'PyPC-NC',
				'Interpreter not initialized.  You need to open & "Run" first.')
			return

		if not self._inter.pause:
			QtGui.QMessageBox.information(
				self, 'PyPC-NC',
				'Interpreter not currently paused.  You may want to start over by clicking "Run".')
			return

		self._inter.target.buffer = [ ]
		self._inter.position = [
			self._machine.machineStatus().x() - self._workpiecePos[0] + self._originOffset[0],
			self._machine.machineStatus().y() - self._workpiecePos[1] + self._originOffset[1],
			self._machine.machineStatus().z() - self._workpiecePos[2]
		]
		self._inter.target.filters()[2].setOffsets(self._workpiecePos)
		self._inter.resume(self._parser)

		self._machine.setAction(ProgrammedMotionController(self._machine))
		self._machine.action().setFeedRateOverride(self._ui.feedRateOverride.value())
		self._machine.action().setCommands(self._inter.target.buffer)

	@QtCore.Slot(int)
	def feedRateOverrideChanged(self, value):
		if isinstance(self._machine.action(), ProgrammedMotionController):
			self._machine.action().setFeedRateOverride(self._ui.feedRateOverride.value())

	@QtCore.Slot()
	def storeXY(self):
		self.storeX()
		self.storeY()

	@QtCore.Slot()
	def storeXYZ(self):
		self.storeXY()
		self.storeZ()

	@QtCore.Slot()
	def storeX(self):
		self._storeButtonUsed = True
		self._workpiecePos[0] = self._machine.machineStatus().x()

	@QtCore.Slot()
	def storeY(self):
		self._storeButtonUsed = True
		self._workpiecePos[1] = self._machine.machineStatus().y()

	@QtCore.Slot()
	def storeZ(self):
		self._storeButtonUsed = True
		self._workpiecePos[2] = self._machine.machineStatus().z()

	def gotoWorkpiece(self, x, y, z):
		if isinstance(self._machine.action(), ProgrammedMotionController):
			return
		elif not isinstance(self._machine.action(), ManualMotionController):
			self._machine.setAction(ManualMotionController(self._machine))

		self._machine.action().gotoXYZ(x, y, z)

	def workpiecePos(self):
		return 

	def originOffset(self):
		return self._originOffset

	def setOriginOffset(self, x, y):
		self._originOffset = (x, y)

	def polarCorrection(self):
		return self._polarCorrection

	def setPolarCorrection(self, r, phi):
		self._polarCorrection = (r, phi)

	@QtCore.Slot()
	def gotoWorkpieceXY(self):
		self.gotoWorkpiece(self._workpiecePos[0], self._workpiecePos[1], None) 

	@QtCore.Slot()
	def gotoWorkpieceXYZ(self):
		self.gotoWorkpiece(self._workpiecePos[0], self._workpiecePos[1], self._workpiecePos[2]) 

	@QtCore.Slot()
	def gotoWorkpieceX(self):
		self.gotoWorkpiece(self._workpiecePos[0], None, None)

	@QtCore.Slot()
	def gotoWorkpieceY(self):
		self.gotoWorkpiece(None, self._workpiecePos[1], None) 

	@QtCore.Slot()
	def gotoWorkpieceZ(self):
		self.gotoWorkpiece(None, None, self._workpiecePos[2]) 

	def workpiecePos(self):
		return self._workpiecePos


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
		if isinstance(self._machine.action(), ProgrammedMotionController):
			return
		elif not isinstance(self._machine.action(), ManualMotionController):
			self._machine.setAction(ManualMotionController(self._machine))

		fast = self._ui.driveFast.isChecked()

		if self._ui.drive1Step.isChecked():
			self._machine.action().singleStep(axis, positive, fast)
		elif self._ui.drive001mm.isChecked():
			self._machine.action().manualMove(axis, positive, 10, fast)
		elif self._ui.drive01mm.isChecked():
			self._machine.action().manualMove(axis, positive, 100, fast)
		elif self._ui.drive1mm.isChecked():
			self._machine.action().manualMove(axis, positive, 1000, fast)
		elif self._ui.drive10mm.isChecked():
			self._machine.action().manualMove(axis, positive, 10000, fast)
		elif self._ui.drive100mm.isChecked():
			self._machine.action().manualMove(axis, positive, 100000, fast)

	@QtCore.Slot(int)
	def readControlEvent(self, fd):
		ev = os.read(fd, 4)
		if len(ev) != 4: return

		button, x, y, z = struct.unpack('bbbb', ev)
		print 'control event: button=%d, x=%d, y=%d, z=%d; time=%f' % (button, x, y, z, time.time())

		if self._debounce != None and time.time() - self._debounce < .1:
			if x != self._debounceX or y != self._debounceY:
				print 'discarding event, bounce detected'
				return

			if x == -1:
				self.manualMove('X', False)
			elif x == 1:
				self.manualMove('X', True)

			if y == -1:
				self.manualMove('Y', False)
			elif y == 1:
				self.manualMove('Y', True)

			self._debounce = None
		else:
			self._debounce = time.time()
			self._debounceX = x
			self._debounceY = y

		if z == -1:
			self.manualMove('Z', False)
		elif z == 1:
			self.manualMove('Z', True)

from Converters import GCode
from Control.MachineStatus import *
from Control.GraphicsView import ControlGraphicsView
from ui.MainWindow import Ui_MainWindow
