import math
from PySide import QtGui, QtCore

class ControlGraphicsView(QtGui.QDialog):
	closed = QtCore.Signal()

	def __init__(self, mainwin, machine):
		self._mainwin = mainwin
		self._machine = machine

		super(ControlGraphicsView, self).__init__(None)

		self._ui = Ui_GraphicsViewWindow()
		self._ui.setupUi(self)

		self._ui.markOrigin.clicked.connect(self.markOrigin)
		self._ui.gotoXY.clicked.connect(self.gotoXY)
		self._ui.polarFixXY.clicked.connect(self.polarFixXY)
		self._ui.closeButton.clicked.connect(self.close)

	@QtCore.Slot()
	def markOrigin(self):
		(x, y) = self._scene.getCursorPosition()
		self._scene.setCrosshairPosition(x, y)
		self._mainwin.setOriginOffset(x, y)

	@QtCore.Slot()
	def gotoXY(self):
		if isinstance(self._machine.action(), ProgrammedMotionController):
			return
		elif not isinstance(self._machine.action(), ManualMotionController):
			self._machine.setAction(ManualMotionController(self._machine))

		(posX, posY) = self._scene.getCursorPosition()
		(orgX, orgY) = self._scene.getCrosshairPosition()

		(posR, posPhi) = self.toPolar(posX - orgX, posY - orgY)
		(r, deltaPhi) = self._mainwin.polarCorrection()
		(posX, posY) = self.fromPolar(posR * r, posPhi + deltaPhi)

		workpiecePos = self._mainwin.workpiecePos()
		self._machine.action().gotoXYZ(posX + workpiecePos[0], posY + workpiecePos[1])

	@QtCore.Slot()
	def polarFixXY(self):
		(orgX, orgY) = self._scene.getCrosshairPosition()
		(posX, posY) = self._scene.getCursorPosition()
		(r1, phi1) = self.toPolar(posX - orgX, posY - orgY)

		workpiecePos = self._mainwin.workpiecePos()
		posX = self._machine.machineStatus().x() - workpiecePos[0] + orgX
		posY = self._machine.machineStatus().y() - workpiecePos[1] + orgY
		(r2, phi2) = self.toPolar(posX - orgX, posY - orgY)
		self._mainwin.setPolarCorrection(r2 / r1, phi2 - phi1)

	def fromPolar(self, r, phi):
		x = r * math.cos(phi)
		y = r * math.sin(phi)
		return (x, y)

	def toPolar(self, x, y):
		r = math.sqrt(x ** 2 + y ** 2)
		phi = cmp(y, 0) * math.acos(x / r)
		return (r, phi)

	def closeEvent(self, event):
		self.closed.emit()
		event.accept()

	def render(self, parser):
		self._scene = MyGraphicsScene()

		renderer = SceneRenderer(self._scene)
		inter = GCode.GCodeInterpreter(renderer)
		inter.offsets = [ 0, 0, 0 ]
		inter.position = [ 0, 0, 0 ]
		inter.incrPosition = [ 0, 0, 0 ]
		inter.run(parser)

		self._ui.graphicsView.setScene(self._scene)

		bbox = self._scene.itemsBoundingRect()
		bbox.setTop(bbox.top() - bbox.height() * 0.1)
		bbox.setBottom(bbox.bottom() + bbox.height() * 0.1)
		bbox.setLeft(bbox.left() - bbox.width() * 0.1)
		bbox.setRight(bbox.right() + bbox.width() * 0.1)
		self._scene.setSceneRect(bbox)
		self._ui.graphicsView.fitInView(bbox, QtCore.Qt.KeepAspectRatio)
		self._ui.graphicsView.autoconfSizes()  # @fixme wait for initial resize

class MyGraphicsScene(QtGui.QGraphicsScene):
	def __init__(self):
		super(MyGraphicsScene, self).__init__()

		pen = QtGui.QPen(QtCore.Qt.GlobalColor.blue)
		self._crossHairV = self.addLine(0, 0, 0, 0, pen)
		self._crossHairH = self.addLine(0, 0, 0, 0, pen)

		pen = QtGui.QPen(QtCore.Qt.GlobalColor.red)
		brush = QtGui.QBrush(QtCore.Qt.GlobalColor.red)
		self._cursor = self.addEllipse(0, 0, 0, 0, pen, brush)

	def mousePressEvent(self, event):
		super(MyGraphicsScene, self).mousePressEvent(event)
		self._mousePressPos = event.screenPos()

	def mouseReleaseEvent(self, event):
		super(MyGraphicsScene, self).mouseReleaseEvent(event)
		if event.button() != QtCore.Qt.LeftButton: return
		if self._mousePressPos.x() != event.screenPos().x(): return
		if self._mousePressPos.y() != event.screenPos().y(): return

		clickPos = event.buttonDownScenePos(QtCore.Qt.LeftButton)
		items = self.items(clickPos.x() - 1000, clickPos.y() - 1000, 2000, 2000, QtCore.Qt.IntersectsItemShape)
		if not len(items): return

		maxDist = None
		selPos = None
		for item in items:
			if isinstance(item, QtGui.QGraphicsLineItem):
				points = [ item.line().p1(), item.line().p2() ]
			elif isinstance(item, QtGui.QGraphicsEllipseItem):
				points = [ item.rect().center() ]
			else:
				continue

			for point in points:
				dist = math.sqrt((point.x() - clickPos.x()) ** 2 + (point.y() - clickPos.y()) ** 2)

				if maxDist == None or dist < maxDist:
					maxDist = dist
					selPos = point

		self.setCursorPosition(selPos.x(), -selPos.y())

	def setCursorPosition(self, x, y):
		d = self._cursor.rect().width()
		self._cursor.setRect(x - d / 2, -y - d / 2, d, d)

	def getCursorPosition(self):
		oldr = self._cursor.rect().width() / 2
		return (self._cursor.rect().x() + oldr, -(self._cursor.rect().y() + oldr))

	def setCursorRadius(self, newr):
		oldr = self._cursor.rect().width() / 2
		x = self._cursor.rect().x() + oldr
		y = self._cursor.rect().y() + oldr
		self._cursor.setRect(x - newr, y - newr, newr * 2, newr * 2)

	def setCrosshairPosition(self, x, y):
		newr = self._crossHairH.line().dx() / 2
		self._crossHairH.setLine(x - newr, -y, x + newr, -y)
		self._crossHairV.setLine(x, -y - newr, x, -y + newr)

	def getCrosshairPosition(self):
		r = self._crossHairH.line().dx() / 2
		return (self._crossHairH.line().x1() + r, -(self._crossHairV.line().y1() + r))

	def setCrosshairSize(self, newr, linew):
		oldr = self._crossHairH.line().dx() / 2
		x = self._crossHairH.line().x1() + oldr
		y = self._crossHairV.line().y1() + oldr

		pen = QtGui.QPen(QtCore.Qt.GlobalColor.blue)
		pen.setWidth(linew)

		self._crossHairH.setLine(x - newr, y, x + newr, y)
		self._crossHairH.setPen(pen)
		self._crossHairV.setLine(x, y - newr, x, y + newr)
		self._crossHairV.setPen(pen)

class MyGraphicsView(QtGui.QGraphicsView):
	def __init__(self, parent):
		super(MyGraphicsView, self).__init__(parent)

	def mousePressEvent(self, event):
		self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
		super(MyGraphicsView, self).mousePressEvent(event)

	def mouseReleaseEvent(self, event):
		self.setDragMode(QtGui.QGraphicsView.NoDrag)
		super(MyGraphicsView, self).mouseReleaseEvent(event)

	def wheelEvent(self,  event):
		factor = 1.2;
		if event.delta() < 0:
			factor = 1.0 / factor
		self.scale(factor, factor)
		self.autoconfSizes()

	def autoconfSizes(self):
		bbox = self.mapToScene(self.viewport().geometry()).boundingRect()
		r = 4 * bbox.width() / self.rect().width()
		self.scene().setCursorRadius(r)

		r = 20 * bbox.width() / self.rect().width()
		lw = 3 * bbox.width() / self.rect().width()
		self.scene().setCrosshairSize(r, lw)



class SceneRenderer:
	axes = [ 'X', 'Y', 'Z' ]
	_x = 0
	_y = 0

	def __init__(self, scene):
		self._scene = scene

	def appendPostamble(self): pass
	def setFeedRate(self, fr): pass
	def setSpindleSpeed(self, speed): pass
	def appendEmptyStep(self): pass
	def setCoolantMist(self): pass
	def setCoolantOff(self): pass
	def setSpindleConfig(self, spindleCCW, spindleEnable, speed): pass
	def setSpeed(self, rapid): pass

	def straightMotion(self, rapid, longMoveAxe, machinePos):
		newx = self._x if machinePos[0] == None else machinePos[0]
		newy = self._y if machinePos[1] == None else machinePos[1]

		if not rapid:
			print (self._x, -self._y, newx, -newy)
			if self._x == newx and self._y == newy:
				pen = QtGui.QPen(QtCore.Qt.GlobalColor.magenta)
				self._scene.addEllipse(newx - 250, -newy - 250, 500, 500, pen)
			else:
				self._scene.addLine(self._x, -self._y, newx, -newy)

		self._x = newx
		self._y = newy

	def circleMotion(self, x, y, p):
		pass # @fixme

from ui.GraphicsView import Ui_GraphicsViewWindow
from Converters import GCode
from Control.MachineStatus import *
