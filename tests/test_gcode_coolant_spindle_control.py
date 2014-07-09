import unittest
from Converters import GCode
from Converters import CNCCon

class TestInterpreterCoolantControl(unittest.TestCase):
	def test_M7(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M7' ])
		self.assertEqual(i.target.buffer, [ 'E', 'A53' ])

	def test_M7repeat(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M7' ])
		i.process([ 'M7' ])
		i.process([ 'M7' ])
		self.assertEqual(i.target.buffer, [ 'E', 'A53', 'E', 'E' ])

	def test_M8(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M8' ])
		self.assertEqual(i.target.buffer, [ 'E', 'A53' ])

	def test_M8repeat(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M8' ])
		i.process([ 'M8' ])
		i.process([ 'M8' ])
		self.assertEqual(i.target.buffer, [ 'E', 'A53', 'E', 'E' ])

	def test_M9(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.target.coolantEnable = True
		i.process([ 'M9' ])
		self.assertEqual(i.target.buffer, [ 'E', 'A51' ])

	def test_M9repeat(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.target.coolantEnable = True
		i.process([ 'M9' ])
		i.process([ 'M9' ])
		i.process([ 'M9' ])
		self.assertEqual(i.target.buffer, [ 'E', 'A51', 'E', 'E' ])

	def test_M9_initiallyOff(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M9' ])
		self.assertEqual(i.target.buffer, [ 'E' ])

	def test_M8M9_with_CCW_spindle(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M4', 'S3000' ])
		i.process([ 'M8' ])
		i.process([ 'M9' ])

		self.assertEqual(i.target.buffer, [
			'E', 'AD1', 'E', 'W100', 'E', 'D42', 'W100',
			'E', 'AD3',
			'E', 'AD1'
		])

class TestInterpreterSpindleCoolantCombinations(unittest.TestCase):
	def test_spindleControl_with_CCW_spindle(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M4', 'S3000' ])
		i.process([ 'M8' ])
		i.process([ 'M5' ])
		i.process([ 'M4', 'S4000' ])
		i.process([ 'M9' ])

		self.assertEqual(i.target.buffer, [
			'E', 'AD1', 'E', 'W100', 'E', 'D42', 'W100',
			'E', 'AD3',						# M8
			'E', 'AD2', 'E',					# M5
			'E', 'AD3',      'W100', 'E', 'D56', 'W100',		# M4 S4000
			'E', 'AD1'
		])

	def test_spindleControl_with_CW_spindle(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M3', 'S3000' ])
		i.process([ 'M8' ])
		i.process([ 'M5' ])
		i.process([ 'M3', 'S4000' ])
		i.process([ 'M9' ])

		self.assertEqual(i.target.buffer, [
			'E',        'E', 'W100', 'E', 'D42', 'W100',
			'E', 'A53',						# M8
			'E', 'A52', 'E',					# M5
			'E', 'A53',      'W100', 'E', 'D56', 'W100',		# M3 S4000
			'E', 'A51'
		])

	def test_coolantControl_with_spindle_off(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M5' ])
		i.process([ 'M7' ])
		i.process([ 'M9' ])

		self.assertEqual(i.target.buffer, [
			'E', 'A50', 'E',
			'E', 'A52',
			'E', 'A50',
		])

class TestInterpreterSpindleSpeed(unittest.TestCase):
	def test_M3(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M3', 'S3000' ])
		self.assertEqual(i.target.buffer, [ 'E', 'E', 'W100', 'E', 'D42', 'W100' ])

	def test_M3_multi(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M3', 'S0' ])
		i.process([ 'M3', 'S1000' ])
		i.process([ 'M3', 'S2000' ])
		i.process([ 'M3', 'S3000' ])
		i.process([ 'M3', 'S4000' ])
		i.process([ 'M3', 'S5000' ])
		i.process([ 'M3', 'S10000' ])
		i.process([ 'M3', 'S15000' ])
		i.process([ 'M3', 'S20000' ])
		i.process([ 'M3', 'S30000' ])
		i.process([ 'M3', 'S40000' ])

		self.assertEqual(i.target.buffer, [
			'E', 'E', 'W100',
			'E', 'E', 'W100', 'E', 'D14', 'W100',  # S1000
			'E', 'E', 'W100', 'E', 'D28', 'W100',  # S2000
			'E', 'E', 'W100', 'E', 'D42', 'W100',  # S3000
			'E', 'E', 'W100', 'E', 'D56', 'W100',  # S4000
			'E', 'E', 'W100', 'E', 'D71', 'W100',  # S5000; WinPC-NC uses D70
			'E', 'E', 'W100', 'E', 'D141', 'W100', # S10000
			'E', 'E', 'W100', 'E', 'D212', 'W100', # S15000
			'E', 'E', 'W100', 'E', 'D255', 'W100', # S20000
			'E', 'E', 'W100', 'E',                 # S30000
			'E', 'E', 'W100', 'E',                 # S40000
		])

	def test_M4(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M3', 'S8000' ])
		i.process([ 'M4', 'S5000' ])
		i.process([ 'M3', 'S6000' ])
		i.process([ 'M4', 'S7000' ])

		self.assertEqual(i.target.buffer, [
			'E',        'E', 'W100', 'E', 'D113', 'W100',
			'E', 'AD1', 'E', 'W100', 'E', 'D71',  'W100',   # WinPC-NC uses D70
			'E', 'A51', 'E', 'W100', 'E', 'D85',  'W100',
			'E', 'AD1', 'E', 'W100', 'E', 'D99',  'W100',
		])

	def test_M5ccw(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M3', 'S8000' ])
		i.process([ 'M4', 'S5000' ])
		i.process([ 'M5' ])
		i.process([ 'M4', 'S7000' ])

		self.assertEqual(i.target.buffer, [
			'E',        'E', 'W100', 'E', 'D113', 'W100',
			'E', 'AD1', 'E', 'W100', 'E', 'D71',  'W100',   # WinPC-NC uses D70
			'E', 'AD0', 'E',
			'E', 'AD1',      'W100', 'E', 'D99',  'W100',
		])


	def test_M5cw(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.process([ 'M3', 'S8000' ])
		i.process([ 'M5' ])
		i.process([ 'M3', 'S7000' ])

		self.assertEqual(i.target.buffer, [
			'E',        'E', 'W100', 'E', 'D113', 'W100',
			'E', 'A50', 'E',
			'E', 'A51',      'W100', 'E', 'D99',  'W100',
		])


	def test_M3_W100_behaviour_G0(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.position = [ 0, 0, 0 ]
		i.offsets = [ 30, 30, 10 ]
		i.process([ 'G0', 'X0', 'Y0' ])
		i.process([ 'M3', 'S5000' ])
		i.process([ 'G0', 'X1' ])
		i.process([ 'G1', 'X2' ])
		i.process([ 'G0', 'X3' ])

		self.assertEqual(i.target.buffer, [
			'E', 'V1,X30000,Y30000',
			'E', 'E', 'W100', 'E', 'D71', 'W100',  # WinPC-NC uses D70
			'E', 'V1,X31000',
			'E', 'E', 'C08', 'W10', 'V21,X32000',
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V1,X33000',
		])

	def test_M3_W100_behaviour_G1G0G1G0(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.position = [ 0, 0, 0 ]
		i.offsets = [ 30, 30, 10 ]
		i.process([ 'G1', 'X0', 'Y0' ])
		i.process([ 'M3', 'S5000' ])
		i.process([ 'G0', 'X1' ])
		i.process([ 'G1', 'X2' ])
		i.process([ 'G0', 'X3' ])

		self.assertEqual(i.target.buffer, [
			'E', 'C08', 'W10', 'V21,X30000,Y30000',
			'E', 'E', 'W100', 'E', 'D71', 'W100',  # WinPC-NC uses D70
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V1,X31000',
			'E', 'E', 'C08', 'W10', 'V21,X32000',
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V1,X33000',
		])

	def test_M3_W100_behaviour_G0G1G1G0G1(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.position = [ 0, 0, 0 ]
		i.offsets = [ 30, 30, 10 ]
		i.process([ 'G0', 'X0', 'Y0' ])
		i.process([ 'M3', 'S5000' ])
		i.process([ 'G1', 'X1' ])
		i.process([ 'G1', 'Y1' ])
		i.process([ 'G0', 'X2' ])
		i.process([ 'G1', 'X3' ])

		self.assertEqual(i.target.buffer, [
			'E', 'V1,X30000,Y30000',
			'E', 'E', 'W100', 'E', 'D71', 'W100',  # WinPC-NC uses D70
			'E', 'E', 'C08', 'W10', 'V21,X31000',
			'E', 'V21,Y31000',
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V1,X32000',
			'E', 'E', 'C08', 'W10', 'V21,X33000',
		])


	def test_M3_W100_behaviour_G0G1M3G1G0G1(self):
		i = GCode.GCodeInterpreter(CNCCon.CNCConWriter())
		i.target.buffer = []
		i.position = [ 0, 0, 0 ]
		i.offsets = [ 30, 30, 10 ]
		i.process([ 'G0', 'X0', 'Y0' ])
		i.process([ 'M3', 'S5000' ])
		i.process([ 'G1', 'X1' ])
		i.process([ 'M3', 'S7000' ])
		i.process([ 'G1', 'Y1' ])
		i.process([ 'G0', 'X2' ])
		i.process([ 'G1', 'X3' ])

		self.assertEqual(i.target.buffer, [
			'E', 'V1,X30000,Y30000',
			'E', 'E', 'W100', 'E', 'D71', 'W100',  # WinPC-NC uses D70
			'E', 'E', 'C08', 'W10', 'V21,X31000',
			'E', 'E', 'W100', 'E', 'D99', 'W100',
			'E', 'V21,Y31000',
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V1,X32000',
			'E', 'E', 'C08', 'W10', 'V21,X33000',
		])

