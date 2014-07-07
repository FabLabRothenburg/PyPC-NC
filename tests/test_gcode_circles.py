import math
import unittest
from Converters import GCode

class TestCirclesCW(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.target.buffer = []
		self.i.position = [ 9.000, 9.000, 0.000 ]

	def test_basicQuarterCircle(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'R20' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-1570796'
		])

	def test_basicHalfCircle(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-30', 'Y15', 'R20' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-3141592'
		])

	def test_basicQuarterCircle2(self):
		self.i.process([ 'G0', 'X-10', 'Y-5' ])
		self.i.process([ 'G2', 'X-30', 'Y15', 'R20' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V1,X0,Y5000',
			'E', 'E', 'C08', 'W10', 'K21,x0,y20000,p-1570796'
		])

	def test_basicQuarterCircle3(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'R20' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-1570796'
		])

	def test_basicArcWith20Degrees(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X8.79385241572', 'Y21.8404028665', 'R20' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x18794,y6840,p-349044'
		])

	def test_oneMoreStrangeArc(self):
		self.i.process([ 'G0', 'X5', 'Y5' ])
		self.i.process([ 'G2', 'X0', 'Y5', 'R10' ])

		self.assertEqual(self.i.target.buffer, [
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

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-1570796'
		])

	def test_basicQuarterCircleCenterFormatJustI(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'I-20' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p-1570796'
		])


	def test_basicThreeQuarterCircle1(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G2', 'X-10', 'Y-5', 'J-20' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x0,y-20000,p-4712388'
		])

	def test_basicThreeQuarterCircle2(self):
		self.i.process([ 'G0', 'X10', 'Y0' ])
		self.i.process([ 'G2', 'X0', 'Y10', 'I-10' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V1,X20000,Y10000',
			'E', 'E', 'C08', 'W10', 'K21,x-10000,y0,p-4712388'
		])

	def test_basicThreeQuarterCircle3(self):
		self.i.process([ 'G0', 'X0', 'Y-10' ])
		self.i.process([ 'G2', 'X10', 'Y0', 'J10' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X10000,Y0',
			'E', 'E', 'C08', 'W10', 'K21,x0,y10000,p-4712388'
		])

	def test_basicThreeQuarterCircle4(self):
		self.i.process([ 'G0', 'X-10', 'Y0' ])
		self.i.process([ 'G2', 'X0', 'Y-10', 'I10' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V1,X0,Y10000',
			'E', 'E', 'C08', 'W10', 'K21,x10000,y0,p-4712388'
		])


class TestAngleCalcCW(unittest.TestCase):
	def test_angleCalcCW_0(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCW(1, 0), 0)

	def test_angleCalcCW_4thPI(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCW(math.cos(-math.pi / 4), math.sin(-math.pi / 4)), 3), round(math.pi / 4, 3))

	def test_angleCalcCW_HalfPI(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCW(math.cos(-math.pi / 2), math.sin(-math.pi / 2)), math.pi / 2)

	def test_angleCalcCW_4thPI3(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCW(math.cos(math.pi / 4 * 5), math.sin(math.pi / 4 * 5)), 3), round(math.pi / 4 * 3, 3))

	def test_angleCalcCW_PI(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCW(math.cos(math.pi), math.sin(math.pi)), 3), round(math.pi, 3))

	def test_angleCalcCW_4thPI5(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCW(math.cos(math.pi / 4 * 3), math.sin(math.pi / 4 * 3)), 3), round(math.pi / 4 * 5, 3))

	def test_angleCalcCW_HalfPI3(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCW(math.cos(math.pi / 2), math.sin(math.pi / 2)), math.pi / 2 * 3)

	def test_angleCalcCW_4thPI7(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCW(math.cos(math.pi / 4), math.sin(math.pi / 4)), 3), round(math.pi / 4 * 7, 3))

class TestAngleCalcCCW(unittest.TestCase):
	def test_angleCalcCCW_0(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCCW(1, 0), 0)

	def test_angleCalcCCW_4thPI(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCCW(math.cos(math.pi / 4), math.sin(math.pi / 4)), 3), round(math.pi / 4, 3))

	def test_angleCalcCCW_HalfPI(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCCW(math.cos(math.pi / 2), math.sin(math.pi / 2)), math.pi / 2)

	def test_angleCalcCCW_4thPI3(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCCW(math.cos(math.pi / 4 * 3), math.sin(math.pi / 4 * 3)), 3), round(math.pi / 4 * 3, 3))

	def test_angleCalcCCW_PI(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCCW(math.cos(math.pi), math.sin(math.pi)), 3), round(math.pi, 3))

	def test_angleCalcCCW_4thPI5(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCCW(math.cos(math.pi / 4 * 5), math.sin(math.pi / 4 * 5)), 3), round(math.pi / 4 * 5, 3))

	def test_angleCalcCCW_HalfPI3(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(i.angleCalcCCW(math.cos(math.pi / 2 * 3), math.sin(math.pi / 2 * 3)), math.pi / 2 * 3)

	def test_angleCalcCCW_4thPI7(self):
		i = GCode.GCodeInterpreter()
		self.assertEqual(round(i.angleCalcCCW(math.cos(math.pi / 4 * 7), math.sin(math.pi / 4 * 7)), 3), round(math.pi / 4 * 7, 3))


class TestCirclesCCW(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.target.buffer = []
		self.i.position = [ 9.000, 9.000, 0.000 ]

	def test_basicQuarterCircle(self):
		self.i.process([ 'G0', 'X-10', 'Y0' ])
		self.i.process([ 'G3', 'X0', 'Y-10', 'I10' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V1,X0,Y10000',
			'E', 'E', 'C08', 'W10', 'K21,x10000,y0,p1570797'
		])

	def test_basicHalfCircle(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G3', 'X-30', 'Y15', 'R20' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p3141593'
		])

	def test_basicArcWith20Degrees(self):
		self.i.process([ 'G0', 'X10', 'Y15' ])
		self.i.process([ 'G3', 'X8.79385241572', 'Y21.8404028665', 'R20' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V2,X20000,Y25000',
			'E', 'E', 'C08', 'W10', 'K21,x-20000,y0,p349045'
		])

	def test_basicThreeQuarterCircle(self):
		self.i.process([ 'G0', 'X10', 'Y0' ])
		self.i.process([ 'G3', 'X0', 'Y-10', 'I-10' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V1,X20000,Y10000',
			'E', 'E', 'C08', 'W10', 'K21,x-10000,y0,p4712389'
		])

	def test_negativeRadius(self):
		self.i.process([ 'G0', 'X100', 'Y90' ])
		self.i.process([ 'G3', 'X90', 'Y100', 'R-10' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V1,X110000,Y100000',
			'E', 'E', 'C08', 'W10', 'K21,x0,y10000,p4712389'
		])


class TestArcDistanceModes(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.target.buffer = []
		self.i.position = [ 9.000, 9.000, 0.000 ]
		self.i.offsets = [ 30.000, 30.000, 10.000 ]

	def test_incrementalMode(self):
		self.i.process([ 'G91.1' ])
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.i.process([ 'G1', 'X10', 'Y10' ])
		self.i.process([ 'G2', 'X20', 'Y20', 'I10', 'J0' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V1,X30000,Y30000',
			'E', 'E', 'C08', 'W10', 'V21,X40000,Y40000',
			'E', 'K21,x10000,y0,p-1570796',
		])

	def test_absoluteMode(self):
		self.i.process([ 'G90.1' ])
		self.i.process([ 'G0', 'X0', 'Y0' ])
		self.i.process([ 'G1', 'X10', 'Y10' ])
		self.i.process([ 'G2', 'X20', 'Y20', 'I20', 'J10' ])

		self.assertEqual(self.i.target.buffer, [
			'E', 'V1,X30000,Y30000',
			'E', 'E', 'C08', 'W10', 'V21,X40000,Y40000',
			'E', 'K21,x10000,y0,p-1570796',
		])

