import unittest
from Converters import GCode

class TestDrillingCycle(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.buffer = []

	def test_setRetractG98(self):
		self.i.process([ 'G98' ])
		self.assertEqual(self.i.retractToOldZ, True)

	def test_setRetractG99(self):
		self.i.process([ 'G99' ])
		self.assertEqual(self.i.retractToOldZ, False)

	def test_absolutePosition(self):
		self.i.position = [ 11.000, 12.000, 13.000 ]
		self.i.process([ 'G90' ])  # abs distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z1.5', 'R2.8' ])

		self.assertEqual(self.i.buffer, [
			# 1. a rapid move parallel to the XY plane to (X4, Y5)
			'E', 'V1,X14000,Y15000',

			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z12800',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z11500',

			# 4. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z13000'
		])
