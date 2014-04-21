import math
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

class TestCirclesCW(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.buffer = []
		self.i.position = [ 9.000, 9.000, 0.000 ]

	def test_basicQuarterCircle(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'R20' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-1570796'
		])

	def test_basicHalfCircle(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-30', 'Y15', 'R20' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-3141592'
		])

	def test_basicQuarterCircle2(self):
		self.i.process([ 'G0', 'X-10', 'Y-5' ])
		self.i.process([ 'G2', 'X-30', 'Y15', 'R20' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V1,X0,Y5000',
			'E', 'E', 'C08', 'W10', 'K21,x0,y20000,p-1570796'
		])

	def test_basicQuarterCircle(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'R20' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-1570796'
		])

	def test_basicArcWith20Degrees(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X8.79385241572', 'Y21.8404028665', 'R20' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x18794,y6840,p-349044'
		])

	def test_oneMoreStrangeArc(self):
		self.i.process([ 'G0', 'X5', 'Y5' ])
		self.i.process([ 'G2', 'X0', 'Y5', 'R10' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V1,X15000,Y15000',
			# WinPC-NC calculates K21,x-2500,y9682,p-505383 here
			# I can't figure out where they round one of the values
			# to get 505383 instead of 505360; using the latter
			# which is just 0.004% off
			'E', 'E', 'C08', 'W10', 'K21,x-2500,y9682,p-505360'
		])

	def test_basicQuarterCircleCenterFormat(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'I-20', 'J0' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-1570796'
		])

	def test_basicQuarterCircleCenterFormatJustI(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'I-20' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-1570796'
		])


	def test_basicThreeQuarterCircle1(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'J-20' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x0,y-20000,p-4712388'
		])

	def test_basicThreeQuarterCircle2(self):
		self.i.process([ 'G0', 'X10', 'Y0' ])
		self.i.process([ 'G2', 'X0', 'Y10', 'I-10' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V1,X20000,Y10000',
			'E', 'E', 'C08', 'W10', 'K21,x-10000,y0,p-4712388'
		])

	def test_basicThreeQuarterCircle3(self):
		self.i.process([ 'G0', 'X0', 'Y-10' ])
		self.i.process([ 'G2', 'X10', 'Y0', 'J10' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V2,X10000,Y0',
			'E', 'E', 'C08', 'W10', 'K21,x0,y10000,p-4712388'
		])

	def test_basicThreeQuarterCircle4(self):
		self.i.process([ 'G0', 'X-10', 'Y0' ])
		self.i.process([ 'G2', 'X0', 'Y-10', 'I10' ])

		self.assertEqual(self.i.buffer, [
			'E', 'V1,X0,Y10000',
			'E', 'E', 'C08', 'W10', 'K21,x10000,y0,p-4712388'
		])


class TestAngleCalcCW(unittest.TestCase):
	def test_angleCalcCW_0(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCW(1, 0), 0)

	def test_angleCalcCW_4thPI(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCW(math.cos(-math.pi / 4), math.sin(-math.pi / 4)), math.pi / 4)

	def test_angleCalcCW_HalfPI(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCW(math.cos(-math.pi / 2), math.sin(-math.pi / 2)), math.pi / 2)

	def test_angleCalcCW_4thPI3(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCW(math.cos(math.pi / 4 * 5), math.sin(math.pi / 4 * 5)), 6), round(math.pi / 4 * 3, 6))

	def test_angleCalcCW_PI(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCW(math.cos(math.pi), math.sin(math.pi)), 6), round(math.pi, 6))

	def test_angleCalcCW_4thPI5(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCW(math.cos(math.pi / 4 * 3), math.sin(math.pi / 4 * 3)), 6), round(math.pi / 4 * 5, 6))

	def test_angleCalcCW_HalfPI3(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCW(math.cos(math.pi / 2), math.sin(math.pi / 2)), math.pi / 2 * 3)

	def test_angleCalcCW_4thPI7(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCW(math.cos(math.pi / 4), math.sin(math.pi / 4)), 6), round(math.pi / 4 * 7, 6))
