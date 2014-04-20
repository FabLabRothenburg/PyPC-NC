import unittest
from Converters import GCode

class TestInterpreterBasics(unittest.TestCase):
	def test_splitBlockSelf(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.splitBlock('M30'), [ [ 'M30' ] ])

	def test_splitBlockGroupParams(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.splitBlock('G0 X0'), [ [ 'G0', 'X0' ] ])

	def test_splitBlockGroupInsns(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.splitBlock('M0 M1'), [ [ 'M0' ], [ 'M1' ] ])

	def test_splitBlockM3takesS(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.splitBlock('M3 S3000'), [ [ 'M3', 'S3000' ] ])

	def test_splitBlockComplex(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.splitBlock('G17 G20 G90 G64 P0.003 M3 S3000 M7 F1'), [
			[ 'G17' ],
			[ 'G20' ],
			[ 'G90' ],
			[ 'G64', 'P0.003' ],
			[ 'M3', 'S3000' ],
			[ 'M7' ],
			[ 'F1' ] ])

	def test_G20(self):
		i = GCode.GCodeInterpreter()
		i.process([ 'G20' ])
		self.assertEqual(i.stretch, 2.54)

	def test_G21(self):
		i = GCode.GCodeInterpreter()
		i.process([ 'G21' ])
		self.assertEqual(i.stretch, 1)

	def test_G90(self):
		i = GCode.GCodeInterpreter()
		i.process([ 'G90' ])
		self.assertEqual(i.absDistanceMode, True)

	def test_G91(self):
		i = GCode.GCodeInterpreter()
		i.process([ 'G91' ])
		self.assertEqual(i.absDistanceMode, False)

	def test_M30(self):
		i = GCode.GCodeInterpreter()
		i.process([ 'M30' ])
		self.assertEqual(i.end, True)

	def test_M2(self):
		i = GCode.GCodeInterpreter()
		i.process([ 'M2' ])
		self.assertEqual(i.end, True)



class TestRapidMotionG0(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.buffer = []
		self.i.position = [ 5.000, 0.0, 2.000 ]

	def test_G0_simpleX0(self):
		self.i.process([ 'G0', 'X0' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V1,X10000' ])

	def test_G0_simpleX10(self):
		self.i.process([ 'G0', 'X10' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V1,X20000' ])

	def test_G0_simpleX10X20(self):
		self.i.process([ 'G0', 'X10' ])
		self.i.process([ 'G0', 'X20' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V1,X20000', 'E', 'V1,X30000' ])

	def test_G0_simpleY10(self):
		self.i.process([ 'G0', 'Y10' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V2,Y20000' ])

	def test_G0_simpleY10Y20(self):
		self.i.process([ 'G0', 'Y10' ])
		self.i.process([ 'G0', 'Y20' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V2,Y20000', 'E', 'V2,Y30000' ])

	def test_G0_simpleXY0(self):
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V2,X10000,Y10000' ])

	def test_G0_simpleXY0(self):
		self.i.position = [ 5.000, 9.500, 2.000 ]
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V1,X10000,Y10000' ])

	def test_G0_simpleX0_repeat(self):
		self.i.process([ 'G0', 'X0' ])
		self.i.process([ 'G0', 'X0' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V1,X10000' ])

	def test_G0_simpleY10_repeat(self):
		self.i.process([ 'G0', 'Y10' ])
		self.i.process([ 'G0', 'Y10' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V2,Y20000' ])

	def test_G0_simpleXY0_repeat(self):
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V2,X10000,Y10000' ])

	def test_G0_simpleZ0(self):
		self.i.process([ 'G0', 'Z0' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V3,Z10000' ])

	def test_G0_simpleZ0Z10(self):
		self.i.process([ 'G0', 'Z0' ])
		self.i.process([ 'G0', 'Z10' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V3,Z10000', 'E', 'V3,Z20000' ])

	def test_G0_incrXXX(self):
		self.i.process([ 'G0', 'X0' ])
		self.i.process([ 'G91' ])
		self.i.process([ 'G0', 'X5' ])
		self.i.process([ 'G0', 'X5' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V1,X10000', 'E', 'V1,X15000', 'E', 'V1,X20000' ])


class WriteZOnFirstMove(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.buffer = []
		self.i.position = [ 9.000, 9.000, 0.000 ]

	def test_firstMove(self):
		self.i.process([ 'G91' ])
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V3,X10000,Y10000,Z10000' ])

	def test_secondMove(self):
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.i.process([ 'G91' ])
		self.i.process([ 'G0', 'X1', 'Y1' ])
		self.assertEqual(self.i.buffer, [ 'E', 'V1,X10000,Y10000', 'E', 'V1,X11000,Y11000' ])



class TestCoordinatedMotionG1(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.buffer = []
		self.i.position = [ 5.000, 0.0, 2.000 ]

	def test_G1_simpleX0(self):
		self.i.process([ 'G1', 'X0' ])
		self.assertEqual(self.i.buffer, [ 'E', 'C08', 'W10', 'V21,X10000' ])

	def test_G1_simpleZ0(self):
		self.i.process([ 'G1', 'Z0' ])
		self.assertEqual(self.i.buffer, [ 'E', 'C08', 'W10', 'V21,z10000' ])

	def test_G1_simpleXYZ1(self):
		self.i.process([ 'G1', 'X1' ])
		self.i.process([ 'G1', 'Y1' ])
		self.i.process([ 'G1', 'Z1' ])
		self.assertEqual(self.i.buffer, [ 'E', 'C08', 'W10', 'V21,X11000', 'E', 'V21,Y11000', 'E', 'V21,z11000' ])

	def test_G1_simpleXYZ1_G91(self):
		self.i.process([ 'G91' ])
		self.i.process([ 'G1', 'X1' ])
		self.i.process([ 'G1', 'Y1' ])
		self.i.process([ 'G1', 'Z1' ])
		self.assertEqual(self.i.buffer, [ 'E', 'C08', 'W10', 'V21,X11000,Y10000,Z10000', 'E', 'V21,Y11000', 'E', 'V21,z11000' ])

class TestG0G1Switching(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.buffer = []
		self.i.position = [ 9.000, 9.000, 0.000 ]

	def test_G0G1G0(self):
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.i.process([ 'G1', 'X5', 'Y5' ])
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.assertEqual(self.i.buffer, [
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

		self.assertEqual(self.i.buffer, [
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

class TestSimpleCircles(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.buffer = []
		self.i.position = [ 9.000, 9.000, 0.000 ]

	def test_basicFullCircle(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'R20' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-1570796'
		])

