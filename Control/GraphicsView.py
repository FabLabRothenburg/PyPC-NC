from PySide import QtGui, QtCore

class ControlGraphicsView(QtGui.QDialog):
	def __init__(self):
		super(ControlGraphicsView, self).__init__(None)

		self._ui = Ui_GraphicsViewWindow()
		self._ui.setupUi(self)

	def render(self, parser):
		self._scene = QtGui.QGraphicsScene()

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
			self._scene.addLine(self._x, -self._y, newx, -newy)

		self._x = newx
		self._y = newy

	def circleMotion(self, x, y, p):
		pass # @fixme

from ui.GraphicsView import Ui_GraphicsViewWindow
from Converters import GCode
