import unittest
from Converters import GCode

class TestGCodeInterpreter(unittest.TestCase):
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

	def test_M30(self):
		i = GCode.GCodeInterpreter()
		i.process([ 'M30' ])
		self.assertEqual(i.end, True)

	def test_M2(self):
		i = GCode.GCodeInterpreter()
		i.process([ 'M2' ])
		self.assertEqual(i.end, True)
