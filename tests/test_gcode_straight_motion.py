import unittest
from Converters import GCode
from Converters import CNCCon

class TestRapidMotionG0(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		self.i.target.buffer = []
		self.i.position = [ 5.000, 0.0, 2.000 ]

	def test_G0_simpleX0(self):
		self.i.process([ 'G0', 'X0' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V1,X10000' ])

	def test_G0_simpleX10(self):
		self.i.process([ 'G0', 'X10' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V1,X20000' ])

	def test_G0_simpleX10X20(self):
		self.i.process([ 'G0', 'X10' ])
		self.i.process([ 'G0', 'X20' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V1,X20000', 'E', 'V1,X30000' ])

	def test_G0_simpleY10(self):
		self.i.process([ 'G0', 'Y10' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V2,Y20000' ])

	def test_G0_simpleY10Y20(self):
		self.i.process([ 'G0', 'Y10' ])
		self.i.process([ 'G0', 'Y20' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V2,Y20000', 'E', 'V2,Y30000' ])

	def test_G0_simpleXY0_Ylonger(self):
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V2,X10000,Y10000' ])

	def test_G0_simpleXY0_Xlonger(self):
		self.i.position = [ 5.000, 9.500, 2.000 ]
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V1,X10000,Y10000' ])

	def test_G0_simpleX0_repeat(self):
		self.i.process([ 'G0', 'X0' ])
		self.i.process([ 'G0', 'X0' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V1,X10000' ])

	def test_G0_simpleY10_repeat(self):
		self.i.process([ 'G0', 'Y10' ])
		self.i.process([ 'G0', 'Y10' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V2,Y20000' ])

	def test_G0_simpleXY0_repeat(self):
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V2,X10000,Y10000' ])

	def test_G0_simpleZ0(self):
		self.i.process([ 'G0', 'Z0' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V3,Z10000' ])

	def test_G0_simpleZ0Z10(self):
		self.i.process([ 'G0', 'Z0' ])
		self.i.process([ 'G0', 'Z10' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V3,Z10000', 'E', 'V3,Z20000' ])

	def test_G0_simpleZ0Z10invert(self):
		self.i.invertZ = True
		self.i.process([ 'G0', 'Z0' ])
		self.i.process([ 'G0', 'Z10' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V3,Z10000', 'E', 'V3,Z0' ])

	def test_G0_incrXXX(self):
		self.i.process([ 'G0', 'X0' ])
		self.i.process([ 'G91' ])
		self.i.process([ 'G0', 'X5' ])
		self.i.process([ 'G0', 'X5' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V1,X10000', 'E', 'V1,X15000', 'E', 'V1,X20000' ])


class WriteZOnFirstMove(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		self.i.target.buffer = []
		self.i.position = [ 9.000, 9.000, 0.000 ]

	def test_firstMove(self):
		self.i.process([ 'G91' ])
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V3,X10000,Y10000,Z10000' ])

	def test_secondMove(self):
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.i.process([ 'G91' ])
		self.i.process([ 'G0', 'X1', 'Y1' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'V1,X10000,Y10000', 'E', 'V1,X11000,Y11000' ])



class TestCoordinatedMotionG1(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		self.i.target.buffer = []
		self.i.position = [ 5.000, 0.0, 2.000 ]

	def test_G1_simpleX0(self):
		self.i.process([ 'G1', 'X0' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'C08', 'W10', 'V21,X10000' ])

	def test_G1_simpleZ0(self):
		self.i.process([ 'G1', 'Z0' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'C08', 'W10', 'V21,Z10000' ])

	def test_G1_simpleXYZ1(self):
		self.i.process([ 'G1', 'X1' ])
		self.i.process([ 'G1', 'Y1' ])
		self.i.process([ 'G1', 'Z1' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'C08', 'W10', 'V21,X11000', 'E', 'V21,Y11000', 'E', 'V21,Z11000' ])

	def test_G1_simpleXYZ1_G91(self):
		self.i.process([ 'G91' ])
		self.i.process([ 'G1', 'X1' ])
		self.i.process([ 'G1', 'Y1' ])
		self.i.process([ 'G1', 'Z1' ])
		self.assertEqual(self.i.target.buffer, [ 'E', 'C08', 'W10', 'V21,X11000,Y10000,Z10000', 'E', 'V21,Y11000', 'E', 'V21,Z11000' ])

class TestG0G1Switching(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		self.i.target.buffer = []
		self.i.position = [ 9.000, 9.000, 0.000 ]

	def test_G0G1G0(self):
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.i.process([ 'G1', 'X5', 'Y5' ])
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.target.buffer, [
			'E', 'V1,X10000,Y10000',
			'E', 'E', 'C08', 'W10', 'V21,X15000,Y15000',
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V1,X10000,Y10000'
		])

	def test_G1G0G1G0(self):
		self.i.process([ 'G1', 'X0', 'Y0' ])
		self.i.process([ 'G1', 'X1', 'Y0' ])
		self.i.process([ 'G0', 'X1', 'Y2' ])
		self.i.process([ 'G0', 'X3', 'Y3' ])
		self.i.process([ 'G1', 'X4', 'Y5' ])
		self.i.process([ 'G1', 'X6', 'Y6' ])
		self.i.process([ 'G0', 'X1', 'Y1' ])
		self.i.process([ 'G0', 'X0', 'Y0' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'C08', 'W10', 'V21,X10000,Y10000',
			'E', 'V21,X11000',
			'E', 'C10', 'W10',
			'E', 'C10', 'W10', 'V2,Y12000',
			'E', 'V1,X13000,Y13000',
			'E', 'E', 'C08', 'W10', 'V21,X14000,Y15000',
			'E', 'V21,X16000,Y16000',
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V1,X11000,Y11000',
			'E', 'V1,X10000,Y10000',
		])

