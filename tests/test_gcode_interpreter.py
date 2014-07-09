import unittest
from Converters import GCode
from Converters import CNCCon

class TestBlockSplitting(unittest.TestCase):
	def test_splitBlockSelf(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		self.assertEqual(i.splitBlock('M30'), [ [ 'M30' ] ])

	def test_splitBlockGroupParams(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		self.assertEqual(i.splitBlock('G0 X0'), [ [ 'G0', 'X0' ] ])

	def test_splitBlockGroupInsns(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		self.assertEqual(i.splitBlock('M0 M1'), [ [ 'M0' ], [ 'M1' ] ])

	def test_splitBlockM3takesS(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		self.assertEqual(i.splitBlock('M3 S3000'), [ [ 'M3', 'S3000' ] ])

	def test_splitBlockComplex(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		self.assertEqual(i.splitBlock('G17 G20 G90 G64 P0.003 M3 S3000 M7 F1'), [
			[ 'G17' ],
			[ 'G20' ],
			[ 'G90' ],
			[ 'G64', 'P0.003' ],
			[ 'M3', 'S3000' ],
			[ 'M7' ],
			[ 'F1' ] ])

class TestInterpreterBasics(unittest.TestCase):
	def test_G20(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.process([ 'G20' ])
		self.assertEqual(i.stretch, 25.4)

	def test_G21(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.process([ 'G21' ])
		self.assertEqual(i.stretch, 1)

	def test_G90(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.process([ 'G90' ])
		self.assertEqual(i.absDistanceMode, True)

	def test_G91(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.process([ 'G91' ])
		self.assertEqual(i.absDistanceMode, False)

	def test_M30(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.process([ 'M30' ])
		self.assertEqual(i.end, True)

	def test_M2(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.process([ 'M2' ])
		self.assertEqual(i.end, True)

	def test_G17(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.process([ 'G17' ])
		self.assertEqual(i.plane, 'XY')

	def test_G18(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.process([ 'G18' ])
		self.assertEqual(i.plane, 'XZ')

	def test_G19(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.process([ 'G19' ])
		self.assertEqual(i.plane, 'YZ')

	def test_F60(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'F60' ])
		self.assertEqual(i.target.buffer, [ 'E', 'G21,1000', 'G20,1000' ])

	def test_F180(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'F180' ])
		self.assertEqual(i.target.buffer, [ 'E', 'G21,3000', 'G20,3000' ])

class TestParameterizedProgramming(unittest.TestCase):
	def test_readParametersReturnFalseOnNonParam(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		r = i.readParameters('M30')
		self.assertEqual(r, False)

	def test_parameterParsing(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.readParameters('#100=0.002000')
		self.assertEqual(i.parameters[100], 0.002)

	def test_parameterSubstitution(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.parameters[100] = 0.002
		r = i.substituteParameters('G0 Z#100')
		self.assertEqual(r, 'G0 Z0.002000')

	def test_parameterSubstitutionMulti(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.parameters[100] = 10
		i.parameters[101] = 5
		r = i.substituteParameters('G0 X#100 Y#100 Z#101')
		self.assertEqual(r, 'G0 X10 Y10 Z5')
